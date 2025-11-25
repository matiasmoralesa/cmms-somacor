#!/usr/bin/env python
"""
Script to check inventory data in the database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.inventory.models import SparePart

def check_inventory():
    """Check inventory data"""
    print("=" * 60)
    print("CHECKING INVENTORY DATA")
    print("=" * 60)
    
    spare_parts = SparePart.objects.all()
    count = spare_parts.count()
    
    print(f"\nTotal Spare Parts: {count}")
    
    if count > 0:
        print("\nFirst 10 spare parts:")
        print("-" * 60)
        for part in spare_parts[:10]:
            print(f"ID: {part.id}")
            print(f"Part Number: {part.part_number}")
            print(f"Name: {part.name}")
            print(f"Category: {part.category}")
            print(f"Quantity: {part.quantity}")
            print(f"Minimum Stock: {part.minimum_stock}")
            print(f"Unit Cost: ${part.unit_cost}")
            print(f"Location: {part.location}")
            print("-" * 60)
    else:
        print("\n⚠️  No spare parts found in database!")
        print("Run: python manage.py load_demo_data")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_inventory()
