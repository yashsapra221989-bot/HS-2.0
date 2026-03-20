#!/usr/bin/env python
import urllib.request
import json
import time

def test_save_with_data():
    """Test saving medical data with actual form data"""
    
    test_data = {
        'id': f'test_user_{int(time.time())}',
        'name': 'John Doe',
        'blood': 'A+',
        'allergy': 'Peanuts',
        'condition': 'Diabetes',
        'contact': '555-1234',
        'photo': None  # No photo for this test
    }
    
    print("="*60)
    print("Testing Medical Data Save")
    print("="*60)
    print(f"\nTest Data:")
    for key, value in test_data.items():
        if key != 'photo':
            print(f"  {key}: {value}")
    
    try:
        print(f"\nSending POST request to /api/save-medical-data...")
        
        req = urllib.request.Request(
            'http://localhost:5000/api/save-medical-data',
            data=json.dumps(test_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        
        print(f"✓ Save successful!")
        print(f"\nServer Response:")
        print(json.dumps(result, indent=2))
        
        # Now verify it was saved by retrieving it
        print(f"\nVerifying save by retrieving data...")
        user_id = result['user_id']
        
        response = urllib.request.urlopen(f'http://localhost:5000/api/get-medical-data/{user_id}')
        retrieved = json.loads(response.read().decode())
        
        if retrieved['success']:
            print(f"✓ Data retrieved successfully!")
            print(f"\nRetrieved Data:")
            print(f"  ID: {retrieved['id']}")
            print(f"  Name: {retrieved['name']}")
            print(f"  Blood: {retrieved['blood']}")
            print(f"  Allergies: {retrieved['allergy']}")
            print(f"  Conditions: {retrieved['condition']}")
            print(f"  Contact: {retrieved['contact']}")
            print(f"  Photo: {'Yes' if retrieved['photo'] else 'No'}")
        else:
            print(f"✗ Failed to retrieve data: {retrieved.get('error')}")
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_save_with_data()
