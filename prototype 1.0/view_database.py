import sqlite3
from datetime import datetime
import os

def view_all_records():
    """View all medical records from the database"""
    
    # Check if database exists
    if not os.path.exists('medical_data.db'):
        print("❌ Database file not found! Run server.py first to create it.")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect('medical_data.db')
        c = conn.cursor()
        
        # Get all records
        c.execute("SELECT * FROM medical_records")
        records = c.fetchall()
        
        print(f"\n{'='*100}")
        print(f"📊 MEDICAL RECORDS DATABASE")
        print(f"{'='*100}")
        print(f"Total Records: {len(records)}\n")
        
        if len(records) == 0:
            print("⚠️  No records found in database yet.")
            print("    Fill out the form and generate a QR code to add data.\n")
        else:
            for i, record in enumerate(records, 1):
                print(f"\n{'─'*100}")
                print(f"Record #{i}")
                print(f"{'─'*100}")
                print(f"  ID:                  {record[0]}")
                print(f"  Name:                {record[1]}")
                print(f"  Blood Type:          {record[2]}")
                print(f"  Allergies:           {record[3]}")
                print(f"  Medical Conditions:  {record[4]}")
                print(f"  Emergency Contact:   {record[5]}")
                print(f"  Photo Stored:        {'✓ Yes' if record[6] else '✗ No'}")
                print(f"  Created:             {record[7]}")
                print(f"  Last Updated:        {record[8]}")
        
        print(f"\n{'='*100}\n")
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def search_by_name(name):
    """Search for a specific person by name"""
    
    if not os.path.exists('medical_data.db'):
        print("❌ Database file not found!")
        return
    
    try:
        conn = sqlite3.connect('medical_data.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM medical_records WHERE name LIKE ?", (f"%{name}%",))
        records = c.fetchall()
        
        print(f"\n{'='*100}")
        print(f"🔍 SEARCH RESULTS FOR: '{name}'")
        print(f"{'='*100}")
        
        if len(records) == 0:
            print(f"No records found for '{name}'")
        else:
            for record in records:
                print(f"\n  ID:                  {record[0]}")
                print(f"  Name:                {record[1]}")
                print(f"  Blood Type:          {record[2]}")
                print(f"  Allergies:           {record[3]}")
                print(f"  Medical Conditions:  {record[4]}")
                print(f"  Emergency Contact:   {record[5]}")
                print(f"  Last Updated:        {record[8]}")
        
        print(f"\n{'='*100}\n")
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

def get_record_count():
    """Get total number of records"""
    
    if not os.path.exists('medical_data.db'):
        print("❌ Database file not found!")
        return 0
    
    try:
        conn = sqlite3.connect('medical_data.db')
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM medical_records")
        count = c.fetchone()[0]
        conn.close()
        
        return count
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return 0

def export_to_csv(filename='exported_data.csv'):
    """Export all records to CSV file"""
    
    if not os.path.exists('medical_data.db'):
        print("❌ Database file not found!")
        return
    
    try:
        import csv
        
        conn = sqlite3.connect('medical_data.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM medical_records")
        records = c.fetchall()
        
        if len(records) == 0:
            print("⚠️  No records to export!")
            return
        
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow(['ID', 'Name', 'Blood Type', 'Allergies', 'Conditions', 
                           'Emergency Contact', 'Photo', 'Created', 'Updated'])
            # Write records
            writer.writerows(records)
        
        print(f"✅ Successfully exported {len(records)} records to '{filename}'")
        conn.close()
        
    except Exception as e:
        print(f"❌ Export error: {e}")

def delete_record(user_id):
    """Delete a specific record by ID"""
    
    if not os.path.exists('medical_data.db'):
        print("❌ Database file not found!")
        return
    
    try:
        conn = sqlite3.connect('medical_data.db')
        c = conn.cursor()
        
        # Check if record exists
        c.execute("SELECT name FROM medical_records WHERE id = ?", (user_id,))
        record = c.fetchone()
        
        if not record:
            print(f"❌ Record with ID '{user_id}' not found!")
            return
        
        # Delete record
        c.execute("DELETE FROM medical_records WHERE id = ?", (user_id,))
        conn.commit()
        
        print(f"✅ Successfully deleted record for '{record[0]}'")
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    print("\n" + "="*100)
    print("🏥 MEDICAL DATABASE VIEWER")
    print("="*100)
    
    while True:
        print("\nOptions:")
        print("  1. View all records")
        print("  2. Search by name")
        print("  3. Get record count")
        print("  4. Export to CSV")
        print("  5. Delete a record")
        print("  0. Exit")
        
        choice = input("\nSelect an option (0-5): ").strip()
        
        if choice == "0":
            print("\n✅ Goodbye!\n")
            break
        
        elif choice == "1":
            view_all_records()
        
        elif choice == "2":
            name = input("Enter name to search: ").strip()
            if name:
                search_by_name(name)
            else:
                print("❌ Please enter a name!")
        
        elif choice == "3":
            count = get_record_count()
            print(f"\n📊 Total records in database: {count}\n")
        
        elif choice == "4":
            filename = input("Enter filename (default: exported_data.csv): ").strip()
            if not filename:
                filename = "exported_data.csv"
            export_to_csv(filename)
        
        elif choice == "5":
            user_id = input("Enter user ID to delete: ").strip()
            if user_id:
                confirm = input(f"⚠️  Are you sure? (yes/no): ").strip().lower()
                if confirm == "yes":
                    delete_record(user_id)
                else:
                    print("❌ Cancelled.")
            else:
                print("❌ Please enter a user ID!")
        
        else:
            print("❌ Invalid option! Please select 0-5.")
