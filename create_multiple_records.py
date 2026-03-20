#!/usr/bin/env python
"""Create multiple test records in the database"""
import urllib.request
import json
import time

def create_record(name, blood, allergy, condition, contact):
    """Create a single medical record"""
    
    test_data = {
        'id': f'user_{int(time.time() * 1000)}_{name.lower().replace(" ", "_")}',
        'name': name,
        'blood': blood,
        'allergy': allergy,
        'condition': condition,
        'contact': contact,
        'photo': None
    }
    
    try:
        req = urllib.request.Request(
            'http://localhost:5000/api/save-medical-data',
            data=json.dumps(test_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        
        return result['success']
    except Exception as e:
        print(f"Error creating record for {name}: {e}")
        return False

def main():
    print("="*70)
    print("CREATING MULTIPLE MEDICAL RECORDS")
    print("="*70)
    print()
    
    # List of people to create records for
    people = [
        {"name": "John Doe", "blood": "O+", "allergy": "Penicillin", "condition": "None", "contact": "555-0001"},
        {"name": "Jane Smith", "blood": "A+", "allergy": "Shellfish", "condition": "Asthma", "contact": "555-0002"},
        {"name": "Bob Johnson", "blood": "B-", "allergy": "Nuts", "condition": "Diabetes", "contact": "555-0003"},
        {"name": "Alice Williams", "blood": "AB+", "allergy": "Latex", "condition": "Hypertension", "contact": "555-0004"},
        {"name": "Mike Brown", "blood": "O-", "allergy": "None", "condition": "None", "contact": "555-0005"},
    ]
    
    success_count = 0
    
    for person in people:
        print(f"Creating record for: {person['name']}")
        print(f"  Blood: {person['blood']}")
        print(f"  Allergies: {person['allergy']}")
        print(f"  Conditions: {person['condition']}")
        
        if create_record(
            person['name'],
            person['blood'],
            person['allergy'],
            person['condition'],
            person['contact']
        ):
            print(f"  ✓ Successfully saved!")
            success_count += 1
        else:
            print(f"  ✗ Failed to save!")
        
        print()
        time.sleep(0.5)  # Small delay between requests
    
    print("="*70)
    print(f"RESULTS: {success_count}/{len(people)} records created successfully!")
    print("="*70)
    print()
    print("View all records in the dashboard:")
    print("  http://localhost:5000/dashboard.html")
    print()

if __name__ == '__main__':
    main()
