#!/usr/bin/env python3
"""
Test chatbot with proper session management
"""

import requests
import json

def test_chatbot_fixed():
    """Test chatbot with fixed session management"""
    base_url = "http://localhost:5002"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        print("🧪 Testing Fixed Chatbot Session Management...")
        
        # Test 1: Start conversation
        print("\n1. Starting conversation...")
        start_response = session.post(f"{base_url}/api/chatbot/start", json={
            "vehicle_price": "30000",
            "vehicle_name": "2024 Toyota Camry"
        })
        
        if start_response.status_code == 200:
            start_data = start_response.json()
            print("✅ Conversation started")
            print(f"   Question: {start_data.get('question', 'N/A')[:50]}...")
        else:
            print(f"❌ Failed to start: {start_response.status_code}")
            return False
        
        # Test 2: Respond to income question
        print("\n2. Responding to income question...")
        respond_response = session.post(f"{base_url}/api/chatbot/respond", json={
            "response": "85k"
        })
        
        if respond_response.status_code == 200:
            respond_data = respond_response.json()
            print("✅ Response processed")
            if respond_data.get('type') == 'question':
                print(f"   Next question: {respond_data.get('question', 'N/A')[:50]}...")
            elif respond_data.get('type') == 'validation_error':
                print(f"   Validation error: {respond_data.get('error_message', 'N/A')}")
            else:
                print(f"   Response type: {respond_data.get('type')}")
        else:
            print(f"❌ Failed to respond: {respond_response.status_code}")
            return False
        
        # Test 3: Respond to credit score question
        print("\n3. Responding to credit score question...")
        respond_response = session.post(f"{base_url}/api/chatbot/respond", json={
            "response": "700"
        })
        
        if respond_response.status_code == 200:
            respond_data = respond_response.json()
            print("✅ Response processed")
            if respond_data.get('type') == 'question':
                print(f"   Next question: {respond_data.get('question', 'N/A')[:50]}...")
            elif respond_data.get('type') == 'validation_error':
                print(f"   Validation error: {respond_data.get('error_message', 'N/A')}")
            else:
                print(f"   Response type: {respond_data.get('type')}")
        else:
            print(f"❌ Failed to respond: {respond_response.status_code}")
            return False
        
        print("\n🎉 Session management test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_chatbot_fixed()
    if success:
        print("\n✅ Chatbot session management is now working!")
    else:
        print("\n❌ There are still issues with session management.")
