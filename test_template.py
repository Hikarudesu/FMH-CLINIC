#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
sys.path.insert(0, r'c:\Users\franc\OneDrive\Desktop\FMH-CLINIC\FMHANIMALCLINIC')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FMHANIMALCLINIC.settings')
django.setup()

# Test template loading
try:
    from django.template import loader
    template = loader.get_template('accounts/admin_dashboard.html')
    print("✅ Template syntax is valid!")
except Exception as e:
    print(f"❌ Template error: {e}")