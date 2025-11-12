#!/usr/bin/env python3
"""
Database Restore Script for NexusLang v2
=========================================

Restores PostgreSQL database from backup.
Designed for RunPod pod recovery scenarios.

Features:
- Auto-detect latest backup
- Decompress gzip backups
- Pre-restore validation
- Safe restore with confirmation
- Progress tracking

Usage:
    python restore_database.py                    # Restore latest backup
    python restore_database.py --file backup.sql.gz  # Restore specific file
    python restore_database.py --list             # List available backups
    python restore_database.py --force            # Skip confirmation
"""

import os
import sys
import subprocess
import gzip
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import argparse
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import settings


class DatabaseRestore:
    """
    Handles PostgreSQL database restoration from backups.
    """
    
    def __init__(self, backup_dir: str = "/workspace/backups"):
        """
        Initialize restore system.
        
        Args:
            backup_dir: Directory containing backups
        """
        self.backup_dir = Path(backup_dir)
        
        # Parse database URL (same as backup script)
        self.parse_database_url()
    
    def parse_database_url(self):
        """Parse DATABASE_URL to extract connection details."""
        url = settings.DATABASE_URL
        
        url = url.replace('postgresql+asyncpg://', '')
        url = url.replace('postgresql://', '')
        
        if '@' in url:
            auth, rest = url.split('@', 1)
            if ':' in auth:
                self.db_user, self.db_password = auth.split(':', 1)
            else:
                self.db_user = auth
                self.db_password = ''
            
            if '/' in rest:
                host_port, self.db_name = rest.split('/', 1)
                if ':' in host_port:
                    self.db_host, port_str = host_port.split(':', 1)
                    self.db_port = int(port_str)
                else:
                    self.db_host = host_port
                    self.db_port = 5432
            else:
                self.db_host = rest
                self.db_port = 5432
                self.db_name = settings.POSTGRES_DB
        else:
            self.db_user = settings.POSTGRES_USER
            self.db_password = settings.POSTGRES_PASSWORD
            self.db_name = settings.POSTGRES_DB
            self.db_host = 'localhost'
            self.db_port = 5432
    
    def list_backups(self) -> List[Path]:
        """
        List all available backups sorted by date (newest first).
        
        Returns:
            List of backup file paths
        """
        if not self.backup_dir.exists():
            return []
        
        backups = sorted(
            self.backup_dir.glob("nexuslang_v2_backup_*.sql.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        return backups
    
    def get_latest_backup(self) -> Optional[Path]:
        """
        Get the most recent backup file.
        
        Returns:
            Path to latest backup, or None if no backups found
        """
        backups = self.list_backups()
        return backups[0] if backups else None
    
    def validate_backup(self, backup_path: Path) -> bool:
        """
        Validate backup file before restoration.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if valid, False otherwise
        """
        print(f"🔍 Validating backup: {backup_path.name}")
        
        # Check file exists
        if not backup_path.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        # Check file size
        size_mb = backup_path.stat().st_size / 1024 / 1024
        if size_mb < 0.01:  # Less than 10KB is suspicious
            print(f"❌ Backup file too small: {size_mb:.2f} MB")
            return False
        
        print(f"✅ Backup file size: {size_mb:.2f} MB")
        
        # Try to decompress first few bytes
        try:
            with gzip.open(backup_path, 'rb') as f:
                header = f.read(100).decode('utf-8', errors='ignore')
                if 'PostgreSQL' in header or 'CREATE' in header or 'DROP' in header:
                    print("✅ Backup file appears valid")
                    return True
                else:
                    print("⚠️  Backup file header unexpected, but continuing...")
                    return True
        except Exception as e:
            print(f"❌ Cannot read backup file: {e}")
            return False
    
    def restore_backup(self, backup_path: Path, force: bool = False) -> bool:
        """
        Restore database from backup file.
        
        Args:
            backup_path: Path to backup file (.sql.gz)
            force: Skip confirmation prompt
            
        Returns:
            True if successful, False otherwise
        """
        # Validate backup first
        if not self.validate_backup(backup_path):
            return False
        
        # Load metadata if available
        meta_file = backup_path.parent / f"{backup_path.stem}.sql.meta.json"
        if meta_file.exists():
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                print(f"📊 Backup metadata:")
                print(f"   Created: {meta.get('timestamp', 'Unknown')}")
                print(f"   Database: {meta.get('database', 'Unknown')}")
                print("")
        
        # Confirmation prompt
        if not force:
            print("⚠️  WARNING: This will REPLACE all current database data!")
            print(f"   Database: {self.db_name} on {self.db_host}")
            print("")
            response = input("Continue with restore? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Restore cancelled")
                return False
            print("")
        
        try:
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password
            
            # Decompress backup to temp file
            print("🗜️  Decompressing backup...")
            temp_sql = backup_path.parent / "temp_restore.sql"
            
            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_sql, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print("✅ Decompressed successfully")
            print("")
            
            # Run psql to restore
            print(f"🔄 Restoring database: {self.db_name}")
            print("   This may take a few minutes...")
            print("")
            
            subprocess.run(
                [
                    'psql',
                    '-h', self.db_host,
                    '-p', str(self.db_port),
                    '-U', self.db_user,
                    '-d', self.db_name,
                    '-f', str(temp_sql),
                    '--quiet'
                ],
                env=env,
                check=True,
                stderr=subprocess.PIPE
            )
            
            # Remove temp file
            temp_sql.unlink()
            
            print("✅ Database restored successfully!")
            print("")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Restore failed: {e}")
            if e.stderr:
                print(f"   Error: {e.stderr.decode()}")
            
            # Clean up temp file
            if temp_sql.exists():
                temp_sql.unlink()
            
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def print_backup_list(self):
        """Print formatted list of available backups."""
        backups = self.list_backups()
        
        if not backups:
            print("No backups found in:", self.backup_dir)
            return
        
        print(f"📋 Available Backups ({len(backups)}):")
        print("=" * 80)
        print("")
        
        for i, backup in enumerate(backups, 1):
            size_mb = backup.stat().st_size / 1024 / 1024
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            age = datetime.now() - mtime
            
            # Load metadata
            meta_file = backup.parent / f"{backup.stem}.sql.meta.json"
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    meta = json.load(f)
                    
                print(f"  {i}. {backup.name}")
                print(f"     Size: {size_mb:.2f} MB")
                print(f"     Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"     Age: {age.days} days, {age.seconds // 3600} hours")
                print(f"     Compression: {meta.get('compression_ratio', 0):.2f}x")
            else:
                print(f"  {i}. {backup.name}")
                print(f"     Size: {size_mb:.2f} MB")
                print(f"     Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print("")


def main():
    """Main entry point for restore script."""
    parser = argparse.ArgumentParser(description='Restore NexusLang v2 database from backup')
    parser.add_argument('--file', type=str, help='Specific backup file to restore')
    parser.add_argument('--latest', action='store_true', help='Restore latest backup (default)')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--backup-dir', type=str, default='/workspace/backups', help='Backup directory')
    
    args = parser.parse_args()
    
    restore_system = DatabaseRestore(backup_dir=args.backup_dir)
    
    # List backups if requested
    if args.list:
        restore_system.print_backup_list()
        return
    
    print("=" * 80)
    print("🗄️  NexusLang v2 Database Restore")
    print("=" * 80)
    print("")
    
    # Determine which backup to restore
    if args.file:
        backup_path = Path(args.file)
        if not backup_path.is_absolute():
            backup_path = restore_system.backup_dir / backup_path
    else:
        # Use latest backup
        backup_path = restore_system.get_latest_backup()
        if not backup_path:
            print("❌ No backups found in:", restore_system.backup_dir)
            print("")
            print("Create a backup first with:")
            print("   python backup_database.py")
            sys.exit(1)
        
        print(f"📦 Using latest backup: {backup_path.name}")
        print("")
    
    # Perform restore
    success = restore_system.restore_backup(backup_path, force=args.force)
    
    if success:
        print("=" * 80)
        print("🎉 Database Restored Successfully!")
        print("=" * 80)
        print("")
        print("Next steps:")
        print("  1. Restart your application")
        print("  2. Verify data integrity")
        print("  3. Check logs for any issues")
        print("")
        sys.exit(0)
    else:
        print("=" * 80)
        print("❌ Restore Failed!")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()

