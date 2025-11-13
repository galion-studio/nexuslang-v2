"""
Comprehensive backup and disaster recovery system for Galion AI
Automated backups, verification, encryption, and recovery procedures
"""

import asyncio
import os
import shutil
import gzip
import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import threading
import time
import tempfile
import subprocess

# Optional backup dependencies
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    boto3 = None

try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    storage = None

try:
    import paramiko
    SFTP_AVAILABLE = True
except ImportError:
    SFTP_AVAILABLE = False
    paramiko = None


logger = logging.getLogger(__name__)


class BackupConfig:
    """Backup configuration"""

    def __init__(self):
        self.enabled = True
        self.backup_directory = "backups"
        self.retention_days = 30
        self.compression_level = 6  # gzip compression level
        self.encryption_enabled = True
        self.encryption_key = os.getenv("BACKUP_ENCRYPTION_KEY")

        # Schedule
        self.database_backup_interval_hours = 6
        self.file_backup_interval_hours = 24
        self.full_backup_interval_days = 7

        # Storage backends
        self.local_storage_enabled = True
        self.aws_s3_enabled = bool(os.getenv("AWS_BACKUP_BUCKET"))
        self.gcp_storage_enabled = bool(os.getenv("GCP_BACKUP_BUCKET"))
        self.sftp_enabled = bool(os.getenv("SFTP_BACKUP_HOST"))

        # AWS S3
        self.aws_bucket = os.getenv("AWS_BACKUP_BUCKET")
        self.aws_region = os.getenv("AWS_REGION", "us-west-2")

        # GCP
        self.gcp_bucket = os.getenv("GCP_BACKUP_BUCKET")
        self.gcp_credentials_path = os.getenv("GCP_CREDENTIALS_PATH")

        # SFTP
        self.sftp_host = os.getenv("SFTP_BACKUP_HOST")
        self.sftp_port = int(os.getenv("SFTP_BACKUP_PORT", "22"))
        self.sftp_username = os.getenv("SFTP_BACKUP_USERNAME")
        self.sftp_password = os.getenv("SFTP_BACKUP_PASSWORD")
        self.sftp_remote_path = os.getenv("SFTP_BACKUP_PATH", "/backups")

        # Monitoring
        self.monitoring_enabled = True
        self.alert_on_failure = True


class BackupEncryption:
    """Backup encryption utilities"""

    @staticmethod
    def generate_key() -> str:
        """Generate a random encryption key"""
        return os.urandom(32).hex()

    @staticmethod
    def encrypt_data(data: bytes, key: str) -> bytes:
        """Encrypt data using AES"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64

            # Derive key using PBKDF2
            salt = b'galion_backup_salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))

            fernet = Fernet(derived_key)
            return fernet.encrypt(data)
        except ImportError:
            logger.warning("Cryptography library not available, skipping encryption")
            return data

    @staticmethod
    def decrypt_data(encrypted_data: bytes, key: str) -> bytes:
        """Decrypt data using AES"""
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64

            # Derive key using PBKDF2
            salt = b'galion_backup_salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(key.encode()))

            fernet = Fernet(derived_key)
            return fernet.decrypt(encrypted_data)
        except ImportError:
            logger.warning("Cryptography library not available, skipping decryption")
            return encrypted_data


class DatabaseBackup:
    """Database backup utilities"""

    def __init__(self, config: BackupConfig):
        self.config = config

    async def create_backup(self, backup_type: str = "full") -> Optional[str]:
        """Create database backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"db_backup_{backup_type}_{timestamp}"

            # Use pg_dump for PostgreSQL
            db_url = os.getenv("DATABASE_URL", "")
            if "postgresql" in db_url:
                return await self._create_postgres_backup(backup_name)
            else:
                logger.error("Unsupported database type")
                return None

        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return None

    async def _create_postgres_backup(self, backup_name: str) -> Optional[str]:
        """Create PostgreSQL backup using pg_dump"""
        try:
            # Parse database URL
            db_url = os.getenv("DATABASE_URL", "")
            # Extract connection details (simplified)
            host = "localhost"
            port = "5432"
            database = "galion_db"
            username = "galion"
            password = "password"

            backup_file = f"{backup_name}.sql.gz"
            backup_path = Path(self.config.backup_directory) / backup_file

            # Create backup directory
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Run pg_dump
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--port={port}",
                f"--username={username}",
                f"--dbname={database}",
                "--no-password",
                "--format=custom",
                "--compress=6",
                f"--file={backup_path}"
            ]

            # Set password environment
            env = os.environ.copy()
            env["PGPASSWORD"] = password

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                # Encrypt if enabled
                if self.config.encryption_enabled and self.config.encryption_key:
                    await self._encrypt_file(backup_path)

                logger.info(f"Database backup created: {backup_path}")
                return str(backup_path)
            else:
                logger.error(f"pg_dump failed: {stderr.decode()}")
                return None

        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            return None

    async def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            # Decrypt if needed
            if self.config.encryption_enabled and self.config.encryption_key:
                await self._decrypt_file(Path(backup_path))

            # Use pg_restore for PostgreSQL
            db_url = os.getenv("DATABASE_URL", "")
            host = "localhost"
            port = "5432"
            database = "galion_db"
            username = "galion"
            password = "password"

            cmd = [
                "pg_restore",
                f"--host={host}",
                f"--port={port}",
                f"--username={username}",
                f"--dbname={database}",
                "--no-password",
                "--clean",
                "--if-exists",
                "--create",
                backup_path
            ]

            env = os.environ.copy()
            env["PGPASSWORD"] = password

            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            success = process.returncode == 0
            if success:
                logger.info(f"Database restored from: {backup_path}")
            else:
                logger.error(f"Database restore failed: {stderr.decode()}")

            return success

        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False

    async def _encrypt_file(self, file_path: Path):
        """Encrypt backup file"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            encrypted_data = BackupEncryption.encrypt_data(data, self.config.encryption_key)

            with open(file_path, 'wb') as f:
                f.write(encrypted_data)

            logger.info(f"Backup file encrypted: {file_path}")

        except Exception as e:
            logger.error(f"File encryption failed: {e}")

    async def _decrypt_file(self, file_path: Path):
        """Decrypt backup file"""
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            data = BackupEncryption.decrypt_data(encrypted_data, self.config.encryption_key)

            with open(file_path, 'wb') as f:
                f.write(data)

            logger.info(f"Backup file decrypted: {file_path}")

        except Exception as e:
            logger.error(f"File decryption failed: {e}")


class FileBackup:
    """File system backup utilities"""

    def __init__(self, config: BackupConfig):
        self.config = config
        self.backup_paths = [
            "uploads",
            "logs",
            "config",
            "static"
        ]

    async def create_backup(self, backup_type: str = "incremental") -> Optional[str]:
        """Create file system backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"files_backup_{backup_type}_{timestamp}.tar.gz"

            backup_path = Path(self.config.backup_directory) / backup_name
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Create temporary directory for backup
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_backup = Path(temp_dir) / "files_backup.tar.gz"

                # Create tar.gz archive
                import tarfile

                with tarfile.open(temp_backup, "w:gz", compresslevel=self.config.compression_level) as tar:
                    for path in self.backup_paths:
                        if os.path.exists(path):
                            tar.add(path, arcname=os.path.basename(path))

                # Move to final location
                shutil.move(str(temp_backup), str(backup_path))

                # Encrypt if enabled
                if self.config.encryption_enabled and self.config.encryption_key:
                    await self._encrypt_file(backup_path)

                logger.info(f"File backup created: {backup_path}")
                return str(backup_path)

        except Exception as e:
            logger.error(f"File backup failed: {e}")
            return None

    async def restore_backup(self, backup_path: str, restore_path: str = ".") -> bool:
        """Restore files from backup"""
        try:
            backup_path = Path(backup_path)

            # Decrypt if needed
            if self.config.encryption_enabled and self.config.encryption_key:
                await self._decrypt_file(backup_path)

            # Extract archive
            import tarfile

            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(path=restore_path)

            logger.info(f"Files restored to: {restore_path}")
            return True

        except Exception as e:
            logger.error(f"File restore failed: {e}")
            return False

    async def _encrypt_file(self, file_path: Path):
        """Encrypt backup file"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            encrypted_data = BackupEncryption.encrypt_data(data, self.config.encryption_key)

            with open(file_path, 'wb') as f:
                f.write(encrypted_data)

        except Exception as e:
            logger.error(f"File encryption failed: {e}")

    async def _decrypt_file(self, file_path: Path):
        """Decrypt backup file"""
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()

            data = BackupEncryption.decrypt_data(encrypted_data, self.config.encryption_key)

            with open(file_path, 'wb') as f:
                f.write(data)

        except Exception as e:
            logger.error(f"File decryption failed: {e}")


class BackupStorage:
    """Backup storage to multiple backends"""

    def __init__(self, config: BackupConfig):
        self.config = config

    async def store_backup(self, local_path: str, remote_name: str) -> bool:
        """Store backup to all configured backends"""
        success = True

        if self.config.local_storage_enabled:
            # Local storage is already done
            pass

        if self.config.aws_s3_enabled and AWS_AVAILABLE:
            if not await self._store_aws_s3(local_path, remote_name):
                success = False

        if self.config.gcp_storage_enabled and GCP_AVAILABLE:
            if not await self._store_gcp(local_path, remote_name):
                success = False

        if self.config.sftp_enabled and SFTP_AVAILABLE:
            if not await self._store_sftp(local_path, remote_name):
                success = False

        return success

    async def retrieve_backup(self, remote_name: str, local_path: str) -> bool:
        """Retrieve backup from primary backend"""
        # Try backends in order of preference
        if self.config.aws_s3_enabled and AWS_AVAILABLE:
            return await self._retrieve_aws_s3(remote_name, local_path)
        elif self.config.gcp_storage_enabled and GCP_AVAILABLE:
            return await self._retrieve_gcp(remote_name, local_path)
        elif self.config.sftp_enabled and SFTP_AVAILABLE:
            return await self._retrieve_sftp(remote_name, local_path)

        # Fallback to local
        return False

    async def _store_aws_s3(self, local_path: str, remote_name: str) -> bool:
        """Store backup in AWS S3"""
        try:
            s3_client = boto3.client('s3', region_name=self.config.aws_region)

            with open(local_path, 'rb') as f:
                s3_client.upload_fileobj(f, self.config.aws_bucket, remote_name)

            logger.info(f"Backup stored in S3: {remote_name}")
            return True

        except Exception as e:
            logger.error(f"S3 storage failed: {e}")
            return False

    async def _retrieve_aws_s3(self, remote_name: str, local_path: str) -> bool:
        """Retrieve backup from AWS S3"""
        try:
            s3_client = boto3.client('s3', region_name=self.config.aws_region)

            with open(local_path, 'wb') as f:
                s3_client.download_fileobj(self.config.aws_bucket, remote_name, f)

            logger.info(f"Backup retrieved from S3: {remote_name}")
            return True

        except Exception as e:
            logger.error(f"S3 retrieval failed: {e}")
            return False

    async def _store_gcp(self, local_path: str, remote_name: str) -> bool:
        """Store backup in Google Cloud Storage"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.config.gcp_credentials_path
            )
            client = storage.Client(credentials=credentials)
            bucket = client.bucket(self.config.gcp_bucket)
            blob = bucket.blob(remote_name)

            blob.upload_from_filename(local_path)
            logger.info(f"Backup stored in GCP: {remote_name}")
            return True

        except Exception as e:
            logger.error(f"GCP storage failed: {e}")
            return False

    async def _retrieve_gcp(self, remote_name: str, local_path: str) -> bool:
        """Retrieve backup from Google Cloud Storage"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.config.gcp_credentials_path
            )
            client = storage.Client(credentials=credentials)
            bucket = client.bucket(self.config.gcp_bucket)
            blob = bucket.blob(remote_name)

            blob.download_to_filename(local_path)
            logger.info(f"Backup retrieved from GCP: {remote_name}")
            return True

        except Exception as e:
            logger.error(f"GCP retrieval failed: {e}")
            return False

    async def _store_sftp(self, local_path: str, remote_name: str) -> bool:
        """Store backup via SFTP"""
        try:
            transport = paramiko.Transport((self.config.sftp_host, self.config.sftp_port))
            transport.connect(
                username=self.config.sftp_username,
                password=self.config.sftp_password
            )

            sftp = paramiko.SFTPClient.from_transport(transport)

            # Ensure remote directory exists
            try:
                sftp.mkdir(self.config.sftp_remote_path)
            except:
                pass  # Directory might already exist

            remote_path = f"{self.config.sftp_remote_path}/{remote_name}"
            sftp.put(local_path, remote_path)

            sftp.close()
            transport.close()

            logger.info(f"Backup stored via SFTP: {remote_name}")
            return True

        except Exception as e:
            logger.error(f"SFTP storage failed: {e}")
            return False

    async def _retrieve_sftp(self, remote_name: str, local_path: str) -> bool:
        """Retrieve backup via SFTP"""
        try:
            transport = paramiko.Transport((self.config.sftp_host, self.config.sftp_port))
            transport.connect(
                username=self.config.sftp_username,
                password=self.config.sftp_password
            )

            sftp = paramiko.SFTPClient.from_transport(transport)

            remote_path = f"{self.config.sftp_remote_path}/{remote_name}"
            sftp.get(remote_path, local_path)

            sftp.close()
            transport.close()

            logger.info(f"Backup retrieved via SFTP: {remote_name}")
            return True

        except Exception as e:
            logger.error(f"SFTP retrieval failed: {e}")
            return False


class BackupManager:
    """Main backup system orchestrator"""

    def __init__(self, config: BackupConfig = None):
        self.config = config or BackupConfig()
        self.database_backup = DatabaseBackup(self.config)
        self.file_backup = FileBackup(self.config)
        self.storage = BackupStorage(self.config)

        # Backup metadata
        self.backup_metadata = {}
        self.backup_schedule = {}

        # Setup backup directory
        Path(self.config.backup_directory).mkdir(parents=True, exist_ok=True)

        # Start automated backup scheduler
        if self.config.enabled:
            self._start_scheduler()

    def _start_scheduler(self):
        """Start automated backup scheduler"""
        def scheduler():
            while True:
                try:
                    asyncio.run(self._run_scheduled_backups())
                    time.sleep(3600)  # Check every hour
                except Exception as e:
                    logger.error(f"Backup scheduler error: {e}")
                    time.sleep(3600)

        thread = threading.Thread(target=scheduler, daemon=True)
        thread.start()

    async def _run_scheduled_backups(self):
        """Run scheduled backups"""
        now = datetime.now()

        # Database backups
        db_interval = timedelta(hours=self.config.database_backup_interval_hours)
        if self._should_run_backup('database', db_interval):
            await self.create_database_backup()

        # File backups
        file_interval = timedelta(hours=self.config.file_backup_interval_hours)
        if self._should_run_backup('files', file_interval):
            await self.create_file_backup()

        # Full backups
        full_interval = timedelta(days=self.config.full_backup_interval_days)
        if self._should_run_backup('full', full_interval):
            await self.create_full_backup()

    def _should_run_backup(self, backup_type: str, interval: timedelta) -> bool:
        """Check if backup should run"""
        last_run = self.backup_schedule.get(backup_type)
        if not last_run:
            return True

        return datetime.now() - last_run >= interval

    async def create_database_backup(self) -> Optional[str]:
        """Create database backup"""
        logger.info("Starting database backup...")
        backup_path = await self.database_backup.create_backup()

        if backup_path:
            await self._finalize_backup(backup_path, "database")
            self.backup_schedule['database'] = datetime.now()

        return backup_path

    async def create_file_backup(self) -> Optional[str]:
        """Create file system backup"""
        logger.info("Starting file backup...")
        backup_path = await self.file_backup.create_backup()

        if backup_path:
            await self._finalize_backup(backup_path, "files")
            self.backup_schedule['files'] = datetime.now()

        return backup_path

    async def create_full_backup(self) -> Optional[str]:
        """Create full system backup"""
        logger.info("Starting full system backup...")

        # Create both database and file backups
        db_backup = await self.create_database_backup()
        file_backup = await self.create_file_backup()

        if db_backup and file_backup:
            # Create combined backup metadata
            full_backup_meta = {
                'type': 'full',
                'database_backup': db_backup,
                'file_backup': file_backup,
                'created_at': datetime.now().isoformat(),
                'size_bytes': self._calculate_backup_size([db_backup, file_backup])
            }

            # Store metadata
            backup_name = f"full_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.meta"
            meta_path = Path(self.config.backup_directory) / backup_name

            with open(meta_path, 'w') as f:
                json.dump(full_backup_meta, f, indent=2)

            await self._finalize_backup(str(meta_path), "full")
            self.backup_schedule['full'] = datetime.now()

            return str(meta_path)

        return None

    async def _finalize_backup(self, backup_path: str, backup_type: str):
        """Finalize backup by storing to remote locations and updating metadata"""
        try:
            backup_file = Path(backup_path)
            remote_name = backup_file.name

            # Store to remote backends
            storage_success = await self.storage.store_backup(backup_path, remote_name)

            # Update metadata
            metadata = {
                'filename': remote_name,
                'local_path': backup_path,
                'type': backup_type,
                'created_at': datetime.now().isoformat(),
                'size_bytes': backup_file.stat().st_size,
                'checksum': self._calculate_checksum(backup_path),
                'encrypted': self.config.encryption_enabled,
                'remote_stored': storage_success,
                'retention_days': self.config.retention_days
            }

            self.backup_metadata[remote_name] = metadata

            # Save metadata
            meta_file = backup_file.with_suffix('.meta')
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Backup finalized: {remote_name}")

        except Exception as e:
            logger.error(f"Backup finalization failed: {e}")

    async def restore_backup(self, backup_name: str, restore_type: str = "database") -> bool:
        """Restore from backup"""
        try:
            # Get backup metadata
            metadata = self.backup_metadata.get(backup_name)
            if not metadata:
                logger.error(f"Backup metadata not found: {backup_name}")
                return False

            # Retrieve from remote storage if needed
            local_path = metadata['local_path']
            if not Path(local_path).exists():
                if not await self.storage.retrieve_backup(backup_name, local_path):
                    logger.error(f"Failed to retrieve backup: {backup_name}")
                    return False

            # Perform restore based on type
            if restore_type == "database":
                return await self.database_backup.restore_backup(local_path)
            elif restore_type == "files":
                return await self.file_backup.restore_backup(local_path)
            elif restore_type == "full":
                # Handle full restore
                with open(local_path, 'r') as f:
                    full_meta = json.load(f)

                db_success = await self.restore_backup(
                    Path(full_meta['database_backup']).name, "database"
                )
                files_success = await self.restore_backup(
                    Path(full_meta['file_backup']).name, "files"
                )

                return db_success and files_success

            return False

        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []

        for metadata in self.backup_metadata.values():
            backup_path = Path(metadata['local_path'])
            exists_locally = backup_path.exists()

            backups.append({
                'name': metadata['filename'],
                'type': metadata['type'],
                'created_at': metadata['created_at'],
                'size_bytes': metadata['size_bytes'],
                'size_mb': round(metadata['size_bytes'] / (1024 * 1024), 2),
                'encrypted': metadata['encrypted'],
                'remote_stored': metadata['remote_stored'],
                'exists_locally': exists_locally,
                'checksum': metadata['checksum']
            })

        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups

    async def cleanup_old_backups(self):
        """Clean up backups older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config.retention_days)
            removed_count = 0

            for backup_name, metadata in list(self.backup_metadata.items()):
                created_at = datetime.fromisoformat(metadata['created_at'])

                if created_at < cutoff_date:
                    # Remove local files
                    local_path = Path(metadata['local_path'])
                    if local_path.exists():
                        local_path.unlink()

                    meta_path = local_path.with_suffix('.meta')
                    if meta_path.exists():
                        meta_path.unlink()

                    # Remove from remote storage (optional)
                    # await self.storage.delete_backup(backup_name)

                    # Remove from metadata
                    del self.backup_metadata[backup_name]
                    removed_count += 1

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old backups")

        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _calculate_backup_size(self, backup_paths: List[str]) -> int:
        """Calculate total size of backup files"""
        total_size = 0
        for path in backup_paths:
            if Path(path).exists():
                total_size += Path(path).stat().st_size
        return total_size

    async def verify_backup(self, backup_name: str) -> Dict[str, Any]:
        """Verify backup integrity"""
        try:
            metadata = self.backup_metadata.get(backup_name)
            if not metadata:
                return {'valid': False, 'error': 'Backup metadata not found'}

            local_path = metadata['local_path']
            if not Path(local_path).exists():
                return {'valid': False, 'error': 'Backup file not found locally'}

            # Verify checksum
            current_checksum = self._calculate_checksum(local_path)
            stored_checksum = metadata['checksum']

            if current_checksum != stored_checksum:
                return {'valid': False, 'error': 'Checksum mismatch'}

            # Verify file can be read/decrypted
            try:
                if self.config.encryption_enabled and self.config.encryption_key:
                    with open(local_path, 'rb') as f:
                        encrypted_data = f.read()
                    BackupEncryption.decrypt_data(encrypted_data, self.config.encryption_key)
            except Exception as e:
                return {'valid': False, 'error': f'Decryption failed: {str(e)}'}

            return {
                'valid': True,
                'size_bytes': metadata['size_bytes'],
                'checksum_verified': True,
                'encryption_verified': True
            }

        except Exception as e:
            return {'valid': False, 'error': str(e)}


# Global backup manager instance
_backup_manager: Optional[BackupManager] = None

def get_backup_manager() -> BackupManager:
    """Get global backup manager instance"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager


# Convenience functions
async def create_full_backup() -> Optional[str]:
    """Create a full system backup"""
    manager = get_backup_manager()
    return await manager.create_full_backup()

async def restore_from_backup(backup_name: str, restore_type: str = "database") -> bool:
    """Restore from a specific backup"""
    manager = get_backup_manager()
    return await manager.restore_backup(backup_name, restore_type)

def list_available_backups() -> List[Dict[str, Any]]:
    """List all available backups"""
    manager = get_backup_manager()
    return manager.list_backups()

async def verify_backup_integrity(backup_name: str) -> Dict[str, Any]:
    """Verify backup integrity"""
    manager = get_backup_manager()
    return await manager.verify_backup(backup_name)


# Disaster recovery utilities
class DisasterRecovery:
    """Disaster recovery procedures and utilities"""

    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager

    async def create_recovery_plan(self) -> Dict[str, Any]:
        """Create a comprehensive recovery plan"""
        backups = self.backup_manager.list_backups()

        # Identify latest backups of each type
        latest_db = None
        latest_files = None
        latest_full = None

        for backup in backups:
            if backup['type'] == 'database' and (not latest_db or backup['created_at'] > latest_db['created_at']):
                latest_db = backup
            elif backup['type'] == 'files' and (not latest_files or backup['created_at'] > latest_files['created_at']):
                latest_files = backup
            elif backup['type'] == 'full' and (not latest_full or backup['created_at'] > latest_full['created_at']):
                latest_full = backup

        return {
            'recovery_options': {
                'database_only': latest_db,
                'files_only': latest_files,
                'full_system': latest_full
            },
            'estimated_recovery_times': {
                'database': '15-30 minutes',
                'files': '10-20 minutes',
                'full_system': '45-90 minutes'
            },
            'recovery_steps': [
                "1. Stop all application services",
                "2. Identify appropriate backup based on data loss",
                "3. Restore database from backup",
                "4. Restore file system from backup",
                "5. Verify data integrity",
                "6. Restart application services",
                "7. Monitor system performance"
            ],
            'contact_information': {
                'emergency_contact': 'emergency@galion.ai',
                'technical_support': 'support@galion.ai',
                'backup_admin': 'backups@galion.ai'
            }
        }

    async def execute_recovery(self, recovery_type: str, backup_name: str = None) -> Dict[str, Any]:
        """Execute disaster recovery"""
        try:
            if not backup_name:
                # Use latest backup of specified type
                backups = self.backup_manager.list_backups()
                for backup in backups:
                    if backup['type'] == recovery_type:
                        backup_name = backup['name']
                        break

            if not backup_name:
                return {'success': False, 'error': f'No {recovery_type} backup found'}

            # Execute recovery
            success = await self.backup_manager.restore_backup(backup_name, recovery_type)

            return {
                'success': success,
                'backup_used': backup_name,
                'recovery_type': recovery_type,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'recovery_type': recovery_type,
                'timestamp': datetime.now().isoformat()
            }


# Global disaster recovery instance
_disaster_recovery: Optional[DisasterRecovery] = None

def get_disaster_recovery() -> DisasterRecovery:
    """Get global disaster recovery instance"""
    global _disaster_recovery
    if _disaster_recovery is None:
        _disaster_recovery = DisasterRecovery(get_backup_manager())
    return _disaster_recovery
