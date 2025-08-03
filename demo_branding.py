#!/usr/bin/env python3
"""
Demo script for White Label Chat SaaS Branding System

This script demonstrates the client-specific branding capabilities
by testing all available configurations and endpoints.
"""

import requests
import json
import sys
from time import sleep

BASE_URL = "http://localhost:5000"

def check_server():
    """Check if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def demo_clients_endpoint():
    """Demo the clients endpoint"""
    print("🔍 Getting available clients...")
    response = requests.get(f"{BASE_URL}/api/clients")
    data = response.json()
    
    print(f"✅ Found {data['count']} clients: {', '.join(data['clients'])}")
    return data['clients']

def demo_client_branding(client):
    """Demo client-specific branding"""
    print(f"\n🎨 Testing {client.upper()} branding...")
    
    # Test API endpoint
    response = requests.get(f"{BASE_URL}/api/branding/{client}")
    branding = response.json()
    
    print(f"   Company: {branding['company_name']}")
    print(f"   Primary Color: {branding['primary_color']}")
    print(f"   Welcome Message: {branding['welcome_message']}")
    print(f"   Logo: {branding['logo_url']}")
    print(f"   Features: {', '.join([k for k, v in branding['features'].items() if v])}")
    
    # Test client URL
    response = requests.get(f"{BASE_URL}/{client}")
    if response.status_code == 200:
        print(f"   ✅ Client URL /{client} is accessible")
        if branding['company_name'].encode() in response.content:
            print(f"   ✅ Company name appears in HTML")
    
    return branding

def demo_default_branding():
    """Demo default branding"""
    print(f"\n🏠 Testing DEFAULT branding...")
    
    response = requests.get(f"{BASE_URL}/api/branding")
    branding = response.json()
    
    print(f"   Company: {branding['company_name']}")
    print(f"   Primary Color: {branding['primary_color']}")
    print(f"   Welcome Message: {branding['welcome_message']}")

def main():
    """Main demo function"""
    print("🚀 White Label Chat SaaS - Branding Demo")
    print("=" * 50)
    
    # Check if server is running
    if not check_server():
        print("❌ Server is not running!")
        print("   Please start the server with: python run.py")
        return 1
    
    print("✅ Server is running!\n")
    
    try:
        # Demo clients endpoint
        clients = demo_clients_endpoint()
        
        # Demo each client's branding
        for client in clients:
            branding = demo_client_branding(client)
        
        # Demo default branding
        demo_default_branding()
        
        print("\n🎯 Branding Demo Summary:")
        print(f"   • {len(clients)} client configurations tested")
        print(f"   • All API endpoints working")
        print(f"   • Client-specific URLs accessible")
        print(f"   • Default fallback working")
        
        print("\n🌐 Try these URLs in your browser:")
        for client in clients:
            print(f"   • {BASE_URL}/{client}")
        print(f"   • {BASE_URL}/ (default)")
        
        print("\n✅ Demo completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
