#!/bin/bash
# debug_chat.sh - Debug chat functionality on EB

echo "🔍 Debugging Ask Druk Chat Functionality"
echo "========================================"

# Get EB URL
EB_URL=$(eb status 2>/dev/null | grep "CNAME" | awk '{print $2}')
if [ -z "$EB_URL" ]; then
    echo "❌ Could not get EB URL"
    exit 1
fi

echo "🌐 Testing URL: $EB_URL"
echo ""

# Test 1: Basic Health Check
echo "1️⃣ Testing Health Check..."
HEALTH_RESPONSE=$(curl -s --connect-timeout 10 "$EB_URL/health")
echo "Response: $HEALTH_RESPONSE"
echo ""

# Test 2: Session Initialization
echo "2️⃣ Testing Session Initialization..."
SESSION_ID="debug_$(date +%s)"
INIT_RESPONSE=$(curl -s -X POST "$EB_URL/initialize-session" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION_ID\"}" \
    --connect-timeout 30)

echo "Session ID: $SESSION_ID"
echo "Response: $INIT_RESPONSE"

if echo "$INIT_RESPONSE" | grep -q "error\|Error\|ERROR"; then
    echo "❌ Session initialization failed"
else
    echo "✅ Session initialization looks good"
fi
echo ""

# Test 3: Simple Chat
echo "3️⃣ Testing Chat Functionality..."
CHAT_RESPONSE=$(curl -s -X POST "$EB_URL/chat" \
    -H "Content-Type: application/json" \
    -d "{
        \"session_id\": \"$SESSION_ID\",
        \"message\": \"Hello, can you help me?\"
    }" \
    --connect-timeout 60)

echo "Chat Response: $CHAT_RESPONSE"

if echo "$CHAT_RESPONSE" | grep -q "error\|Error\|ERROR"; then
    echo "❌ Chat failed"
else
    echo "✅ Chat seems to be working"
fi
echo ""

# Test 4: Check for specific errors
echo "4️⃣ Checking for Common Issues..."

if echo "$CHAT_RESPONSE" | grep -q "knowledge base"; then
    echo "⚠️  Knowledge base issue detected"
fi

if echo "$CHAT_RESPONSE" | grep -q "Azure\|OpenAI"; then
    echo "⚠️  Azure OpenAI connection issue detected"
fi

if echo "$CHAT_RESPONSE" | grep -q "timeout\|Timeout"; then
    echo "⚠️  Timeout issue detected"
fi

echo ""
echo "🔧 SSH Commands to Debug Further:"
echo "================================="
echo "eb ssh"
echo "# Then run these commands:"
echo "cd /var/app/current"
echo "python -c \"import application; print('Import OK')\""
echo "ls -la knowledge_base/"
echo "env | grep AZURE"
echo "tail -50 /var/log/eb-engine.log"
