#!/bin/bash
set -e

DB_ENDPOINT=10.10.x.y # TODO: MUST BE UPDATED
DB_PASSWORD=demoPassword
DB_NAME="demo"
DB_USER="dbadmin"

# Update system and install Node.js
dnf update -y
dnf install -y nodejs22 git postgresql17

# Clone application
cd /home/ec2-user
git clone -b lab01 https://github.com/vietaws/vietnam-local-zone.git app
cd app

# Create .env file (update DB_ENDPOINT with your actual Private IP Adddress of Local Zone Database Instance)
cat > .env <<EOF
DB_HOST=${DB_ENDPOINT}
DB_PORT=5432
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
PORT=80
EOF

# Install dependencies
npm install
chown -R ec2-user:ec2-user /home/ec2-user/app
mv server-v2.js server.js

# Create systemd service
cat > /etc/systemd/system/demo-app.service <<'EOFS'
[Unit]
Description=Inventory Management Application
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
