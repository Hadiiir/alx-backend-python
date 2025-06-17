#!/bin/bash

echo "=== Docker Setup Verification ==="

# 1. Check Requirements.txt
echo -e "\n[1/4] Checking requirements.txt..."
if [ -s "messaging_app/requirements.txt" ]; then
    echo "✅ requirements.txt exists and is not empty"
else
    echo "❌ requirements.txt missing or empty"
    exit 1
fi

# 2. Check Dockerfile existence
echo -e "\n[2/4] Checking Dockerfile..."
if [ -s "messaging_app/Dockerfile" ]; then
    echo "✅ Dockerfile exists and is not empty"
else
    echo "❌ Dockerfile missing or empty"
    exit 1
fi

# 3. Check Python 3.10 base image
echo -e "\n[3/4] Checking Python version..."
if grep -q "python:3.10" messaging_app/Dockerfile; then
    echo "✅ Correct Python 3.10 base image found"
else
    echo "❌ Python 3.10 base image missing"
    exit 1
fi

# 4. Check port exposure and dependencies
echo -e "\n[4/4] Checking configurations..."
if grep -q "EXPOSE 8000" messaging_app/Dockerfile; then
    echo "✅ Port 8000 properly exposed"
else
    echo "❌ Port 8000 not exposed"
fi

if grep -q "pip install -r requirements.txt" messaging_app/Dockerfile; then
    echo "✅ Dependencies installation configured"
else
    echo "❌ Missing dependencies installation"
fi

echo -e "\nVerification complete!"