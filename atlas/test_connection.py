#!/usr/bin/env python3
"""
Test Connection Script for robot_gui.py
=======================================

This script tests if the robot_gui.py server is accessible from other devices.
Run this script from another computer or device to verify connectivity.
"""

import requests
import socket
import sys
import time

def test_connection(host, port=8080):
    """Test connection to robot_gui.py server"""
    
    print(f"🔍 Testing connection to {host}:{port}")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        # Create socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("   ✅ Port is open and accessible")
        else:
            print("   ❌ Port is not accessible")
            return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Test 2: HTTP API endpoint
    print("2. Testing HTTP API endpoint...")
    try:
        url = f"http://{host}:{port}/api/status"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("   ✅ API endpoint responds correctly")
            print(f"   📄 Response: {response.text[:100]}...")
        else:
            print(f"   ❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection refused - server may not be running")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout - server may be slow")
        return False
    except Exception as e:
        print(f"   ❌ HTTP request error: {e}")
        return False
    
    # Test 3: CORS headers
    print("3. Testing CORS headers...")
    try:
        url = f"http://{host}:{port}/api/status"
        response = requests.options(url, timeout=10)
        
        cors_headers = response.headers.get('Access-Control-Allow-Origin')
        if cors_headers:
            print("   ✅ CORS headers present")
        else:
            print("   ⚠️  CORS headers not found (may cause issues with mobile app)")
    except Exception as e:
        print(f"   ⚠️  Could not test CORS: {e}")
    
    print("=" * 50)
    print("🎯 Connection test completed successfully!")
    return True

def main():
    """Main function"""
    print("🤖 Robot GUI Connection Test")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <IP_ADDRESS> [PORT]")
        print("Example: python test_connection.py 10.136.166.163 8080")
        print("\nMake sure robot_gui.py is running before testing!")
        return
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    print(f"Target: {host}:{port}")
    print("Make sure robot_gui.py is running and the server is started!")
    print()
    
    # Test connection
    success = test_connection(host, port)
    
    if success:
        print("\n✅ SUCCESS: robot_gui.py is accessible from this device!")
        print("You can now use the mobile app to connect.")
    else:
        print("\n❌ FAILED: Cannot connect to robot_gui.py")
        print("\nTroubleshooting steps:")
        print("1. Make sure robot_gui.py is running")
        print("2. Check that the server is started (tab '📱 Mobile App')")
        print("3. Verify the IP address is correct")
        print("4. Check firewall settings")
        print("5. Ensure both devices are on the same network")

if __name__ == "__main__":
    main()
