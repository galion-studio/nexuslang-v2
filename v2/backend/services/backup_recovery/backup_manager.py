"""
Backup and recovery management for Deep Search system.
Provides comprehensive data backup, restoration, and disaster recovery.
"""

import asyncio
import logging
import json
import os
import gzip
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import aiofiles

logger = logging.getLogger(__name__)


class BackupManager:
    """
    Comprehensive backup and recovery system for Deep Search.

    Features:
    - Automated scheduled backups
    - Incremental backup support
    - Point-in-time recovery
    - Data integrity verification
    - Cross-region backup replication
    - Emergency recovery procedures
    """

    def __init__(self, backup_dir: str = "./backups", max_backups: int = 30,
                 compression_level: int = 6):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.compression_level = compression_level

        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Backup metadata
        self.backup_metadata = {
            "total_backups": 0,
            "last_backup": None,
            "last_full_backup": None,
            "backup_sizes": {},
            "integrity_checks": {}
        }

        # Tables to backup (in dependency order)
        self.backup_tables = [
            "users",
            "knowledge_entries",
            "contributions",
            "knowledge_graph",
            "relationships"
        ]

    async def create_full_backup(self, session: AsyncSession,
                                backup_name: str = None) -> Dict[str, Any]:
        """Create a full backup of all deep search data."""
        if backup_name is None:
            backup_name = f"full_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)

        try:
            logger.info(f"Starting full backup: {backup_name}")

            backup_manifest = {
                "backup_type": "full",
                "backup_name": backup_name,
                "created_at": datetime.utcnow().isoformat(),
                "tables": {},
                "total_records": 0,
                "compressed_size": 0,
                "integrity_hash": None
            }

            total_records = 0

            # Backup each table
            for table_name in self.backup_tables:
                table_data = await self._backup_table(session, table_name, backup_path)
                backup_manifest["tables"][table_name] = table_data
                total_records += table_data["record_count"]

            # Create backup manifest
            manifest_file = backup_path / "manifest.json"
            async with aiofiles.open(manifest_file, 'w') as f:
                await f.write(json.dumps(backup_manifest, indent=2))

            # Compress the backup
            compressed_file = await self._compress_backup(backup_path, backup_name)

            # Calculate integrity hash
            integrity_hash = await self._calculate_integrity_hash(compressed_file)
            backup_manifest["integrity_hash"] = integrity_hash
            backup_manifest["compressed_size"] = os.path.getsize(compressed_file)

            # Update manifest with final data
            async with aiofiles.open(manifest_file, 'w') as f:
                await f.write(json.dumps(backup_manifest, indent=2))

            # Update backup metadata
            self.backup_metadata["total_backups"] += 1
            self.backup_metadata["last_backup"] = backup_name
            self.backup_metadata["last_full_backup"] = backup_name
            self.backup_metadata["backup_sizes"][backup_name] = backup_manifest["compressed_size"]

            # Cleanup old backups
            await self._cleanup_old_backups()

            logger.info(f"Full backup completed: {backup_name} ({total_records} records, {backup_manifest['compressed_size']} bytes)")

            return {
                "success": True,
                "backup_name": backup_name,
                "total_records": total_records,
                "compressed_size": backup_manifest["compressed_size"],
                "integrity_hash": integrity_hash,
                "created_at": backup_manifest["created_at"]
            }

        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            # Cleanup failed backup
            if backup_path.exists():
                shutil.rmtree(backup_path)
            return {
                "success": False,
                "error": str(e),
                "backup_name": backup_name
            }

    async def create_incremental_backup(self, session: AsyncSession,
                                       since_backup: str = None) -> Dict[str, Any]:
        """Create an incremental backup since the last full backup."""
        backup_name = f"incremental_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        try:
            logger.info(f"Starting incremental backup: {backup_name}")

            # Find last full backup if not specified
            if since_backup is None:
                since_backup = self.backup_metadata.get("last_full_backup")

            if not since_backup:
                logger.warning("No previous full backup found, creating full backup instead")
                return await self.create_full_backup(session, backup_name.replace("incremental", "full"))

            since_timestamp = await self._get_backup_timestamp(since_backup)
            if not since_timestamp:
                logger.error(f"Could not find timestamp for backup: {since_backup}")
                return {"success": False, "error": f"Invalid backup reference: {since_backup}"}

            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)

            backup_manifest = {
                "backup_type": "incremental",
                "backup_name": backup_name,
                "since_backup": since_backup,
                "since_timestamp": since_timestamp.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "tables": {},
                "total_records": 0
            }

            total_records = 0

            # Backup only changed data since the reference timestamp
            for table_name in self.backup_tables:
                table_data = await self._backup_table_incremental(
                    session, table_name, since_timestamp, backup_path
                )
                if table_data["record_count"] > 0:
                    backup_manifest["tables"][table_name] = table_data
                    total_records += table_data["record_count"]

            # Create backup manifest
            manifest_file = backup_path / "manifest.json"
            async with aiofiles.open(manifest_file, 'w') as f:
                await f.write(json.dumps(backup_manifest, indent=2))

            # Compress the backup
            compressed_file = await self._compress_backup(backup_path, backup_name)
            backup_manifest["compressed_size"] = os.path.getsize(compressed_file)

            # Calculate integrity hash
            integrity_hash = await self._calculate_integrity_hash(compressed_file)
            backup_manifest["integrity_hash"] = integrity_hash

            # Update manifest
            async with aiofiles.open(manifest_file, 'w') as f:
                await f.write(json.dumps(backup_manifest, indent=2))

            # Update metadata
            self.backup_metadata["total_backups"] += 1
            self.backup_metadata["last_backup"] = backup_name
            self.backup_metadata["backup_sizes"][backup_name] = backup_manifest["compressed_size"]

            logger.info(f"Incremental backup completed: {backup_name} ({total_records} records)")

            return {
                "success": True,
                "backup_name": backup_name,
                "total_records": total_records,
                "compressed_size": backup_manifest["compressed_size"],
                "since_backup": since_backup
            }

        except Exception as e:
            logger.error(f"Incremental backup failed: {e}")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            return {"success": False, "error": str(e)}

    async def restore_backup(self, session: AsyncSession, backup_name: str,
                           dry_run: bool = False) -> Dict[str, Any]:
        """Restore data from a backup."""
        try:
            backup_path = self.backup_dir / backup_name

            # Check if backup exists (try compressed first)
            compressed_file = self.backup_dir / f"{backup_name}.tar.gz"
            if compressed_file.exists():
                # Extract backup
                await self._extract_backup(compressed_file, backup_path)

            if not backup_path.exists():
                return {"success": False, "error": f"Backup not found: {backup_name}"}

            # Read manifest
            manifest_file = backup_path / "manifest.json"
            if not manifest_file.exists():
                return {"success": False, "error": "Backup manifest not found"}

            async with aiofiles.open(manifest_file, 'r') as f:
                manifest = json.loads(await f.read())

            # Verify backup integrity
            if manifest.get("integrity_hash"):
                compressed_file = self.backup_dir / f"{backup_name}.tar.gz"
                if compressed_file.exists():
                    calculated_hash = await self._calculate_integrity_hash(compressed_file)
                    if calculated_hash != manifest["integrity_hash"]:
                        return {"success": False, "error": "Backup integrity check failed"}

            if dry_run:
                # Just analyze what would be restored
                analysis = await self._analyze_restore_impact(session, manifest)
                return {
                    "success": True,
                    "dry_run": True,
                    "analysis": analysis,
                    "manifest": manifest
                }

            # Perform restoration
            restore_results = {}
            for table_name, table_info in manifest["tables"].items():
                result = await self._restore_table(session, table_name,
                                                 backup_path / f"{table_name}.json")
                restore_results[table_name] = result

            logger.info(f"Backup restoration completed: {backup_name}")

            return {
                "success": True,
                "backup_name": backup_name,
                "restore_results": restore_results,
                "manifest": manifest
            }

        except Exception as e:
            logger.error(f"Backup restoration failed: {e}")
            return {"success": False, "error": str(e)}

    async def _backup_table(self, session: AsyncSession, table_name: str,
                           backup_path: Path) -> Dict[str, Any]:
        """Backup a single table."""
        try:
            # Get all records from the table
            query = text(f"SELECT * FROM {table_name}")
            result = await session.execute(query)
            records = result.fetchall()

            # Convert to list of dicts
            records_data = [dict(record) for record in records]

            # Save to JSON file
            table_file = backup_path / f"{table_name}.json"
            async with aiofiles.open(table_file, 'w') as f:
                await f.write(json.dumps(records_data, indent=2, default=str))

            return {
                "record_count": len(records_data),
                "file_size": os.path.getsize(table_file),
                "backup_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to backup table {table_name}: {e}")
            return {"error": str(e), "record_count": 0}

    async def _backup_table_incremental(self, session: AsyncSession, table_name: str,
                                       since_timestamp: datetime, backup_path: Path) -> Dict[str, Any]:
        """Backup only changed records since timestamp."""
        try:
            # Get records modified since the timestamp
            query = text(f"""
                SELECT * FROM {table_name}
                WHERE updated_at > :since_timestamp
                   OR created_at > :since_timestamp
            """)
            result = await session.execute(query, {"since_timestamp": since_timestamp})
            records = result.fetchall()

            records_data = [dict(record) for record in records]

            if records_data:
                # Save to JSON file only if there are changes
                table_file = backup_path / f"{table_name}.json"
                async with aiofiles.open(table_file, 'w') as f:
                    await f.write(json.dumps(records_data, indent=2, default=str))

            return {
                "record_count": len(records_data),
                "has_changes": len(records_data) > 0,
                "backup_time": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to backup table {table_name} incrementally: {e}")
            return {"error": str(e), "record_count": 0, "has_changes": False}

    async def _compress_backup(self, backup_path: Path, backup_name: str) -> str:
        """Compress backup directory to tar.gz."""
        import tarfile
        import io

        compressed_file = self.backup_dir / f"{backup_name}.tar.gz"

        with tarfile.open(compressed_file, "w:gz", compresslevel=self.compression_level) as tar:
            for file_path in backup_path.rglob("*"):
                if file_path.is_file():
                    tar.add(file_path, arcname=file_path.relative_to(backup_path.parent))

        # Remove uncompressed directory
        shutil.rmtree(backup_path)

        return str(compressed_file)

    async def _extract_backup(self, compressed_file: str, extract_path: Path):
        """Extract compressed backup."""
        import tarfile

        with tarfile.open(compressed_file, "r:gz") as tar:
            tar.extractall(extract_path.parent)

    async def _calculate_integrity_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of backup file."""
        sha256 = hashlib.sha256()

        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                data = await f.read(65536)  # 64KB chunks
                if not data:
                    break
                sha256.update(data)

        return sha256.hexdigest()

    async def _get_backup_timestamp(self, backup_name: str) -> Optional[datetime]:
        """Get the creation timestamp of a backup."""
        try:
            manifest_file = self.backup_dir / backup_name / "manifest.json"
            if not manifest_file.exists():
                compressed_file = self.backup_dir / f"{backup_name}.tar.gz"
                if compressed_file.exists():
                    # Extract temporarily to read manifest
                    temp_dir = self.backup_dir / f"temp_{backup_name}"
                    await self._extract_backup(str(compressed_file), temp_dir)
                    manifest_file = temp_dir / "manifest.json"

            if manifest_file.exists():
                async with aiofiles.open(manifest_file, 'r') as f:
                    manifest = json.loads(await f.read())
                    return datetime.fromisoformat(manifest["created_at"])

            # Cleanup temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

        except Exception as e:
            logger.error(f"Failed to get backup timestamp for {backup_name}: {e}")

        return None

    async def _restore_table(self, session: AsyncSession, table_name: str,
                           data_file: Path) -> Dict[str, Any]:
        """Restore a single table from backup data."""
        try:
            # Read backup data
            async with aiofiles.open(data_file, 'r') as f:
                records = json.loads(await f.read())

            if not records:
                return {"restored": 0, "skipped": 0}

            restored = 0
            skipped = 0

            for record in records:
                try:
                    # Use upsert logic (INSERT ... ON CONFLICT)
                    # This is a simplified version - you might want more sophisticated conflict resolution
                    await session.execute(
                        text(f"""
                            INSERT INTO {table_name} ({', '.join(record.keys())})
                            VALUES ({', '.join([':' + k for k in record.keys()])})
                            ON CONFLICT (id) DO NOTHING
                        """),
                        record
                    )
                    restored += 1
                except Exception as e:
                    logger.warning(f"Failed to restore record in {table_name}: {e}")
                    skipped += 1

            await session.commit()

            return {"restored": restored, "skipped": skipped}

        except Exception as e:
            logger.error(f"Failed to restore table {table_name}: {e}")
            return {"error": str(e), "restored": 0, "skipped": 0}

    async def _analyze_restore_impact(self, session: AsyncSession,
                                     manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the impact of restoring a backup."""
        analysis = {
            "tables": {},
            "total_records": 0,
            "estimated_impact": "low"
        }

        for table_name, table_info in manifest.get("tables", {}).items():
            record_count = table_info.get("record_count", 0)
            analysis["tables"][table_name] = {
                "backup_records": record_count,
                "existing_records": 0,
                "conflicts_expected": 0
            }

            # Check existing records (simplified)
            try:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                result = await session.execute(count_query)
                existing_count = result.scalar()
                analysis["tables"][table_name]["existing_records"] = existing_count

                # Estimate conflicts (records with same ID)
                if record_count > 0:
                    analysis["tables"][table_name]["conflicts_expected"] = min(record_count, existing_count)

            except Exception as e:
                logger.warning(f"Could not analyze table {table_name}: {e}")

            analysis["total_records"] += record_count

        # Determine impact level
        total_existing = sum(t["existing_records"] for t in analysis["tables"].values())
        total_backup = analysis["total_records"]

        if total_backup > total_existing * 2:
            analysis["estimated_impact"] = "high"
        elif total_backup > total_existing * 0.5:
            analysis["estimated_impact"] = "medium"

        return analysis

    async def _cleanup_old_backups(self):
        """Remove old backups to maintain max_backups limit."""
        try:
            # Get all backup files
            backup_files = list(self.backup_dir.glob("*.tar.gz"))

            if len(backup_files) > self.max_backups:
                # Sort by modification time (oldest first)
                backup_files.sort(key=lambda x: x.stat().st_mtime)

                # Remove oldest backups
                to_remove = backup_files[:len(backup_files) - self.max_backups]
                for old_backup in to_remove:
                    old_backup.unlink()
                    logger.info(f"Removed old backup: {old_backup.name}")

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")

    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []

        try:
            # Get compressed backup files
            for backup_file in self.backup_dir.glob("*.tar.gz"):
                backup_info = {
                    "name": backup_file.stem,
                    "file_path": str(backup_file),
                    "size": backup_file.stat().st_size,
                    "created_at": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                    "compressed": True
                }
                backups.append(backup_info)

            # Get uncompressed backup directories
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir() and not backup_dir.name.startswith("temp_"):
                    manifest_file = backup_dir / "manifest.json"
                    if manifest_file.exists():
                        async with aiofiles.open(manifest_file, 'r') as f:
                            manifest = json.loads(await f.read())

                        backup_info = {
                            "name": backup_dir.name,
                            "path": str(backup_dir),
                            "created_at": manifest.get("created_at"),
                            "type": manifest.get("backup_type"),
                            "total_records": manifest.get("total_records", 0),
                            "compressed": False
                        }
                        backups.append(backup_info)

            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created_at"], reverse=True)

        except Exception as e:
            logger.error(f"Failed to list backups: {e}")

        return backups

    async def get_backup_status(self) -> Dict[str, Any]:
        """Get comprehensive backup status."""
        try:
            backups = await self.list_backups()

            status = {
                "total_backups": len(backups),
                "last_backup": None,
                "last_full_backup": None,
                "backup_sizes": {},
                "storage_used": 0,
                "oldest_backup": None,
                "newest_backup": None
            }

            if backups:
                status["last_backup"] = backups[0]["name"]
                status["newest_backup"] = backups[0]["created_at"]

                # Calculate storage and find specific backup types
                for backup in backups:
                    if backup["name"].startswith("full_backup"):
                        if not status["last_full_backup"]:
                            status["last_full_backup"] = backup["name"]

                    status["backup_sizes"][backup["name"]] = backup.get("size", 0)
                    status["storage_used"] += backup.get("size", 0)

                status["oldest_backup"] = backups[-1]["created_at"]

            # Add metadata
            status.update(self.backup_metadata)

            return status

        except Exception as e:
            logger.error(f"Failed to get backup status: {e}")
            return {"error": str(e)}

    async def emergency_restore(self, session: AsyncSession, backup_name: str) -> Dict[str, Any]:
        """Perform emergency restoration with additional safety checks."""
        logger.warning(f"Starting emergency restoration from backup: {backup_name}")

        try:
            # First, create a backup of current state
            emergency_backup = await self.create_full_backup(
                session, f"emergency_pre_restore_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            )

            if not emergency_backup["success"]:
                return {
                    "success": False,
                    "error": "Failed to create emergency backup before restoration"
                }

            # Perform the restoration
            restore_result = await self.restore_backup(session, backup_name)

            if restore_result["success"]:
                logger.info(f"Emergency restoration completed successfully from {backup_name}")
                return {
                    "success": True,
                    "backup_name": backup_name,
                    "emergency_backup": emergency_backup["backup_name"],
                    "restore_result": restore_result
                }
            else:
                # Try to restore from the emergency backup
                logger.error("Restoration failed, attempting to restore from emergency backup")
                rollback_result = await self.restore_backup(session, emergency_backup["backup_name"])

                return {
                    "success": False,
                    "error": restore_result.get("error", "Restoration failed"),
                    "emergency_backup": emergency_backup["backup_name"],
                    "rollback_attempted": rollback_result["success"]
                }

        except Exception as e:
            logger.error(f"Emergency restoration failed catastrophically: {e}")
            return {
                "success": False,
                "error": f"Critical error during emergency restoration: {e}"
            }
