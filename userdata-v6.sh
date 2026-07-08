#!/bin/bash
set -e

# Update system and install Node.js
dnf update -y
dnf install -y nodejs22 git

# Clone application
cd /home/ec2-user
git clone -b lab01 https://github.com/vietaws/vietnam-local-zone.git app
cd app

# Create .env file
cat > .env <<EOF
PORT=3001
EOF

# Install dependencies
npm install
chown -R ec2-user:ec2-user /home/ec2-user/app

# Use the static-only server and index
cp -f server-v3.js server.js
cp -f public/index-v2.html public/index.html

# Create systemd service
cat > /etc/systemd/system/demo-app.service <<'EOFS'
[Unit]
Description=EC2 Instance Info Application
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/app
EnvironmentFile=/home/ec2-user/app/.env
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=demo-app
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOFS

# Enable and start service
systemctl daemon-reload
systemctl enable demo-app
systemctl start demo-app
