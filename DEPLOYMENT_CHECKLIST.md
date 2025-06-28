# Ask Druk - Elastic Beanstalk Deployment Checklist

## Pre-Deployment Checklist ✅

### 1. Environment Setup
- [ ] AWS CLI configured with proper credentials
- [ ] EB CLI installed (`pip install awsebcli`)
- [ ] Azure OpenAI credentials ready
- [ ] Knowledge base files verified and corrected

### 2. Code Preparation
- [ ] All corrected knowledge base files in place
- [ ] `.env.template` created with required variables
- [ ] Static files in `/static` directory
- [ ] Dependencies in `requirements.txt` verified

### 3. EB Configuration Files Created
- [ ] `wsgi.py` - WSGI entry point
- [ ] `Procfile` - Process configuration
- [ ] `.ebextensions/01_druk_application.config` - Basic app config
- [ ] `.ebextensions/02_druk_routing.config` - Session routing
- [ ] `.platform/nginx/conf.d/proxy.conf` - Nginx configuration

## Deployment Steps 🚀

### Step 1: Initialize EB Application
```bash
cd C:\Users\Sujay\CodingProjects\Draper_E_Bhutan
eb init
```
**Choose:**
- Platform: Python 3.11
- Region: Your preferred AWS region
- Application name: `ask-druk-bhutan-ai`

### Step 2: Set Environment Variables
```bash
eb setenv AZURE_API_KEY="your_azure_openai_key" \
         AZURE_ENDPOINT="https://your-resource.openai.azure.com/" \
         AZURE_API_VERSION="2024-08-01-preview" \
         AZURE_ENDPOINT_EMBEDDING="https://your-embedding-resource.openai.azure.com/" \
         FLASK_ENV="production" \
         PYTHONPATH="/var/app/current"
```

### Step 3: Create Environment
```bash
# Production environment
eb create druk-production --instance-type t3.medium

# Development environment (optional)
eb create druk-dev --instance-type t3.small
```

### Step 4: Deploy Application
```bash
eb deploy
```

### Step 5: Verify Deployment
```bash
eb status
eb health
./deployment_test.sh  # Run our test script
```

## Post-Deployment Verification ✅

### 1. Core Functionality Tests
- [ ] Health endpoint responds: `/health`
- [ ] Main interface loads: `/`
- [ ] Emergency contacts work: `/emergency-contacts`
- [ ] Session initialization works
- [ ] Chat responses are generated
- [ ] Knowledge base queries return accurate info

### 2. Performance Tests
- [ ] Response times under 10 seconds for chat
- [ ] Concurrent request handling
- [ ] File upload functionality (if applicable)
- [ ] Session continuity across requests

### 3. Error Handling Tests
- [ ] Graceful error pages during downtime
- [ ] Emergency contacts always available
- [ ] Proper error messages for invalid requests
- [ ] Timeout handling for long AI operations

## Monitoring Setup 📊

### 1. CloudWatch Monitoring
- [ ] Enable enhanced monitoring
- [ ] Set up alarms for:
  - High CPU usage (>80%)
  - High memory usage (>85%)
  - High response times (>15 seconds)
  - Error rates (>5%)

### 2. Log Management
- [ ] Configure log retention
- [ ] Set up log streaming to CloudWatch
- [ ] Monitor application logs for errors

### 3. Health Monitoring
- [ ] Configure health check URL: `/health`
- [ ] Set appropriate health check timeout
- [ ] Monitor deployment health in EB console

## Production Optimization 🎯

### 1. Performance Optimization
- [ ] Enable CloudFront for static content
- [ ] Configure auto-scaling rules
- [ ] Optimize instance types based on usage
- [ ] Enable load balancing if using multiple instances

### 2. Security Configuration
- [ ] Enable HTTPS redirect
- [ ] Configure security groups
- [ ] Set up WAF rules if needed
- [ ] Secure environment variable storage

### 3. Backup and Recovery
- [ ] Schedule EB environment snapshots
- [ ] Backup knowledge base files
- [ ] Document disaster recovery procedures
- [ ] Test recovery procedures

## Troubleshooting Guide 🔧

### Common Issues and Solutions

#### Application Won't Start
```bash
# Check logs
eb logs | grep ERROR

# Verify environment variables
eb printenv

# Check dependencies
eb ssh
pip list | grep llama-index
```

#### Slow Response Times
```bash
# Monitor resource usage
eb ssh
top
htop

# Check worker processes
ps aux | grep gunicorn
```

#### Session Routing Issues
```bash
# Check nginx configuration
eb ssh
sudo nginx -t
sudo systemctl reload nginx
```

#### Knowledge Base Not Loading
```bash
# Verify file structure
eb ssh
ls -la /var/app/current/knowledge_base/
```

## Success Metrics 📈

### Performance Targets
- **Response Time:** < 10 seconds for chat queries
- **Availability:** > 99.5% uptime
- **Error Rate:** < 2% of requests
- **Concurrent Users:** Support 50+ simultaneous sessions

### User Experience Targets
- **Cultural Accuracy:** Bhutanese context preserved
- **Emergency Access:** Always available fallback
- **Session Continuity:** Conversations persist across requests
- **Knowledge Accuracy:** Updated information from verified sources

## Maintenance Schedule 🗓️

### Weekly Tasks
- [ ] Review application logs
- [ ] Check performance metrics
- [ ] Monitor error rates
- [ ] Verify knowledge base accuracy

### Monthly Tasks
- [ ] Update dependencies
- [ ] Review and update knowledge base
- [ ] Performance optimization review
- [ ] Security patch assessment

### Quarterly Tasks
- [ ] Full disaster recovery test
- [ ] Capacity planning review
- [ ] User feedback analysis
- [ ] Knowledge base comprehensive update

---

## Emergency Contacts for Technical Issues 🆘

**Always Available Emergency Numbers (Built into App):**
- Police: 113
- Fire: 110  
- Medical: 112
- Traffic: 111
- Disaster: 999

**Technical Support:**
- AWS Support (if configured)
- Development Team Contact
- Azure OpenAI Support (for AI issues)

---

## Deployment Complete! 🎉

Once all items are checked, your Ask Druk application will be:

✅ **Deployed on AWS Elastic Beanstalk**  
✅ **Optimized for AI-powered government services**  
✅ **Configured with session continuity**  
✅ **Equipped with emergency failsafes**  
✅ **Ready to serve Bhutanese citizens**  

Your AI assistant is now ready to help citizens navigate government services with accurate, culturally-appropriate responses! 🇧🇹🤖
