#!/bin/bash
# User data script for ECS general instances

# Configure ECS agent
echo "ECS_CLUSTER=${cluster_name}" >> /etc/ecs/ecs.config
echo "ECS_ENABLE_TASK_IAM_ROLE=true" >> /etc/ecs/ecs.config
echo "ECS_ENABLE_TASK_IAM_ROLE_NETWORK_HOST=true" >> /etc/ecs/ecs.config
echo "ECS_ENABLE_CONTAINER_METADATA=true" >> /etc/ecs/ecs.config

# Enable CloudWatch agent
yum install -y amazon-cloudwatch-agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c default

# Update packages
yum update -y

# Install SSM agent (for Session Manager)
yum install -y amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

