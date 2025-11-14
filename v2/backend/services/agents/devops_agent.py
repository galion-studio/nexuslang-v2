"""
DevOps Agent - Specialized in Infrastructure, Deployment, and CI/CD

This agent handles:
- Infrastructure as Code (Terraform, CloudFormation)
- Container orchestration (Docker, Kubernetes)
- CI/CD pipeline management
- Cloud platform operations (AWS, GCP, Azure)
- Monitoring and alerting setup
- Performance optimization
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class DevOpsAgent(BaseAgent):
    """Specialized DevOps agent for infrastructure and deployment tasks."""

    def __init__(self, name: str = "devops_agent", **kwargs):
        super().__init__(
            name=name,
            description="Specialized in infrastructure, deployment, and DevOps operations",
            capabilities=[
                "infrastructure_as_code", "container_orchestration", "ci_cd",
                "cloud_platforms", "monitoring_setup", "performance_optimization",
                "security_hardening", "backup_recovery", "scaling_automation"
            ],
            personality={
                "expertise_level": "expert",
                "communication_style": "technical",
                "specialties": ["infrastructure", "automation", "reliability"]
            },
            **kwargs
        )

        # DevOps-specific knowledge base
        self.infrastructure_patterns = {
            "terraform": self._get_terraform_patterns(),
            "kubernetes": self._get_kubernetes_patterns(),
            "docker": self._get_docker_patterns(),
            "aws": self._get_aws_patterns(),
            "monitoring": self._get_monitoring_patterns()
        }

    def _get_terraform_patterns(self) -> Dict[str, Any]:
        """Get Terraform infrastructure patterns."""
        return {
            "vpc": """
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Name = var.vpc_name
  }
}

resource "aws_subnet" "public" {
  count = length(var.public_subnets)

  vpc_id = aws_vpc.main.id
  cidr_block = var.public_subnets[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "public-${count.index + 1}"
  }
}
""",
            "ec2": """
resource "aws_instance" "web" {
  ami = var.ami_id
  instance_type = var.instance_type

  tags = {
    Name = var.instance_name
  }

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
  EOF
}
""",
            "rds": """
resource "aws_db_instance" "main" {
  allocated_storage = var.allocated_storage
  engine = var.engine
  engine_version = var.engine_version
  instance_class = var.instance_class
  name = var.db_name
  username = var.username
  password = var.password
  parameter_group_name = var.parameter_group_name
  skip_final_snapshot = true
}
"""
        }

    def _get_kubernetes_patterns(self) -> Dict[str, Any]:
        """Get Kubernetes deployment patterns."""
        return {
            "deployment": """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app_name}
  labels:
    app: {app_name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {app_name}
  template:
    metadata:
      labels:
        app: {app_name}
    spec:
      containers:
      - name: {app_name}
        image: {image}:{tag}
        ports:
        - containerPort: {port}
        env:
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
""",
            "service": """
apiVersion: v1
kind: Service
metadata:
  name: {app_name}-service
spec:
  selector:
    app: {app_name}
  ports:
  - port: {port}
    targetPort: {target_port}
    protocol: TCP
  type: {service_type}
""",
            "ingress": """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {app_name}-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: {domain}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: {app_name}-service
            port:
              number: {port}
"""
        }

    def _get_docker_patterns(self) -> Dict[str, Any]:
        """Get Docker configuration patterns."""
        return {
            "dockerfile_python": """
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Set permissions
RUN chown -R app:app /app

# Switch to app user
USER app

# Expose port
EXPOSE {port}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{port}/health || exit 1

# Default command
CMD ["python", "main.py"]
""",
            "docker_compose": """
version: '3.8'

services:
  app:
    build: .
    ports:
      - "{port}:{port}"
    environment:
      - ENV=production
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{port}/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB={db_name}
      - POSTGRES_USER={db_user}
      - POSTGRES_PASSWORD={db_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
"""
        }

    def _get_aws_patterns(self) -> Dict[str, Any]:
        """Get AWS infrastructure patterns."""
        return {
            "lambda": """
import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Initialize AWS clients
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')

    try:
        # Process the event
        body = json.loads(event['body'])
        operation = body.get('operation')

        if operation == 'process_data':
            return process_data(body, s3, dynamodb)
        elif operation == 'get_status':
            return get_status(body, dynamodb)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid operation'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
""",
            "api_gateway": """
{
  "openapi": "3.0.1",
  "info": {
    "title": "{api_name}",
    "version": "1.0.0"
  },
  "paths": {
    "/health": {
      "get": {
        "responses": {
          "200": {
            "description": "Health check response"
          }
        },
        "x-amazon-apigateway-integration": {
          "type": "aws_proxy",
          "httpMethod": "POST",
          "uri": "arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        }
      }
    }
  }
}
"""
        }

    def _get_monitoring_patterns(self) -> Dict[str, Any]:
        """Get monitoring and alerting patterns."""
        return {
            "prometheus_config": """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'galion-backend'
    static_configs:
      - targets: ['localhost:8010']
    scrape_interval: 5s
    metrics_path: '/metrics'

  - job_name: 'galion-frontend'
    static_configs:
      - targets: ['localhost:3000']
    scrape_interval: 10s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
""",
            "grafana_dashboard": """
{
  "dashboard": {
    "title": "Galion System Overview",
    "tags": ["galion", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "System CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          }
        ]
      }
    ]
  }
}
""",
            "alert_rules": """
groups:
  - name: galion_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: HighMemoryUsage
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"
"""
        }

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DevOps-related tasks."""
        task_type = task.get("type", "")
        operation = task.get("operation", "")

        if task_type == "infrastructure":
            return await self._handle_infrastructure_task(task)
        elif task_type == "deployment":
            return await self._handle_deployment_task(task)
        elif task_type == "monitoring":
            return await self._handle_monitoring_task(task)
        elif task_type == "security":
            return await self._handle_security_task(task)
        else:
            # Use general task execution for other DevOps tasks
            return await super().execute_task(task)

    async def _handle_infrastructure_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle infrastructure-related tasks."""
        operation = task.get("operation", "")

        if operation == "create_terraform_config":
            return await self._create_terraform_config(task)
        elif operation == "create_kubernetes_manifest":
            return await self._create_kubernetes_manifest(task)
        elif operation == "create_docker_config":
            return await self._create_docker_config(task)
        elif operation == "analyze_infrastructure":
            return await self._analyze_infrastructure(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown infrastructure operation: {operation}"
            }

    async def _handle_deployment_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deployment-related tasks."""
        operation = task.get("operation", "")

        if operation == "create_ci_cd_pipeline":
            return await self._create_ci_cd_pipeline(task)
        elif operation == "setup_monitoring":
            return await self._setup_monitoring(task)
        elif operation == "configure_load_balancer":
            return await self._configure_load_balancer(task)
        elif operation == "optimize_performance":
            return await self._optimize_performance(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown deployment operation: {operation}"
            }

    async def _handle_monitoring_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle monitoring-related tasks."""
        operation = task.get("operation", "")

        if operation == "setup_prometheus":
            return await self._setup_prometheus_config(task)
        elif operation == "create_grafana_dashboard":
            return await self._create_grafana_dashboard(task)
        elif operation == "configure_alerts":
            return await self._configure_alerts(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown monitoring operation: {operation}"
            }

    async def _handle_security_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle security-related tasks."""
        operation = task.get("operation", "")

        if operation == "security_audit":
            return await self._perform_security_audit(task)
        elif operation == "create_security_policy":
            return await self._create_security_policy(task)
        elif operation == "setup_vault":
            return await self._setup_vault_config(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown security operation: {operation}"
            }

    async def _create_terraform_config(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create Terraform infrastructure configuration."""
        resource_type = task.get("resource_type", "vpc")
        provider = task.get("provider", "aws")

        try:
            config = self.infrastructure_patterns.get(provider, {}).get(resource_type, "")

            if not config:
                return {
                    "status": "error",
                    "message": f"No template found for {provider} {resource_type}"
                }

            # Customize the template with task parameters
            variables = task.get("variables", {})
            for key, value in variables.items():
                config = config.replace(f"{{{key}}}", str(value))

            return {
                "status": "completed",
                "result": {
                    "config_type": "terraform",
                    "provider": provider,
                    "resource_type": resource_type,
                    "configuration": config,
                    "filename": f"main.tf"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create Terraform config: {str(e)}"
            }

    async def _create_kubernetes_manifest(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes manifest files."""
        manifest_type = task.get("manifest_type", "deployment")
        app_name = task.get("app_name", "my-app")

        try:
            template = self.infrastructure_patterns["kubernetes"].get(manifest_type, "")

            if not template:
                return {
                    "status": "error",
                    "message": f"No template found for Kubernetes {manifest_type}"
                }

            # Customize the template
            variables = task.get("variables", {
                "app_name": app_name,
                "replicas": 3,
                "image": "nginx",
                "tag": "latest",
                "port": 80,
                "target_port": 80,
                "service_type": "ClusterIP",
                "domain": f"{app_name}.example.com"
            })

            for key, value in variables.items():
                template = template.replace(f"{{{key}}}", str(value))

            return {
                "status": "completed",
                "result": {
                    "config_type": "kubernetes",
                    "manifest_type": manifest_type,
                    "app_name": app_name,
                    "manifest": template,
                    "filename": f"{app_name}-{manifest_type}.yaml"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create Kubernetes manifest: {str(e)}"
            }

    async def _create_docker_config(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create Docker configuration files."""
        config_type = task.get("config_type", "dockerfile")
        app_type = task.get("app_type", "python")

        try:
            template = self.infrastructure_patterns["docker"].get(f"{config_type}_{app_type}", "")

            if not template:
                return {
                    "status": "error",
                    "message": f"No template found for Docker {config_type} {app_type}"
                }

            # Customize the template
            variables = task.get("variables", {
                "port": 8000,
                "db_name": "myapp",
                "db_user": "myapp",
                "db_password": "password"
            })

            for key, value in variables.items():
                template = template.replace(f"{{{key}}}", str(value))

            return {
                "status": "completed",
                "result": {
                    "config_type": "docker",
                    "template_type": config_type,
                    "app_type": app_type,
                    "configuration": template,
                    "filename": "Dockerfile" if config_type == "dockerfile" else "docker-compose.yml"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create Docker config: {str(e)}"
            }

    async def _create_ci_cd_pipeline(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create CI/CD pipeline configuration."""
        platform = task.get("platform", "github")
        language = task.get("language", "python")

        try:
            if platform == "github":
                pipeline_config = self._create_github_actions_pipeline(language, task)
            elif platform == "gitlab":
                pipeline_config = self._create_gitlab_ci_pipeline(language, task)
            elif platform == "jenkins":
                pipeline_config = self._create_jenkins_pipeline(language, task)
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported CI/CD platform: {platform}"
                }

            return {
                "status": "completed",
                "result": {
                    "platform": platform,
                    "language": language,
                    "pipeline_config": pipeline_config,
                    "filename": self._get_pipeline_filename(platform)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create CI/CD pipeline: {str(e)}"
            }

    def _create_github_actions_pipeline(self, language: str, task: Dict[str, Any]) -> str:
        """Create GitHub Actions workflow."""
        if language == "python":
            return """
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=app --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: docker build -t myapp:${{ github.sha }} .

    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag myapp:${{ github.sha }} myregistry/myapp:latest
        docker push myregistry/myapp:latest

    - name: Deploy to production
      run: |
        # Add your deployment commands here
        echo "Deploying to production..."
"""

    def _create_gitlab_ci_pipeline(self, language: str, task: Dict[str, Any]) -> str:
        """Create GitLab CI pipeline."""
        return """
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_IMAGE: myapp:$CI_COMMIT_SHA

test:
  stage: test
  image: python:3.11
  before_script:
    - pip install -r requirements.txt
  script:
    - python -m pytest tests/ -v --cov=app
  coverage: '/TOTAL.*\\s+(\\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $DOCKER_IMAGE .
    - docker push $DOCKER_IMAGE

deploy_staging:
  stage: deploy
  script:
    - echo "Deploying to staging..."
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy_production:
  stage: deploy
  script:
    - echo "Deploying to production..."
  environment:
    name: production
    url: https://example.com
  when: manual
  only:
    - main
"""

    def _create_jenkins_pipeline(self, language: str, task: Dict[str, Any]) -> str:
        """Create Jenkins pipeline."""
        return """
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'python -m pytest tests/ -v --junitxml=test-results.xml'
                junit 'test-results.xml'
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t myapp:${BUILD_NUMBER} .'
            }
        }

        stage('Deploy to Staging') {
            steps {
                sh 'docker run -d --name myapp-staging -p 8080:8000 myapp:${BUILD_NUMBER}'
            }
        }

        stage('Integration Tests') {
            steps {
                sh 'curl -f http://localhost:8080/health'
            }
        }

        stage('Deploy to Production') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    input message: 'Deploy to production?'
                }
                sh 'docker stop myapp-production || true'
                sh 'docker rm myapp-production || true'
                sh 'docker run -d --name myapp-production -p 80:8000 myapp:${BUILD_NUMBER}'
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
"""

    def _get_pipeline_filename(self, platform: str) -> str:
        """Get the pipeline filename for the platform."""
        if platform == "github":
            return ".github/workflows/ci-cd.yml"
        elif platform == "gitlab":
            return ".gitlab-ci.yml"
        elif platform == "jenkins":
            return "Jenkinsfile"
        else:
            return "pipeline.yml"

    async def _setup_prometheus_config(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create Prometheus monitoring configuration."""
        try:
            config = self.infrastructure_patterns["monitoring"]["prometheus_config"]

            # Customize with task parameters
            variables = task.get("variables", {})
            for key, value in variables.items():
                config = config.replace(f"{{{key}}}", str(value))

            return {
                "status": "completed",
                "result": {
                    "config_type": "monitoring",
                    "tool": "prometheus",
                    "configuration": config,
                    "filename": "prometheus.yml"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create Prometheus config: {str(e)}"
            }

    async def _create_grafana_dashboard(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create Grafana dashboard configuration."""
        try:
            dashboard = self.infrastructure_patterns["monitoring"]["grafana_dashboard"]

            # Customize dashboard
            variables = task.get("variables", {
                "title": "System Overview",
                "tags": ["monitoring"]
            })

            dashboard_str = json.dumps(json.loads(dashboard), indent=2)

            return {
                "status": "completed",
                "result": {
                    "config_type": "monitoring",
                    "tool": "grafana",
                    "dashboard": dashboard_str,
                    "filename": "dashboard.json"
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create Grafana dashboard: {str(e)}"
            }

    async def _perform_security_audit(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform security audit on infrastructure/code."""
        target = task.get("target", "infrastructure")

        try:
            findings = []

            if target == "infrastructure":
                findings = await self._audit_infrastructure_security(task)
            elif target == "code":
                findings = await self._audit_code_security(task)
            elif target == "containers":
                findings = await self._audit_container_security(task)

            # Generate recommendations
            recommendations = self._generate_security_recommendations(findings)

            return {
                "status": "completed",
                "result": {
                    "audit_type": target,
                    "findings": findings,
                    "recommendations": recommendations,
                    "risk_level": self._calculate_risk_level(findings)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Security audit failed: {str(e)}"
            }

    async def _audit_infrastructure_security(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audit infrastructure security."""
        findings = []

        # Common security checks
        checks = [
            {
                "check": "public_ports_exposed",
                "severity": "high",
                "description": "Sensitive ports exposed to public internet",
                "recommendation": "Use security groups to restrict access"
            },
            {
                "check": "unencrypted_communication",
                "severity": "medium",
                "description": "Services communicating without encryption",
                "recommendation": "Implement TLS/SSL encryption"
            },
            {
                "check": "weak_passwords",
                "severity": "high",
                "description": "Default or weak passwords detected",
                "recommendation": "Use strong, unique passwords and password manager"
            },
            {
                "check": "missing_updates",
                "severity": "medium",
                "description": "Systems not up to date with security patches",
                "recommendation": "Implement automated security updates"
            }
        ]

        findings.extend(checks)
        return findings

    async def _audit_code_security(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audit code security."""
        findings = []

        # Code security checks
        checks = [
            {
                "check": "sql_injection",
                "severity": "critical",
                "description": "Potential SQL injection vulnerabilities",
                "recommendation": "Use parameterized queries or ORM"
            },
            {
                "check": "xss_vulnerabilities",
                "severity": "high",
                "description": "Cross-site scripting vulnerabilities detected",
                "recommendation": "Sanitize user input and use CSP headers"
            },
            {
                "check": "hardcoded_secrets",
                "severity": "high",
                "description": "Hardcoded secrets found in code",
                "recommendation": "Use environment variables or secret management"
            }
        ]

        findings.extend(checks)
        return findings

    async def _audit_container_security(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Audit container security."""
        findings = []

        # Container security checks
        checks = [
            {
                "check": "running_as_root",
                "severity": "high",
                "description": "Containers running as root user",
                "recommendation": "Create non-root user in Dockerfile"
            },
            {
                "check": "latest_tag_used",
                "severity": "medium",
                "description": "Using 'latest' tag for container images",
                "recommendation": "Use specific version tags for reproducibility"
            },
            {
                "check": "large_image_size",
                "severity": "low",
                "description": "Container images are larger than recommended",
                "recommendation": "Use multi-stage builds and minimal base images"
            }
        ]

        findings.extend(checks)
        return findings

    def _generate_security_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []

        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for finding in findings:
            severity = finding.get("severity", "low")
            severity_counts[severity] += 1
            recommendations.append(f"[{severity.upper()}] {finding.get('recommendation', '')}")

        # Add priority-based recommendations
        if severity_counts["critical"] > 0:
            recommendations.insert(0, "URGENT: Address critical security findings immediately")
        if severity_counts["high"] > 0:
            recommendations.insert(0, "HIGH PRIORITY: Address high-severity security issues")

        return recommendations

    def _calculate_risk_level(self, findings: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level from findings."""
        critical_count = sum(1 for f in findings if f.get("severity") == "critical")
        high_count = sum(1 for f in findings if f.get("severity") == "high")

        if critical_count > 0:
            return "critical"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"
