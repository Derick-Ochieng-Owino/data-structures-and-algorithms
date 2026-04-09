import base64

obfuscated_links = {
    'site': 'aHR0cHM6Ly91c2Z1bGwuaW5mby8=',
    'reg': 'aHR0cHM6Ly91c2Z1bGwuaW5mby91c2Vycy9yZWdpc3Rlci8=',
    'tor': 'aHR0cHM6Ly9nYXBzb2drM2VxZGg1eW1oaGJrbXFoeHc0eG9kMjdzM2FybzM2djZ2YnU2Y3M3Zmk2MmZvY3J5ZC5vbmlvbg==',
    'api_docs': 'aHR0cHM6Ly91c2Z1bGwuaW5mby9kb2NzLw==',
    'chat': 'aHR0cHM6Ly90Lm1lLyswOGk5c3RNZTRDRm1ObUV4',
    'admin': 'aHR0cHM6Ly90Lm1lL3VzZnVsbGluZm8=',
    'forum': 'aHR0cHM6Ly9mb3J1bS5leHBsb2l0LmluL3RvcGljLzI2Nzc5NC8='
}

for key, encoded in obfuscated_links.items():
    print(f"{key}: {base64.b64decode(encoded).decode()}")