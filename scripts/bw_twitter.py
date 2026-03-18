#!/usr/bin/env python3
"""BrowserWing Twitter scraper for tech daily brief"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8080"

def get_session():
    """Get SSE session from BrowserWing"""
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/mcp/sse", 
                          headers={"Accept": "text/event-stream"}, 
                          stream=True, timeout=5)
        for line in resp.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: ') and 'sessionId=' in decoded:
                    session_id = decoded.split('sessionId=')[1]
                    resp.close()
                    return session_id
        resp.close()
    except Exception as e:
        print(f"Error getting session: {e}")
    return None

def mcp_call(session_id, method, params, req_id=1):
    """Make MCP call"""
    url = f"{BASE_URL}/api/v1/mcp/sse_message?sessionId={session_id}"
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
    resp = requests.post(url, json=payload, timeout=30)
    return resp.json() if resp.text else None

def scrape_twitter_profile(username):
    """Scrape a Twitter profile"""
    print(f"\n{'='*60}")
    print(f"Scraping @{username}")
    print('='*60)
    
    session_id = get_session()
    if not session_id:
        print("❌ Failed to get session")
        return None
    
    # Initialize
    mcp_call(session_id, "initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "twitter-scrape", "version": "1.0"}
    })
    
    # Navigate to profile
    url = f"https://x.com/{username}"
    result = mcp_call(session_id, "tools/call", {
        "name": "browser_navigate",
        "arguments": {"url": url}
    }, 2)
    
    if result and 'error' not in result:
        print(f"✓ Navigated to {url}")
    else:
        print(f"❌ Navigation failed: {result}")
        return None
    
    time.sleep(2)  # Wait for page load
    
    # Get snapshot
    result = mcp_call(session_id, "tools/call", {
        "name": "browser_snapshot",
        "arguments": {}
    }, 3)
    
    if result and 'result' in result:
        content = result['result'].get('content', [])
        if content:
            text = content[0].get('text', '')
            print(f"\n--- Page Content (first 3000 chars) ---")
            print(text[:3000])
            return text
    
    print("❌ Failed to get snapshot")
    return None

if __name__ == "__main__":
    accounts = ["OpenAI", "sama", "AnthropicAI", "GoogleDeepMind", "nvidia"]
    if len(sys.argv) > 1:
        accounts = sys.argv[1:]
    
    results = {}
    for account in accounts:
        content = scrape_twitter_profile(account)
        if content:
            results[account] = content
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Scraped {len(results)}/{len(accounts)} accounts")
