# Elastic Beanstalk Deployment Guide for Ask Druk - Bhutan's AI Citizen Assistant

This guide covers deploying Ask Druk to AWS Elastic Beanstalk with optimized configuration for AI-powered government services.

## 🎯 **Deployment Architecture**

```
Application Load Balancer (AWS ALB)
                │
        ┌───────▼───────┐
        │  Nginx Proxy  │ ← Session-based routing for chat continuity
        │   (EB Host)    │
        └───────┬───────┘
                │
    ┌───────────▼──────────┐
    │   Gunicorn Master    │
    └─┬──────────────────┬─┘
      │                  │
   Worker1            Worker2 ← 2 workers optimized for AI processing
```

## 📁 **EB Configuration Files**

### **Key Files Created:**
- `wsgi.py` - WSGI entry point for Elastic Beanstalk
- `Procfile` - Process configuration with optimized worker settings
- `.ebextensions/01_druk_application.config` - Basic app configuration
- `.ebextensions/02_druk_routing.config` - Session-based routing for chat continuity
- `.platform/nginx/conf.d/proxy.conf` - Advanced nginx configuration

## 🚀 **Deployment Steps**

### **1. Prerequisites**
```bash
# Install EB CLI if needed
pip install awsebcli

# Ensure you have AWS credentials configured
aws configure
```

### **2. Environment Variables Setup**
Set these environment variables in Elastic Beanstalk:

```bash
eb setenv AZURE_API_KEY="your_azure_openai_key" \
         AZURE_ENDPOINT="https://your-resource.openai.azure.com/" \
         AZURE_API_VERSION="2024-08-01-preview" \
         AZURE_ENDPOINT_EMBEDDING="https://your-embedding-resource.openai.azure.com/" \
         FLASK_ENV="production" \
         PYTHONPATH="/var/app/current"
```

### **3. Initialize EB Application**
```bash
# Navigate to project directory
cd C:\Users\Sujay\CodingProjects\Draper_E_Bhutan

# Initialize EB (first time only)
eb init
# Select: Python 3.11
# Choose your preferred region
# Application name: ask-druk-bhutan-ai
```

### **4. Create Environment**
```bash
# Create production environment
eb create druk-production --instance-type t3.medium

# Or create development environment
eb create druk-dev --instance-type t3.small
```

### **5. Deploy Application**
```bash
# Deploy to existing environment
eb deploy

# Monitor deployment status
eb status
```

## 🔧 **Configuration Details**

### **Worker Configuration**
- **2 Gunicorn workers** optimized for AI processing
- **2 threads per worker** for concurrent request handling
- **300-second timeout** for AI response generation
- **Uvicorn worker class** for FastAPI compatibility

### **Session Routing**
- Session-based load balancing for chat continuity
- Consistent hashing based on `session_id`
- Fallback to round-robin for stateless requests

### **File Upload Support**
- **100MB max body size** for document uploads
- Extended timeouts for document processing
- Proper error handling for large files

### **Bhutan-Specific Features**
- Emergency contacts always available (even during downtime)
- Cultural branding in error pages
- Optimized for Bhutanese government services

## 📊 **Monitoring & Health Checks**

### **Health Endpoints**
```bash
# Get your EB URL
EB_URL=$(eb status | grep "CNAME" | awk '{print $2}')

# Test application health
curl $EB_URL/health

# Test emergency contacts (always available)
curl $EB_URL/emergency-contacts

# Test chat functionality
curl -X POST $EB_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "message": "How do I apply for a passport?"
  }'
```

### **View Logs**
```bash
# View all logs
eb logs

# Follow logs in real-time
eb logs --all

# SSH into instance for detailed debugging
eb ssh
sudo tail -f /var/log/gunicorn-error.log
sudo tail -f /var/log/gunicorn-access.log
```

## ⚙️ **Instance Configuration**

### **Recommended Instance Types**
- **t3.small**: 2 vCPU, 2GB RAM (development/testing)
- **t3.medium**: 2 vCPU, 4GB RAM (production recommended)
- **t3.large**: 2 vCPU, 8GB RAM (high load)

### **Auto Scaling Configuration**
```bash
eb config

# Add to configuration:
# AutoScalingGroup:
#   MinSize: 1
#   MaxSize: 3
#   DesiredCapacity: 1
# 
# Triggers:
#   - MeasureName: CPUUtilization
#     Statistic: Average
#     Unit: Percent
#     UpperThreshold: 75
#     LowerThreshold: 25
```

## 🔍 **Testing Deployment**

### **Functional Tests**
```bash
# Test main interface
curl $EB_URL/

# Test admin interface
curl $EB_URL/admin

# Test chat with session continuity
SESSION_ID="test_$(date +%s)"
curl -X POST $EB_URL/initialize-session \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\"}"

curl -X POST $EB_URL/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"message\": \"What documents do I need for a driving license?\"
  }"
```

### **Load Testing**
```bash
# Simple load test
for i in {1..10}; do
  curl -s $EB_URL/health > /dev/null && echo "Request $i: OK" || echo "Request $i: FAILED"
done
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Application won't start**
```bash
# Check logs for errors
eb logs | grep "ERROR"

# Verify environment variables
eb printenv

# Check if all dependencies are installed
eb ssh
/opt/python/run/venv/bin/pip list | grep llama-index
```

#### **2. AI responses timing out**
```bash
# Check worker processes
eb ssh
ps aux | grep gunicorn

# Monitor resource usage
top -p $(pgrep gunicorn)
```

#### **3. Knowledge base not loading**
```bash
# Check knowledge base files
eb ssh
ls -la /var/app/current/knowledge_base/

# Verify file permissions
sudo chown -R webapp:webapp /var/app/current/knowledge_base/
```

#### **4. Session routing not working**
```bash
# Check nginx configuration
eb ssh
sudo nginx -t
sudo cat /etc/nginx/conf.d/session_routing.conf
```

## 🎯 **Production Optimization**

### **Performance Tuning**
1. **Enable CloudFront** for static file caching
2. **Configure RDS** for persistent chat sessions (if needed)
3. **Set up ElastiCache** for session storage
4. **Enable CloudWatch** monitoring

### **Security Configuration**
```bash
# Set secure environment variables
eb setenv FLASK_ENV="production" \
         DEBUG="False" \
         SECURE_SSL_REDIRECT="True"
```

### **Backup Strategy**
- Regular snapshots of EB environment
- Backup of knowledge base files
- Version control for all configuration

## 🎉 **Deployment Success**

Your Ask Druk application is now deployed with:

✅ **AI-optimized infrastructure** for government service assistance  
✅ **Session-based routing** for continuous conversations  
✅ **Bhutan-specific error handling** with cultural sensitivity  
✅ **Emergency contact failsafe** always available  
✅ **Auto-scaling capability** for varying citizen demand  
✅ **Comprehensive monitoring** for reliability  

## 🔄 **Update Workflow**

```bash
# Make changes to code or knowledge base
git add .
git commit -m "Update Bhutan knowledge base"

# Deploy updates
eb deploy

# Verify deployment
eb status
curl $(eb status | grep "CNAME" | awk '{print $2}')/health
```

Perfect for serving Bhutan's citizens with reliable, AI-powered government assistance! 🇧🇹🤖
