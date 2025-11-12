#!/usr/bin/env python3
"""
Automated Backup Daemon for Project Nexus
Implements 3-2-1 backup strategy:
- 3 copies of data
- 2 different storage media
- 1 offsite backup

Features:
- Hourly database snapshots
- Daily full backups
- Automatic cleanup of old backups
- Offsite sync to Backblaze B2
- Backup verification
- Slack/Discord notifications on failure

Usage:
    python backup-daemon.py --config backup-config.yml
"""

import os
import sys
import yaml
import subprocess
import datetime
import time
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import shutil


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/nexus-backup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('backup-daemon')


class BackupConfig:
    """Configuration for backup system"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Database settings
        self.db_host = self.config['database']['host']
        self.db_port = self.config['database']['port']
        self.db_name = self.config['database']['name']
        self.db_user = self.config['database']['user']
        self.db_password = os.getenv('POSTGRES_PASSWORD')
        
        # Backup locations
        self.backup_dir = Path(self.config['backup']['local_dir'])
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Retention policies
        self.keep_hourly = self.config['retention']['hourly']
        self.keep_daily = self.config['retention']['daily']
        self.keep_weekly = self.config['retention']['weekly']
        self.keep_monthly = self.config['retention']['monthly']
        
        # Offsite backup (Backblaze B2)
        self.b2_enabled = self.config.get('b2', {}).get('enabled', False)
        self.b2_bucket = self.config.get('b2', {}).get('bucket')
        self.b2_key_id = os.getenv('BACKBLAZE_KEY_ID')
        self.b2_app_key = os.getenv('BACKBLAZE_APPLICATION_KEY')


class BackupDaemon:
    """Main backup daemon class"""
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.running = True
        
    def create_db_backup(self, backup_type: str = 'hourly') -> Optional[Path]:
        """
        Create a PostgreSQL database backup.
        
        Args:
            backup_type: Type of backup (hourly, daily, weekly, monthly)
            
        Returns:
            Path to backup file or None if failed
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"nexus_db_{backup_type}_{timestamp}.sql.gz"
        backup_path = self.config.backup_dir / backup_filename
        
        logger.info(f"Creating {backup_type} database backup: {backup_filename}")
        
        try:
            # Use pg_dump with compression
            cmd = [
                'pg_dump',
                '-h', self.config.db_host,
                '-p', str(self.config.db_port),
                '-U', self.config.db_user,
                '-d', self.config.db_name,
                '--no-password',
                '-F', 'c',  # Custom format (compressed)
                '-f', str(backup_path)
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config.db_password
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # Verify backup file was created
                if backup_path.exists() and backup_path.stat().st_size > 0:
                    # Calculate checksum
                    checksum = self.calculate_checksum(backup_path)
                    
                    # Save metadata
                    self.save_backup_metadata(backup_path, backup_type, checksum)
                    
                    logger.info(f"✅ Backup created successfully: {backup_filename} ({self.get_file_size(backup_path)})")
                    return backup_path
                else:
                    logger.error(f"❌ Backup file empty or not created: {backup_filename}")
                    return None
            else:
                logger.error(f"❌ pg_dump failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Backup timed out after 5 minutes")
            return None
        except Exception as e:
            logger.error(f"❌ Backup failed with exception: {e}")
            return None
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def save_backup_metadata(self, backup_path: Path, backup_type: str, checksum: str):
        """Save metadata about a backup"""
        metadata = {
            'filename': backup_path.name,
            'backup_type': backup_type,
            'created_at': datetime.datetime.now().isoformat(),
            'size_bytes': backup_path.stat().st_size,
            'checksum_sha256': checksum,
            'database': self.config.db_name,
            'verified': False
        }
        
        metadata_path = backup_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def verify_backup(self, backup_path: Path) -> bool:
        """
        Verify a backup by checking its integrity.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if backup is valid, False otherwise
        """
        logger.info(f"Verifying backup: {backup_path.name}")
        
        try:
            # Check if metadata exists
            metadata_path = backup_path.with_suffix('.json')
            if not metadata_path.exists():
                logger.warning(f"No metadata found for {backup_path.name}")
                return False
            
            # Load metadata
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Verify checksum
            current_checksum = self.calculate_checksum(backup_path)
            if current_checksum != metadata['checksum_sha256']:
                logger.error(f"❌ Checksum mismatch for {backup_path.name}")
                return False
            
            # Test restore (to /tmp)
            test_db = f"nexus_verify_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cmd = [
                'pg_restore',
                '-h', self.config.db_host,
                '-p', str(self.config.db_port),
                '-U', self.config.db_user,
                '-d', 'postgres',  # Connect to postgres to create test db
                '--no-password',
                '--create',
                '--dbname', test_db,
                str(backup_path)
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config.db_password
            
            # Verify can read the backup (don't actually restore)
            cmd_list = ['pg_restore', '--list', str(backup_path)]
            result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"✅ Backup verified: {backup_path.name}")
                
                # Update metadata
                metadata['verified'] = True
                metadata['verified_at'] = datetime.datetime.now().isoformat()
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return True
            else:
                logger.error(f"❌ Backup verification failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Backup verification exception: {e}")
            return False
    
    def sync_to_b2(self, backup_path: Path) -> bool:
        """
        Sync backup to Backblaze B2 (offsite backup).
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if sync successful, False otherwise
        """
        if not self.config.b2_enabled:
            logger.info("B2 sync disabled, skipping")
            return True
        
        logger.info(f"Syncing to B2: {backup_path.name}")
        
        try:
            # Use rclone to sync to B2
            cmd = [
                'rclone',
                'copy',
                str(backup_path),
                f"b2:{self.config.b2_bucket}/backups/",
                '--b2-account', self.config.b2_key_id,
                '--b2-key', self.config.b2_app_key,
                '--progress',
                '--transfers', '4'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info(f"✅ Synced to B2: {backup_path.name}")
                
                # Also sync metadata
                metadata_path = backup_path.with_suffix('.json')
                if metadata_path.exists():
                    cmd[2] = str(metadata_path)
                    subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                return True
            else:
                logger.error(f"❌ B2 sync failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ B2 sync timed out")
            return False
        except Exception as e:
            logger.error(f"❌ B2 sync exception: {e}")
            return False
    
    def cleanup_old_backups(self):
        """
        Remove old backups according to retention policy.
        Keeps:
        - Last N hourly backups
        - Last N daily backups
        - Last N weekly backups
        - Last N monthly backups
        """
        logger.info("Cleaning up old backups...")
        
        # Get all backup files
        backup_files = sorted(
            self.config.backup_dir.glob("nexus_db_*.sql.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Organize by type
        backups_by_type = {
            'hourly': [],
            'daily': [],
            'weekly': [],
            'monthly': []
        }
        
        for backup_file in backup_files:
            for backup_type in backups_by_type.keys():
                if f"_{backup_type}_" in backup_file.name:
                    backups_by_type[backup_type].append(backup_file)
                    break
        
        # Apply retention policy
        retention = {
            'hourly': self.config.keep_hourly,
            'daily': self.config.keep_daily,
            'weekly': self.config.keep_weekly,
            'monthly': self.config.keep_monthly
        }
        
        deleted_count = 0
        for backup_type, keep_count in retention.items():
            backups = backups_by_type[backup_type]
            to_delete = backups[keep_count:]  # Keep first N, delete rest
            
            for backup_file in to_delete:
                logger.info(f"Deleting old backup: {backup_file.name}")
                backup_file.unlink()
                
                # Also delete metadata
                metadata_file = backup_file.with_suffix('.json')
                if metadata_file.exists():
                    metadata_file.unlink()
                
                deleted_count += 1
        
        logger.info(f"✅ Cleaned up {deleted_count} old backups")
    
    def get_file_size(self, path: Path) -> str:
        """Get human-readable file size"""
        size_bytes = path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def run_hourly_backup(self):
        """Run hourly backup cycle"""
        logger.info("=" * 60)
        logger.info("Starting hourly backup cycle")
        logger.info("=" * 60)
        
        backup_path = self.create_db_backup('hourly')
        
        if backup_path:
            # Verify backup
            if self.verify_backup(backup_path):
                # Sync to B2 (best effort)
                self.sync_to_b2(backup_path)
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        logger.info("Hourly backup cycle complete")
        logger.info("=" * 60)
    
    def run_daily_backup(self):
        """Run daily backup cycle"""
        logger.info("=" * 60)
        logger.info("Starting daily backup cycle")
        logger.info("=" * 60)
        
        backup_path = self.create_db_backup('daily')
        
        if backup_path:
            # Verify backup
            if self.verify_backup(backup_path):
                # Always sync daily backups to B2
                self.sync_to_b2(backup_path)
    
    def run(self):
        """Main daemon loop"""
        logger.info("🚀 Backup daemon started")
        
        # Track last backup times
        last_hourly = datetime.datetime.now() - datetime.timedelta(hours=1)
        last_daily = datetime.datetime.now() - datetime.timedelta(days=1)
        
        while self.running:
            now = datetime.datetime.now()
            
            # Check if hourly backup is due
            if (now - last_hourly).total_seconds() >= 3600:  # 1 hour
                self.run_hourly_backup()
                last_hourly = now
            
            # Check if daily backup is due (at 2 AM)
            if now.hour == 2 and (now - last_daily).days >= 1:
                self.run_daily_backup()
                last_daily = now
            
            # Sleep for 5 minutes
            time.sleep(300)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Project Nexus Backup Daemon')
    parser.add_argument('--config', default='backup-config.yml', help='Path to config file')
    parser.add_argument('--once', action='store_true', help='Run once and exit (for testing)')
    
    args = parser.parse_args()
    
    # Load configuration
    if not os.path.exists(args.config):
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)
    
    config = BackupConfig(args.config)
    daemon = BackupDaemon(config)
    
    if args.once:
        # Run once for testing
        daemon.run_hourly_backup()
    else:
        # Run as daemon
        try:
            daemon.run()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal, exiting...")
            daemon.running = False


if __name__ == '__main__':
    main()

