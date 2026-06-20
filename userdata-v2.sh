#!/bin/bash
set -e

DB_NAME="demo"
DB_USER="dbadmin"
DB_PASSWORD="demoPassword"
TABLE_NAME="products"

# Logging to Amazon EC2 by using Session Manager
dnf update -y

# Initialize database
dnf install postgresql17-server -y
sudo postgresql-setup --initdb

systemctl start postgresql
systemctl enable postgresql


# Create db and table
sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';"
sudo -u postgres createdb -O ${DB_USER} ${DB_NAME}
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"


# Create table
sudo -u postgres psql -d ${DB_NAME} -c "
CREATE TABLE ${TABLE_NAME} (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  price DECIMAL(10, 2),
  quantity INTEGER DEFAULT 0
);"

sudo -u postgres psql -d ${DB_NAME} -c "
  GRANT ALL ON SCHEMA public TO ${DB_USER};
  
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_USER};
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO ${DB_USER};
  
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DB_USER};
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO ${DB_USER};
"



# Config Authentication
sed -i 's/local   all             all                                     peer/local   all     all                                     scram-sha-256/g' /var/lib/pgsql/data/pg_hba.conf
sed -i 's/host    all             all             127.0.0.1\/32            ident/host    all             all             127.0.0.1\/32            scram-sha-256/g' /var/lib/pgsql/data/pg_hba.conf
sed -i 's/host    all             all             ::1\/128                 ident/host    all             all             ::1\/128                 scram-sha-256/g' /var/lib/pgsql/data/pg_hba.conf

echo "host    all             all             0.0.0.0/0               scram-sha-256"

systemctl restart postgresql