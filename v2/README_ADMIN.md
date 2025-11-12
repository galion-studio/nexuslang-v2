# Admin Guide - Content Management System

## Quick Admin Access

### Setup Environment Variables

Add to your shell profile (`.bashrc`, `.zshrc`, or PowerShell profile):

```bash
# Bash/Zsh
export RUNPOD_HOST="your-runpod-ip"
export RUNPOD_PORT="your-ssh-port"
```

```powershell
# PowerShell
$env:RUNPOD_HOST = "your-runpod-ip"
$env:RUNPOD_PORT = "your-ssh-port"
```

### Use Admin Control Script

**Windows PowerShell**:
```powershell
# Interactive menu
.\admin-control.ps1

# Direct commands
.\admin-control.ps1 -Action deploy
.\admin-control.ps1 -Action logs
.\admin-control.ps1 -Action status
```

**Linux/Mac** (create bash version):
```bash
# SSH alias
alias runpod-ssh='ssh nexus-admin@$RUNPOD_HOST -p $RUNPOD_PORT'

# Quick commands
alias runpod-logs='runpod-ssh "cd /home/nexus-admin/project-nexus/v2 && docker-compose logs -f"'
alias runpod-status='runpod-ssh "cd /home/nexus-admin/project-nexus/v2 && docker-compose ps"'
```

## Common Admin Tasks

### 1. Deploy Updates

```powershell
# From local machine
.\admin-control.ps1 -Action deploy

# Or manually
ssh nexus-admin@$RUNPOD_HOST -p $RUNPOD_PORT
cd /home/nexus-admin/project-nexus
git pull origin main
cd v2
docker-compose -f docker-compose.nexuslang.yml up -d
```

### 2. View Real-Time Logs

```powershell
.\admin-control.ps1 -Action logs

# Or specific service
ssh nexus-admin@$RUNPOD_HOST -p $RUNPOD_PORT \
  "cd /home/nexus-admin/project-nexus/v2 && docker-compose logs -f backend"
```

### 3. Database Management

**Access Database**:
```powershell
.\admin-control.ps1 -Action db
```

**Run Query**:
```sql
-- View all brands
SELECT * FROM brands;

-- View recent posts
SELECT * FROM content_posts ORDER BY created_at DESC LIMIT 10;

-- View scheduled posts
SELECT * FROM scheduled_jobs WHERE status = 'pending';

-- Analytics summary
SELECT 
    platform,
    COUNT(*) as posts,
    SUM(likes) as total_likes
FROM platform_posts pp
JOIN post_analytics pa ON pp.id = pa.platform_post_id
GROUP BY platform;
```

### 4. Create Backup

```powershell
.\admin-control.ps1 -Action backup
```

This creates a timestamped backup in `~/backups/` on RunPod and optionally downloads it.

### 5. Monitor System Health

```powershell
# View service status
.\admin-control.ps1 -Action status

# Test API
.\admin-control.ps1 -Action test

# View upcoming posts
.\admin-control.ps1 -Action upcoming
```

### 6. Manual Operations

**Sync Analytics**:
```powershell
.\admin-control.ps1 -Action sync
```

**Process Scheduled Jobs**:
```powershell
.\admin-control.ps1 -Action jobs
```

### 7. Development Access

**Open SSH Tunnel**:
```powershell
.\admin-control.ps1 -Action tunnel
```

This forwards all ports to localhost:
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Backend: localhost:8100
- Frontend: localhost:3100

Now you can:
- Connect to database from local tools (DataGrip, pgAdmin)
- Test API from Postman using localhost:8100
- Debug frontend at localhost:3100

## Cursor Integration

### Remote Development

1. Open Cursor
2. Install "Remote - SSH" extension
3. Add SSH config:

```
Host runpod-nexus
    HostName <YOUR_RUNPOD_IP>
    Port <YOUR_SSH_PORT>
    User nexus-admin
    IdentityFile ~/.ssh/id_ed25519
```

4. Connect: Cmd+Shift+P → "Remote-SSH: Connect to Host" → "runpod-nexus"
5. Open folder: `/home/nexus-admin/project-nexus`

### Local Git Sync

Keep your local repository in sync:

```bash
# On local machine
cd path/to/project-nexus
git pull origin main

# Make changes
git add .
git commit -m "Update content manager"
git push origin main

# Then deploy to RunPod
.\admin-control.ps1 -Action deploy
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
.\admin-control.ps1 -Action logs

# Restart services
.\admin-control.ps1 -Action restart

# If that fails, rebuild
ssh nexus-admin@$RUNPOD_HOST -p $RUNPOD_PORT
cd /home/nexus-admin/project-nexus/v2
docker-compose down
docker-compose build
docker-compose up -d
```

### Database Issues

```bash
# Check database is running
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Restore from backup
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U nexuslang nexuslang_v2
```

### Network Issues

```bash
# Check firewall
sudo ufw status

# Check if ports are open
netstat -tulpn | grep -E '(3100|8100)'

# Restart Cloudflare tunnel
sudo systemctl restart cloudflared
```

## Security Best Practices

1. **Never commit credentials** - Use environment variables
2. **Rotate SSH keys** - Every 90 days
3. **Regular backups** - Automated daily
4. **Monitor logs** - Check for suspicious activity
5. **Update dependencies** - Monthly security updates
6. **Strong passwords** - For database and user accounts
7. **Firewall rules** - Only allow necessary ports
8. **HTTPS only** - Via Cloudflare Tunnel

## Performance Monitoring

### Check Resource Usage

```bash
# On RunPod
docker stats

# Disk usage
df -h

# Database size
docker-compose exec postgres psql -U nexuslang nexuslang_v2 -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### Optimize Database

```bash
# Vacuum and analyze
docker-compose exec postgres psql -U nexuslang nexuslang_v2 -c "VACUUM ANALYZE;"

# Reindex
docker-compose exec postgres psql -U nexuslang nexuslang_v2 -c "REINDEX DATABASE nexuslang_v2;"
```

## Useful SQL Queries

```sql
-- Top performing posts
SELECT 
    cp.title,
    b.name as brand,
    SUM(pa.likes + pa.comments + pa.shares) as total_engagement,
    COUNT(pp.id) as platform_count
FROM content_posts cp
JOIN brands b ON cp.brand_id = b.id
JOIN platform_posts pp ON cp.id = pp.content_post_id
JOIN post_analytics pa ON pp.id = pa.platform_post_id
GROUP BY cp.id, b.name
ORDER BY total_engagement DESC
LIMIT 10;

-- Posting frequency by brand
SELECT 
    b.name,
    COUNT(*) as total_posts,
    COUNT(CASE WHEN cp.status = 'published' THEN 1 END) as published,
    COUNT(CASE WHEN cp.status = 'scheduled' THEN 1 END) as scheduled
FROM brands b
LEFT JOIN content_posts cp ON b.id = cp.brand_id
GROUP BY b.name;

-- Platform performance
SELECT 
    pp.platform,
    COUNT(*) as posts,
    AVG(pa.engagement_rate) as avg_engagement,
    SUM(pa.views) as total_views
FROM platform_posts pp
JOIN post_analytics pa ON pp.id = pa.platform_post_id
GROUP BY pp.platform
ORDER BY avg_engagement DESC;
```

## Contact

For issues or questions:
- Create GitHub issue: https://github.com/<YOUR_ORG>/project-nexus/issues
- Email: admin@galion.studio
- Check documentation: `v2/CONTENT_MANAGER_IMPLEMENTATION_COMPLETE.md`

