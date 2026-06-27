#!/bin/bash
# run this ON the EC2 instance (via SSH) every time you want to ship
# a new commit. The CI/CD pipeline builds+pushes images to GHCR on
# every merge to main; this script just pulls the latest code + images and
# restarts the stack with minimal downtime.
set -e

cd /home/ec2-user/app
git pull origin main
docker compose -f docker-compose.hardened.yml pull
docker compose -f docker-compose.hardened.yml up -d --remove-orphans

echo "Deployed. Tailing logs (Ctrl+C to stop watching, containers keep running):"
docker compose -f docker-compose.hardened.yml logs -f --tail=50
