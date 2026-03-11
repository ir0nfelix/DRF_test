#!/bin/bash
echo "1. Getting tokens..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login/ -H "Content-Type: application/json" -d '{"username": "student", "password": "student"}')
ACCESS=$(echo $RESPONSE | grep -o '"access":"[^"]*' | cut -d'"' -f4)
REFRESH=$(echo $RESPONSE | grep -o '"refresh":"[^"]*' | cut -d'"' -f4)

echo "Access Token: $ACCESS"
echo "Refresh Token: $REFRESH"

echo "\n2. Testing protected endpoint WITH access token..."
curl -s -X GET http://127.0.0.1:8000/api/v1/protected_users/ -H "Authorization: JWT $ACCESS"

echo "\n\n3. Logging out (Blacklisting Refresh Token)..."
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/logout/ -H "Content-Type: application/json" -d "{\"refresh\": \"$REFRESH\"}"

echo "\n\n4. Trying to use blacklisted Refresh Token to get new access token..."
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/jwt/refresh/ -H "Content-Type: application/json" -d "{\"refresh\": \"$REFRESH\"}"

echo "\n\n5. Trying protected endpoint again WITH the original access token..."
curl -s -X GET http://127.0.0.1:8000/api/v1/protected_users/ -H "Authorization: JWT $ACCESS"
echo ""
