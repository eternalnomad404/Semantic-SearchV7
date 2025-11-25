#!/bin/bash

# EC2 Setup Script - Run this on your EC2 instance
# This script installs Docker and sets up the environment

set -e

echo "🚀 Setting up EC2 instance for Semantic Search API..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo amazon-linux-extras install docker -y

# Start Docker service
echo "▶️ Starting Docker service..."
sudo service docker start

# Add current user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -a -G docker $USER

# Enable Docker to start on boot
echo "🔄 Enabling Docker auto-start..."
sudo chkconfig docker on

# Install docker-compose
echo "🔧 Installing docker-compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
echo "📁 Creating application directory..."
mkdir -p ~/semantic-search-api
cd ~/semantic-search-api

# Install curl for health checks
echo "🌐 Installing curl..."
sudo yum install curl -y

# Configure firewall (if needed)
echo "🔥 Configuring firewall..."
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

echo ""
echo "✅ EC2 setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Log out and log back in (for docker group to take effect)"
echo "2. Transfer your Docker image: scp semantic-search-api.tar.gz ec2-user@this-ip:~/"
echo "3. Load and run: gunzip -c semantic-search-api.tar.gz | docker load"
echo "4. Start container: docker run -d -p 8000:8000 --name semantic-search --restart unless-stopped semantic-search-api:latest"
echo ""
echo "🔗 Your API will be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8000"
