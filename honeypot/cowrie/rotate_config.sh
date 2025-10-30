#!/bin/bash
# Script to rotate honeypot configurations
# This simulates diversity to avoid detection

set -e

HONEYPOT_DIR="/home/runner/work/project-asylum/project-asylum/honeypot/cowrie"
CONFIG_FILE="$HONEYPOT_DIR/cowrie.cfg"
USERDB_FILE="$HONEYPOT_DIR/userdb.txt"

# Array of hostnames to rotate
HOSTNAMES=(
    "server-01"
    "web-server-prod"
    "db-master"
    "api-gateway"
    "backup-server"
    "mail-relay"
)

# Array of SSH versions
SSH_VERSIONS=(
    "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"
    "SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2"
    "SSH-2.0-OpenSSH_8.4p1 Ubuntu-6ubuntu2"
    "SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.7"
)

# Select random configurations
RANDOM_HOSTNAME=${HOSTNAMES[$RANDOM % ${#HOSTNAMES[@]}]}
RANDOM_SSH_VERSION=${SSH_VERSIONS[$RANDOM % ${#SSH_VERSIONS[@]}]}

echo "Rotating honeypot configuration..."
echo "New hostname: $RANDOM_HOSTNAME"
echo "New SSH version: $RANDOM_SSH_VERSION"

# Update configuration (in production, use sed or config management tool)
# For now, just log the rotation
echo "[$(date)] Rotated to hostname=$RANDOM_HOSTNAME ssh_version=$RANDOM_SSH_VERSION" >> "$HONEYPOT_DIR/rotation.log"

# In production, restart containers with new configuration
# docker-compose restart cowrie

echo "Configuration rotation complete"
