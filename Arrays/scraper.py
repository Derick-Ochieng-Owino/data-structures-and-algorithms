import requests
import csv
import time
import pandas as pd
import re
from bs4 import BeautifulSoup
from itertools import product
import os
import random
import json

# Config files
FIRSTNAMES_FILE = 'firstnames.txt'
STATES_FILE = 'states.txt'

# Your SESSION COOKIES
COOKIES = {
    'sessionid': 'e39fh79c0jsijqkt5aiiufeozwhkknlv',
    'csrftoken': 'EoV8qAopMEoyNeKUAboB3pVzEhYBMidR',
}

CSRF_TOKEN = "EoV8qAopMEoyNeKUAboB3pVzEhYBMidR"

# Auto-save settings
AUTO_SAVE_EVERY = 1000
CHECKPOINT_FILE = 'checkpoint_ssns.json'

# YEAR RANGE FOR VALID USERS (1975-2007)
MIN_YEAR = 1975
MAX_YEAR = 2007

# HUMAN-LIKE LIMITS (MAX 6s per search total)
MAX_SEARCH_TIME = 6.0  # Max 6 seconds per full search cycle
MAX_DAILY_SEARCHES = 200
MAX_HOURLY_SEARCHES = 25

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
]

def load_list(filename):
    try:
        with open(filename, 'r') as f:
            items = [line.strip() for line in f if line.strip()]
        print(f"📁 Loaded {len(items)} items from {filename}")
        return items
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []

def is_valid_dob(dob_str):
    """Check if DOB has valid month/day/year (not 00/00, year 1975-2007)"""
    if not dob_str or len(dob_str) < 8:
        return False
    
    dob_clean = re.sub(r'[^\d]', '', dob_str)
    if len(dob_clean) >= 8:
        month = dob_clean[:2]
        day = dob_clean[2:4]
        year = dob_clean[4:8] if len(dob_clean) == 8 else dob_clean[-4:]
        
        if month == "00" or day == "00":
            return False
        if not (MIN_YEAR <= int(year) <= MAX_YEAR):
            return False
            
    return True

def extract_year_from_dob(dob_str):
    """Extract year from DOB string (handles MMDDYYYY or MM-DD-YYYY)"""
    dob_clean = re.sub(r'[^\d]', '', dob_str)
    if len(dob_clean) >= 8:
        return dob_clean[-4:]
    return "0000"

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            df = pd.read_json(CHECKPOINT_FILE)
            ssns = set(df['ssn'].tolist())
            print(f"📂 Loaded checkpoint: {len(ssns):,} SSNs")
            return ssns
        except:
            print("⚠️  Checkpoint corrupt, starting fresh")
    return set()

def save_checkpoint(ssns_set, total_count):
    pd.DataFrame(list(ssns_set), columns=['ssn']).to_json(CHECKPOINT_FILE, orient='records')
    print(f"💾 Checkpoint saved: {total_count:,} unique SSNs")

def human_delay(max_time):
    """Fast human delay within max_time constraint (0.5-2s)"""
    delay = min(random.uniform(0.5, 2.0), max_time)
    time.sleep(delay)
    return delay

def check_limits(processed_today):
    """Check daily/hourly limits"""
    global search_count_today, searches_this_hour, hour_start
    
    if processed_today >= MAX_DAILY_SEARCHES:
        print("🛑 Daily limit reached. Pausing until tomorrow.")
        return False
    
    current_time = time.time()
    if current_time - hour_start > 3600:
        searches_this_hour = 0
        hour_start = current_time
    
    if searches_this_hour >= MAX_HOURLY_SEARCHES:
        wait_time = 3600 - (current_time - hour_start)
        print(f"⏳ Hourly limit. Waiting {wait_time/60:.0f}m...")
        time.sleep(wait_time)
        searches_this_hour = 0
    
    searches_this_hour += 1
    return True

def update_session_fingerprint(session):
    """Rotate browser fingerprint"""
    ua = random.choice(USER_AGENTS)
    session.headers.update({
        'User-Agent': ua,
        'Referer': 'https://usfull.info/service/get_ssndob/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })

def search_with_backoff(session, firstname, state, max_time):
    """Fast search with timeout enforcement"""
    start_time = time.time()
    max_retries = 2
    
    for attempt in range(max_retries):
        remaining_time = max_time - (time.time() - start_time)
        if remaining_time < 1.0:
            print(f"⏰ Timeout exceeded ({time.time()-start_time:.1f}s)")
            return []
        
        try:
            data = {
                'csrfmiddlewaretoken': CSRF_TOKEN,
                'firstname': firstname,
                'lastname': '',
                'st': state,
                'dob': '',
                'extended_search': 'on'
            }
            
            update_session_fingerprint(session)
            
            resp = session.post(
                'https://usfull.info/service/get_ssndob/', 
                data=data, 
                timeout=min(remaining_time, 4.0)
            )
            
            elapsed = time.time() - start_time
            if resp.status_code == 200 and elapsed < max_time:
                return parse_results(resp.text, firstname)
                
        except Exception as e:
            print(f"⚠️  Attempt {attempt+1} failed (took {time.time()-start_time:.1f}s): {e}")
        
        if attempt < max_retries - 1:
            backoff = min(0.5 + (0.5 * attempt), remaining_time * 0.3)
            time.sleep(backoff)
    
    return []

def parse_results(html_content, firstname):
    """Extract users with VALID DOB (1975-2007, no 00/00)"""
    results = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    table = soup.find('table')
    if not table:
        return results
    
    rows = table.find_all('tr')
    if len(rows) < 2:
        return results
    
    for i, row in enumerate(rows[1:], 1):
        cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
        if len(cells) >= 8:
            ssn = cells[10] if len(cells) > 10 else ''
            dob = cells[9] if len(cells) > 9 else ''
            
            if ssn and is_valid_dob(dob):
                year = extract_year_from_dob(dob)
                user_data = {
                    'firstname': cells[0] if len(cells) > 0 else '',
                    'lastname': cells[1] if len(cells) > 1 else '',
                    'middlename': cells[2] if len(cells) > 2 else '',
                    'zip': cells[4] if len(cells) > 4 else '',
                    'address': cells[5] if len(cells) > 5 else '',
                    'city': cells[6] if len(cells) > 6 else '',
                    'state': cells[7] if len(cells) > 7 else '',
                    'phone': cells[8] if len(cells) > 8 else '',
                    'dob': dob,
                    'year': year,
                    'ssn': ssn,
                    'query_name': firstname,
                    'query_state': '',
                    'row_number': i,
                    'found_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                results.append(user_data)
    
    return results

# MAIN EXECUTION
print("🚀 SSN Dumper - HUMAN SPEED (MAX 6s/search)")
FIRSTNAMES = load_list(FIRSTNAMES_FILE)
STATES = load_list(STATES_FILE)

if not FIRSTNAMES or not STATES:
    print("❌ Missing files")
    exit(1)

# Shuffle for realistic order
combinations = list(product(FIRSTNAMES, STATES))
random.shuffle(combinations)
total_combinations = len(combinations)

seen_ssns = load_checkpoint()
session = requests.Session()
session.cookies.update(COOKIES)
session.headers.update({
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded'
})

# Global limit tracking
search_count_today = 0
searches_this_hour = 0
hour_start = time.time()

all_results = []
processed = 0
new_total = 0

try:
    for firstname, state in combinations:
        search_start = time.time()
        
        if not check_limits(processed):
            break
        
        processed += 1
        print(f"\n--- [{processed:,}/{total_combinations:,}] {firstname} | {state} ---")
        
        # TIMED SEARCH (max 6s total)
        users = search_with_backoff(session, firstname, state, MAX_SEARCH_TIME)
        search_elapsed = time.time() - search_start
        
        new_hits = 0
        for user in users:
            ssn = user['ssn']
            if ssn and ssn not in seen_ssns:
                all_results.append(user)
                seen_ssns.add(ssn)
                new_hits += 1
                new_total += 1
                print(f"✅ #{new_total:,} NEW: {user['firstname']} {user['lastname'][:6]}... | {user['ssn']}")
        
        print(f"   📊 {new_hits} new (total: {len(seen_ssns):,}) | ⏱️ {search_elapsed:.1f}s")
        
        # Auto-save
        if new_total % AUTO_SAVE_EVERY == 0:
            save_checkpoint(seen_ssns, len(seen_ssns))
            pd.DataFrame(all_results).to_csv(f'checkpoint_{new_total}.csv', index=False)
            print(f"💾 AUTO-SAVED {new_total:,}!")
        
        search_count_today += 1

except KeyboardInterrupt:
    print("\n⏹️  Interrupted - saving...")

# FINAL SAVE
print("\n🔄 Final cleanup...")
unique_final = {}
for record in all_results:
    ssn = record['ssn']
    unique_final[ssn] = record

df_final = pd.DataFrame(list(unique_final.values()))
output_file = 'valid_ssn_dob_1975_2007_unique_final.csv'

if not df_final.empty:
    df_final.to_csv(output_file, index=False)
    save_checkpoint(seen_ssns, len(seen_ssns))
    
    print(f"\n🎉 FINAL: {len(df_final):,} UNIQUE VALID SSNs!")
    print(f"💾 '{output_file}'")
    print("\n📊 STATS:")
    print(f"Valid records: {len(df_final):,}")
    print(f"Avg search time: ~{MAX_SEARCH_TIME}s")
    
else:
    print("\n😞 No valid records found.")

print("\n✅ COMPLETE - Human-speed extraction finished!")