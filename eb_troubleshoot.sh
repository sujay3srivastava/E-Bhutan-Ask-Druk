#!/bin/bash
# eb_troubleshoot.sh - Quick troubleshooting for Ask Druk deployment

echo "🇧🇹 Ask Druk - Deployment Troubleshooting"
echo "=========================================="

# Function to run command and show result
run_check() {
    echo "🔍 $1"
    echo "----------------------------------------"
    eval "$2"
    echo ""
}

# Basic checks
run_check "Check EB Status" "eb status"
run_check "Check Application Health" "eb health"

# Get EB URL
EB_URL=$(eb status 2>/dev/null | grep "CNAME" | awk '{print $2}')
if [ -z "$EB_URL" ]; then
    echo "❌ Could not get EB URL"
    exit 1
fi

echo "🌐 Testing URL: $EB_URL"
echo ""

# Test endpoints
run_check "Test Nginx Health" "curl -s --connect-timeout 10 $EB_URL/nginx-health || echo 'Failed to connect'"
run_check "Test Application Health" "curl -s --connect-timeout 10 $EB_URL/health || echo 'Failed to connect'"
run_check "Test Emergency Contacts" "curl -s --connect-timeout 10 $EB_URL/emergency-contacts | head -c 200"

# SSH into instance for detailed checks
echo "🔧 Running detailed checks on EB instance..."
eb ssh --command "
echo '=== PROCESS CHECK ==='
ps aux | grep -E '(gunicorn|python|nginx)' | grep -v grep

echo '=== PORT CHECK ==='
netstat -tlnp | grep -E ':80|:8000'

echo '=== NGINX STATUS ==='
systemctl status nginx --no-pager -l

echo '=== NGINX CONFIG TEST ==='
nginx -t

echo '=== APPLICATION LOGS (last 20 lines) ==='
tail -20 /var/log/eb-engine.log

echo '=== GUNICORN LOGS (if exists) ==='
if [ -f /var/log/gunicorn-error.log ]; then
    tail -20 /var/log/gunicorn-error.log
else
    echo 'No gunicorn error log found'
fi

echo '=== TEST LOCAL CONNECTION ==='
curl -s --connect-timeout 5 http://127.0.0.1:8000/health || echo 'Local connection failed'

echo '=== ENVIRONMENT VARIABLES ==='
env | grep -E '(AZURE|PYTHON|PORT)' | head -5

echo '=== DISK SPACE ==='
df -h

echo '=== MEMORY USAGE ==='
free -h
"

echo ""
echo "🎯 Quick Fixes to Try:"
echo "======================"
echo "1. If app not responding: eb deploy --staged"
echo "2. If nginx errors: eb ssh then 'sudo systemctl restart nginx'"
echo "3. If dependency issues: Check requirements.txt and eb logs"
echo "4. If timeout issues: Check Azure OpenAI credentials"
echo ""
echo "📋 Full logs command: eb logs --all"
echo "🔄 Redeploy command: eb deploy"
