# Inventory Management Application

Simple inventory management system built with Node.js, Express, and PostgreSQL Database.

## Features
- Add new products with name and quantity
- Edit existing products
- Delete products
- View all products in inventory
- Responsive design

## Prerequisites
- PostgreSQL instance
- Amazon EC2 instance (application server)
- Node.js 22

## Database Setup

### 1. Create PostgreSQL Instance

- Engine: PostgreSQL
- Instance class: `R7i.large`
- Database name: `demo`
- Master username: `dbadmin`
- Master password: `demoPassword`
- VPC: Same as application EC2
- Subnet group: Private subnets
- Security group: Allow port 5432 from application security group
- Public access: No

### 2. Products Table

Connect to Postgres using psql or any PostgreSQL client:

```bash
psql -h <psql-endpoint> -U dbadmin -d demo

INSERT INTO products (name, price, quantity) VALUES
  ('Laptop', 999.99, 10),
  ('Mouse', 29.99, 50),
  ('Keyboard', 79.99, 30);
```

Fix Authentication
```sh
# Edit the postgresql.conf and postgresql file:
sudo vi /var/lib/pgsql/data/postgresql.conf

Find and change: 

listen_addresses = 'localhost'

To:

listen_addresses = '*'

# Edit the pg_hba.conf and postgresql file:
sudo vi /var/lib/pgsql/data/pg_hba.conf

Add this line before other rules (for local connections):

host    demo    dbadmin    127.0.0.1/32    md5

For remote connections from specific IP:

host    demo    dbadmin    10.0.0.0/16    md5

Or for any IP (less secure):

host    demo    dbadmin    0.0.0.0/0    md5

# Restart psql
sudo systemctl restart postgresql
```


## Application Deployment

### 1. Launch Application EC2 Instance

- Name: `demo-app`
- Type: `C7i.large`
- Subnet: Public
- Security group: Allow port 80 and outbound to DB port 5432
- IAM Instance Profile: `ec2-instance-role`

### 2. Install Dependencies

```bash
sudo dnf update -y
sudo dnf install -y nodejs22 git postgresql17
```

### 3. Clone Application

```bash
cd /home/ec2-user
git clone -b lab01 https://github.com/vietaws/vietnam-local-zone.git app
cd app
```

### 4. Install Node Modules

```bash
npm install
sudo chown -R ec2-user:ec2-user /home/ec2-user/app
```

### 6. Test Database Connection From Application

```bash
psql -h <db-endpoint> -U dbadmin -d demo
```

### 7. View Logs

```bash
# Real-time logs
sudo journalctl -u demo-app -f

# Recent logs
sudo journalctl -u demo-app -n 50
```

## Automated Deployment with User Data

Use the provided `userdata-v3.sh` script when launching EC2 instances. Make sure to update the DB endpoint in the script before use.
