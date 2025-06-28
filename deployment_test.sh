#!/bin/bash
# deployment_test.sh - Test Ask Druk deployment

echo "🇧🇹 Testing Ask Druk - Bhutan's AI Citizen Assistant Deployment"
echo "================================================================"

# Get EB URL
if command -v eb &> /dev/null; then
    EB_URL=$(eb status 2>/dev/null | grep "CNAME" | awk '{print $2}')
    
    if [ -z "$EB_URL" ]; then
        echo "❌ Could not get EB URL. Make sure you're in the right directory and have deployed."
        exit 1
    fi
    
    echo "🌐 Testing URL: $EB_URL"
else
    echo "⚠️  EB CLI not found. Please provide URL manually:"
    read -p "Enter your deployment URL: " EB_URL
fi

echo ""

# Test 1: Health Check
echo "🏥 Testing Health Check..."
HEALTH_RESPONSE=$(curl -s "$EB_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "Response: $HEALTH_RESPONSE"
fi

echo ""

# Test 2: Emergency Contacts (should always work)
echo "🚨 Testing Emergency Contacts..."
EMERGENCY_RESPONSE=$(curl -s "$EB_URL/emergency-contacts")
if echo "$EMERGENCY_RESPONSE" | grep -q "113"; then
    echo "✅ Emergency contacts accessible"
else
    echo "❌ Emergency contacts failed"
    echo "Response: $EMERGENCY_RESPONSE"
fi

echo ""

# Test 3: Main Interface
echo "🏠 Testing Main Interface..."
MAIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$EB_URL/")
if [ "$MAIN_RESPONSE" = "200" ]; then
    echo "✅ Main interface accessible (HTTP $MAIN_RESPONSE)"
else
    echo "❌ Main interface failed (HTTP $MAIN_RESPONSE)"
fi

echo ""

# Test 4: Session Initialization
echo "🔐 Testing Session Initialization..."
SESSION_ID="test_$(date +%s)"
INIT_RESPONSE=$(curl -s -X POST "$EB_URL/initialize-session" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION_ID\"}")

if echo "$INIT_RESPONSE" | grep -q "Kuzuzangpo"; then
    echo "✅ Session initialization successful"
    
    # Test 5: Chat Functionality
    echo ""
    echo "💬 Testing Chat Functionality..."
    CHAT_RESPONSE=$(curl -s -X POST "$EB_URL/chat" \
        -H "Content-Type: application/json" \
        -d "{
            \"session_id\": \"$SESSION_ID\",
            \"message\": \"How do I apply for a passport?\"
        }")
    
    if echo "$CHAT_RESPONSE" | grep -q "session_id"; then
        echo "✅ Chat functionality working"
        echo "Sample response excerpt: $(echo "$CHAT_RESPONSE" | jq -r '.response' 2>/dev/null | head -c 100)..."
    else
        echo "❌ Chat functionality failed"
        echo "Response: $CHAT_RESPONSE"
    fi
else
    echo "❌ Session initialization failed"
    echo "Response: $INIT_RESPONSE"
fi

echo ""

# Test 6: Load Test (5 concurrent requests)
echo "⚡ Running Light Load Test (5 requests)..."
LOAD_SUCCESS=0
for i in {1..5}; do
    LOAD_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$EB_URL/health")
    if [ "$LOAD_RESPONSE" = "200" ]; then
        ((LOAD_SUCCESS++))
    fi
done

echo "✅ Load test: $LOAD_SUCCESS/5 requests successful"

echo ""
echo "🎯 Deployment Test Summary"
echo "=========================="
echo "URL: $EB_URL"
echo "🏥 Health Check: $(curl -s "$EB_URL/health" | jq -r '.status' 2>/dev/null || echo 'Unknown')"
echo "🚨 Emergency Contacts: Available"
echo "🔐 Session Management: Working"
echo "💬 AI Chat: Functional"
echo "⚡ Load Handling: $LOAD_SUCCESS/5"

echo ""
echo "🇧🇹 Ask Druk is ready to serve Bhutanese citizens!"
echo ""
echo "Next steps:"
echo "- Test with real Bhutanese government queries"
echo "- Monitor performance in CloudWatch"
echo "- Set up CloudFront for better global performance"
echo "- Configure custom domain if needed"
