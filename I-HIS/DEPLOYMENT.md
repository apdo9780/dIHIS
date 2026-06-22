# I-HIS Deployment Guide

## Local Development Deployment

### Prerequisites
- Python 3.8+
- pip
- Git

### Steps

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd I-HIS
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

5. **Run Application**
   ```bash
   python run.py
   ```

   Access at: http://localhost:5000

## Production Deployment

### Option 1: Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Procfile**
   ```
   web: gunicorn run:app
   ```

3. **Create runtime.txt**
   ```
   python-3.10.13
   ```

4. **Deploy**
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```

### Option 2: AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Open ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and pip
   sudo apt install python3 python3-pip python3-venv -y
   
   # Install PostgreSQL
   sudo apt install postgresql postgresql-contrib -y
   ```

3. **Clone and Setup Application**
   ```bash
   git clone <repository-url>
   cd I-HIS
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

5. **Configure Nginx**
   ```bash
   sudo apt install nginx -y
   
   # Create config: /etc/nginx/sites-available/i-his
   sudo nano /etc/nginx/sites-available/i-his
   ```

6. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

7. **Enable Configuration**
   ```bash
   sudo ln -s /etc/nginx/sites-available/i-his /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

8. **Create Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/i-his.service
   ```

9. **Service Configuration**
   ```ini
   [Unit]
   Description=I-HIS Application
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/I-HIS
   ExecStart=/home/ubuntu/I-HIS/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

10. **Start Service**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable i-his
    sudo systemctl start i-his
    ```

### Option 3: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.10-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
   ```

2. **Build Image**
   ```bash
   docker build -t i-his:latest .
   ```

3. **Run Container**
   ```bash
   docker run -p 5000:5000 \
     -e FLASK_ENV=production \
     -e DATABASE_URL=postgresql://... \
     i-his:latest
   ```

## Database Migration (SQLite to PostgreSQL)

### 1. Export SQLite Data
```python
import sqlite3
import json

conn = sqlite3.connect('instance/i_his.db')
cursor = conn.cursor()

# Get all patients
cursor.execute('SELECT * FROM patients')
patients = cursor.fetchall()

# Save to JSON
with open('patients_backup.json', 'w') as f:
    json.dump(patients, f)

conn.close()
```

### 2. Setup PostgreSQL
```bash
sudo -u postgres psql

CREATE DATABASE i_his;
CREATE USER i_his_user WITH PASSWORD 'strong_password';
ALTER ROLE i_his_user SET client_encoding TO 'utf8';
ALTER ROLE i_his_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE i_his_user SET default_transaction_deferrable TO on;
ALTER ROLE i_his_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE i_his TO i_his_user;
```

### 3. Update Connection String
```bash
# In .env
DATABASE_URL=postgresql://i_his_user:strong_password@localhost/i_his
```

### 4. Initialize Database
```bash
python run.py  # This creates tables
```

## SSL/HTTPS Setup

### Using Let's Encrypt with Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y

sudo certbot certonly --nginx -d your-domain.com

# Update Nginx configuration
sudo nano /etc/nginx/sites-available/i-his
```

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring & Logging

### Application Logging
```python
import logging

logging.basicConfig(
    filename='i_his.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

### Monitor Gunicorn
```bash
# Watch process
watch ps aux | grep gunicorn

# View logs
tail -f /var/log/gunicorn/i_his.log
```

### Monitor Nginx
```bash
# Check status
sudo systemctl status nginx

# View logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## Backup & Recovery

### Database Backup (PostgreSQL)
```bash
# Backup
sudo -u postgres pg_dump i_his > backup.sql

# Restore
sudo -u postgres psql i_his < backup.sql
```

### Database Backup (SQLite)
```bash
cp instance/i_his.db instance/i_his.db.backup
```

### Complete System Backup
```bash
tar -czf i-his-backup-$(date +%Y%m%d).tar.gz /home/ubuntu/I-HIS
```

## Performance Optimization

### Enable Caching
```python
# In app/__init__.py
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

### Optimize Database Queries
```python
# Use select_in_load for relationships
from sqlalchemy.orm import selectinload

patients = Patient.query.selectinload(Patient.appointments).all()
```

### Compress Response
```bash
# Enable Gzip in Nginx
gzip on;
gzip_types text/plain text/css application/json;
```

## Security Hardening

### Update Dependencies
```bash
pip list --outdated
pip install --upgrade package-name
```

### Run Security Checks
```bash
pip install bandit
bandit -r app/
```

### Configure CORS (if needed)
```python
from flask_cors import CORS

CORS(app, origins=['trusted-domain.com'])
```

### Environment Variables
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use environment variable manager
export DATABASE_URL=postgresql://...
export SECRET_KEY=your-secret-key
```

## Troubleshooting

### Application won't start
```bash
# Check Python version
python --version

# Check dependencies
pip list

# Run with verbose logging
python run.py --verbose
```

### Database connection issues
```bash
# Test PostgreSQL connection
psql -h localhost -U i_his_user -d i_his

# Check DATABASE_URL
echo $DATABASE_URL
```

### Port already in use
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Permission issues
```bash
# Fix directory permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/I-HIS

# Fix file permissions
chmod -R 755 /home/ubuntu/I-HIS
```

## Scaling Considerations

### Horizontal Scaling
1. Load balancer (HAProxy/Nginx)
2. Multiple Gunicorn instances
3. Shared PostgreSQL database
4. Session store (Redis)

### Vertical Scaling
1. Increase EC2 instance size
2. More CPU/RAM
3. Database optimization
4. Caching layer (Redis)

## Maintenance

### Regular Updates
```bash
# Weekly
sudo apt update && sudo apt upgrade -y

# Monthly
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### Monitor Resources
```bash
# CPU and Memory
top

# Disk usage
df -h

# Database size
du -sh instance/i_his.db
```

---

**Document Version**: 1.0  
**Last Updated**: Week 1  
