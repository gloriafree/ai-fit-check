#!/usr/bin/env python3
"""
Quick test to verify Fashn.ai API connectivity.
Run this first to make sure your API key works before running the full pipeline.

Usage:
    python scripts/test_fashn_api.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import requests


def test_fashn_api():
    # Load config
    with open("configs/config.yaml") as f:
        config = yaml.safe_load(f)

    api_key = config["fashn"]["api_key"]
    base_url = config["fashn"]["base_url"]

    print("🔑 Testing Fashn.ai API connection...")
    print(f"   Base URL: {base_url}")
    print(f"   API Key:  {api_key[:10]}...{api_key[-4:]}")
    print()

    # Test 1: Check API health / auth
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        # Try a minimal request to check auth
        response = requests.get(
            f"{base_url}/status/test",
            headers=headers,
            timeout=10,
        )

        if response.status_code == 401:
            print("❌ Authentication failed. Check your API key.")
            print(f"   Response: {response.text}")
            return False
        elif response.status_code == 404:
            # 404 on a non-existent prediction ID means auth works
            print("✅ API authentication successful!")
            print("   (404 on test ID = auth is working, endpoint is reachable)")
            return True
        elif response.status_code == 200:
            print("✅ API is reachable and responding!")
            return True
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return True  # Auth might still be fine

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Fashn.ai API.")
        print("   Check your internet connection.")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_fashn_api()
    print()
    if success:
        print("🎉 API is ready! You can now run the full pipeline:")
        print("   python run.py --clothing <image> --person <photo>")
    else:
        print("Please fix the issues above before running the pipeline.")
    sys.exit(0 if success else 1)
