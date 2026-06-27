#!/bin/bash
# EC2 user-data script. Paste this into the "User data" field when
# launching the instance (Advanced details section) - it runs automatically
# on first boot, no manual SSH needed for initial setup.
#
# Why EC2 + docker-compose instead of ECS/Fargate/EKS: this is a portfolio
# project, not a team's production system. A single instance running the
# same docker-compose.yml you already tested locally is something you can
# fully explain in an interview. ECS/EKS add real value at a scale and
# org-complexity this project isn't at yet - Day 25 covers K8s manifests
# separately so you have them ready, without forcing you onto a cluster
# you'd have to justify running for one project.
set -e

# Docker + Compose plugin
yum update -y
yum install -y docker git
systemctl enable docker
systemctl start docker
usermod -aG docker ec2-user

mkdir -p /usr/local/lib/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
    -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# clone + first run - replace with your actual repo URL
cd /home/ec2-user
sudo -u ec2-user git clone https://github.com/sumedChalakh/nexusai-enterprise-platform.git app
cd app

# .env is NOT in git - you still need to create backend/.env on the instance
# yourself (scp it up, or paste it via SSM Parameter Store / Secrets Manager
# for a more production-grade approach later)
echo "Bootstrap done. SSH in, add backend/.env, then run:"
echo "  docker compose -f docker-compose.hardened.yml up --build -d"
