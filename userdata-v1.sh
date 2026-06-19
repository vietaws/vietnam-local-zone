#!/bin/bash

# Update system
dnf update -y

# Install simple http server to serve the React app
dnf install httpd -y

# Create a Simple static file on webserver
echo "Hello World from AWS!" > /var/www/html/index.html

# Start the httpd service
systemctl start httpd
systemctl enable httpd
