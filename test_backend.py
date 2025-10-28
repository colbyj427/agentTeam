#!/usr/bin/env python3
"""
Simple test script to verify the backend is working.
Run this after setting up your environment variables.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_backend():
    """Test basic backend functionality."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Agent Team Backend...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on localhost:8000")
        return False
    
    # Test 2: Get agents
    try:
        response = requests.get(f"{base_url}/api/agents", timeout=5)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents)} agents: {[a['name'] for a in agents]}")
        else:
            print(f"❌ Failed to get agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting agents: {e}")
        return False
    
    # Test 3: Send a test message
    try:
        test_message = {
            "content": "Hello, can you help me create a simple Python file?",
            "agent_name": "Developer"
        }
        
        response = requests.post(
            f"{base_url}/api/messages", 
            json=test_message,
            timeout=30  # Longer timeout for AI response
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Message sent successfully")
            print(f"   Agent: {result['sender']}")
            print(f"   Response: {result['content'][:100]}...")
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False
    
    print("\n🎉 All tests passed! Backend is working correctly.")
    return True

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL", 
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment.")
        return False
    
    print("✅ All required environment variables are set")
    return True

if __name__ == "__main__":
    print("Agent Team Backend Test")
    print("=" * 40)
    
    if not check_environment():
        sys.exit(1)
    
    if not test_backend():
        sys.exit(1)
