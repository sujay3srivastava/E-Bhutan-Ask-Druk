# 🚨 URGENT FIXES for Ask Druk Deployment Issues

Based on the nginx error logs showing "Connection refused" errors, here are the immediate fixes applied:

## 🔍 **Root Cause**
The application wasn't starting properly on port 8000, causing nginx to get connection refused errors.

## ✅ **Fixes Applied**

### 1. **Updated Procfile**
- Simplified gunicorn command
- Added proper binding to 0.0.0.0:8000
- Enabled preloading and better logging

### 2. **Fixed WSGI Configuration**
- Enhanced wsgi.py with proper path handling
- Added debugging information
- Ensured proper FastAPI application object

### 3. **Cleaned Up Nginx Configuration**
- Removed conflicting server blocks
- Fixed types_hash warnings
- Added proper upstream configuration
- Implemented comprehensive error handling

### 4. **Added Debugging Hooks**
- Pre-deployment cleanup scripts
- Post-deployment health checks
- Environment verification scripts
- Comprehensive logging

## 🚀 **Immediate Deployment Steps**

### Step 1: Deploy the Fixed Configuration
```bash
cd C:\Users\Sujay\CodingProjects\Draper_E_Bhutan
eb deploy
```

### Step 2: Monitor Deployment
```bash
# Watch deployment in real-time
eb logs --all

# Check status
eb status
eb health
```

### Step 3: Run Troubleshooting Script
```bash
# Make executable and run
chmod +x eb_troubleshoot.sh
./eb_troubleshoot.sh
```

### Step 4: Verify Functionality
```bash
# Get your EB URL
EB_URL=$(eb status | grep "CNAME" | awk '{print $2}')

# Test endpoints
curl $EB_URL/nginx-health      # Should return "Ask Druk Nginx OK"
curl $EB_URL/health           # Should return JSON health status
curl $EB_URL/emergency-contacts # Should return emergency numbers
```

## 🔧 **If Still Not Working**

### Check Application Startup
```bash
eb ssh
# Once connected:
sudo su
cd /var/app/current

# Test Python import
python -c "import application; print('✅ Import OK')"

# Check if gunicorn is running
ps aux | grep gunicorn

# Check if port 8000 is listening
netstat -tlnp | grep :8000

# Restart the application
sudo systemctl restart web
```

### Check Nginx Configuration
```bash
# Test nginx config
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# Restart nginx if needed
sudo systemctl restart nginx
```

### Check Environment Variables
```bash
eb printenv

# Ensure these are set:
# AZURE_API_KEY
# AZURE_ENDPOINT
# AZURE_API_VERSION
# AZURE_ENDPOINT_EMBEDDING
```

## 🎯 **Expected Results After Fix**

1. **Application starts successfully** on port 8000
2. **Nginx serves requests** without connection refused errors
3. **Health check works**: `curl $EB_URL/health`
4. **Emergency contacts always available**: `curl $EB_URL/emergency-contacts`
5. **Main interface loads**: `curl $EB_URL/`

## 📊 **Monitoring Commands**

```bash
# Real-time logs
eb logs --all

# Application health
eb health

# Detailed troubleshooting
./eb_troubleshoot.sh

# SSH for deep debugging
eb ssh
```

## 🔄 **Recovery Plan**

If the application still doesn't start:

1. **Check dependencies**:
   ```bash
   eb ssh
   cd /var/app/current
   pip list | grep -E "(fastapi|uvicorn|llama-index)"
   ```

2. **Test minimal startup**:
   ```bash
   # Create minimal test
   python -c "
   from fastapi import FastAPI
   app = FastAPI()
   
   @app.get('/test')
   def test():
       return {'status': 'ok'}
   
   if __name__ == '__main__':
       import uvicorn
       uvicorn.run(app, host='0.0.0.0', port=8000)
   "
   ```

3. **Check Azure OpenAI connectivity**:
   ```bash
   python -c "
   import os
   import openai
   
   client = openai.AzureOpenAI(
       api_key=os.getenv('AZURE_API_KEY'),
       api_version=os.getenv('AZURE_API_VERSION'),
       azure_endpoint=os.getenv('AZURE_ENDPOINT')
   )
   
   print('✅ Azure OpenAI client created successfully')
   "
   ```

## 🎉 **Success Indicators**

You'll know it's working when:
- ✅ No "Connection refused" errors in nginx logs
- ✅ `curl $EB_URL/health` returns JSON health status
- ✅ Application responds within 10 seconds
- ✅ Emergency contacts always available
- ✅ Chat functionality works via API

The fixes focus on ensuring the Python application starts properly and nginx can successfully proxy requests to it.
