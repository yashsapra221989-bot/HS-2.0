#!/usr/bin/env python
import urllib.request
import json

try:
    response = urllib.request.urlopen('http://localhost:5000/api/all-records')
    data = json.loads(response.read().decode())
    print('✓ API Working!')
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f'✗ Error: {e}')
