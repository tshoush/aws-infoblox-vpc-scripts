#!/bin/bash
# Container setup script for Ubuntu WSL
# This script installs Docker CE without Docker Desktop

set -e

echo "Container Setup Script for Ubuntu WSL"
echo "===================================="

# Update system
echo -e "\n[1/7] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install prerequisites
echo -e "\n[2/7] Installing prerequisites..."
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common

# Add Docker GPG key
echo -e "\n[3/7] Adding Docker GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo -e "\n[4/7] Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
echo -e "\n[5/7] Installing Docker..."
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add current user to docker group
echo -e "\n[6/7] Configuring Docker permissions..."
sudo usermod -aG docker $USER

# Start Docker service
echo -e "\n[7/7] Starting Docker service..."
sudo service docker start

# Create docker daemon config for better performance
echo -e "\nConfiguring Docker daemon..."
sudo mkdir -p /etc/docker
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Test Docker installation
echo -e "\nTesting Docker installation..."
sudo docker run hello-world

echo -e "\n✅ Docker installation complete!"
echo "⚠️  Please logout and login again for group permissions to take effect."
echo "   Or run: newgrp docker"
echo -e "\nTo start Docker automatically, add to ~/.bashrc:"
echo "   sudo service docker start"