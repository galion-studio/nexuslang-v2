# Terraform Configuration for Project Nexus
# Infrastructure as Code for reproducible deployments

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.42"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
  
  # Backend configuration for state management
  backend "s3" {
    # Use Cloudflare R2 for state storage
    bucket = "nexus-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "auto"
    
    # R2 S3-compatible endpoint
    endpoints = {
      s3 = "https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com"
    }
    
    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
  }
}

# Variables
variable "hcloud_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_api_token" {
  description = "Cloudflare API token"
  type        = string
  sensitive   = true
}

variable "cloudflare_zone_id" {
  description = "Cloudflare zone ID for galion.app"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key for server access"
  type        = string
}

# Providers
provider "hcloud" {
  token = var.hcloud_token
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# SSH Key
resource "hcloud_ssh_key" "nexus" {
  name       = "nexus-deployment"
  public_key = var.ssh_public_key
}

# Server
resource "hcloud_server" "nexus" {
  name        = "nexus-production"
  server_type = "cx21"  # 2 vCPU, 4GB RAM, 40GB SSD - $5.83/month
  image       = "ubuntu-22.04"
  location    = "nbg1"  # Nuremberg, Germany (or choose based on your location)
  ssh_keys    = [hcloud_ssh_key.nexus.id]
  
  labels = {
    project     = "nexus"
    environment = "production"
    managed_by  = "terraform"
  }
  
  # User data for initial setup
  user_data = file("${path.module}/cloud-init.yml")
  
  # Firewall
  firewall_ids = [hcloud_firewall.nexus.id]
}

# Firewall
resource "hcloud_firewall" "nexus" {
  name = "nexus-firewall"
  
  # SSH
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "22"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
  }
  
  # HTTP
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "80"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
  }
  
  # HTTPS
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "443"
    source_ips = [
      "0.0.0.0/0",
      "::/0"
    ]
  }
  
  # PostgreSQL (only from Cloudflare IPs for security)
  rule {
    direction = "in"
    protocol  = "tcp"
    port      = "5432"
    source_ips = [
      "173.245.48.0/20",
      "103.21.244.0/22",
      "103.22.200.0/22",
      # Add more Cloudflare IPs as needed
    ]
  }
}

# Volume for persistent data
resource "hcloud_volume" "nexus_data" {
  name      = "nexus-data"
  size      = 100  # 100GB - $5/month
  server_id = hcloud_server.nexus.id
  automount = true
  format    = "ext4"
  
  labels = {
    project = "nexus"
    type    = "data"
  }
}

# Volume for backups
resource "hcloud_volume" "nexus_backups" {
  name      = "nexus-backups"
  size      = 50  # 50GB - $2.50/month
  server_id = hcloud_server.nexus.id
  automount = true
  format    = "ext4"
  
  labels = {
    project = "nexus"
    type    = "backups"
  }
}

# Cloudflare DNS Records
resource "cloudflare_record" "galion_app" {
  zone_id = var.cloudflare_zone_id
  name    = "@"
  value   = hcloud_server.nexus.ipv4_address
  type    = "A"
  ttl     = 1  # Automatic (proxied through Cloudflare)
  proxied = true
}

resource "cloudflare_record" "api_galion_app" {
  zone_id = var.cloudflare_zone_id
  name    = "api"
  value   = hcloud_server.nexus.ipv4_address
  type    = "A"
  ttl     = 1
  proxied = true
}

resource "cloudflare_record" "www_galion_app" {
  zone_id = var.cloudflare_zone_id
  name    = "www"
  value   = hcloud_server.nexus.ipv4_address
  type    = "A"
  ttl     = 1
  proxied = true
}

resource "cloudflare_record" "status_galion_app" {
  zone_id = var.cloudflare_zone_id
  name    = "status"
  value   = "stats.uptimerobot.com"
  type    = "CNAME"
  ttl     = 1
  proxied = false  # Don't proxy status page
}

# Outputs
output "server_ip" {
  description = "Server IP address"
  value       = hcloud_server.nexus.ipv4_address
}

output "server_id" {
  description = "Server ID"
  value       = hcloud_server.nexus.id
}

output "data_volume_id" {
  description = "Data volume ID"
  value       = hcloud_volume.nexus_data.id
}

output "backup_volume_id" {
  description = "Backup volume ID"
  value       = hcloud_volume.nexus_backups.id
}

# Estimated monthly cost
output "estimated_monthly_cost" {
  description = "Estimated monthly infrastructure cost"
  value       = "$13.33 (Server: $5.83 + Data Volume: $5.00 + Backup Volume: $2.50)"
}

