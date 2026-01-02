#!/bin/bash

echo "Starting SmartPharmacy Backend..."

# Create Brand table if it doesn't exist (bypass Django migrations)
python << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartpharmacy.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check if core_brand table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'core_brand'
        );
    """)
    exists = cursor.fetchone()[0]

    if not exists:
        print("Creating core_brand table...")
        cursor.execute("""
            CREATE TABLE core_brand (
                id BIGSERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                category VARCHAR(20) NOT NULL DEFAULT 'OTHER',
                is_premium BOOLEAN NOT NULL DEFAULT FALSE,
                product_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        print("core_brand table created successfully!")
    else:
        print("core_brand table already exists.")

    # Check if brand_id column exists in core_product
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = 'core_product' AND column_name = 'brand_id'
        );
    """)
    brand_col_exists = cursor.fetchone()[0]

    if not brand_col_exists:
        print("Adding brand_id column to core_product...")
        cursor.execute("""
            ALTER TABLE core_product
            ADD COLUMN brand_id BIGINT REFERENCES core_brand(id) ON DELETE SET NULL;
        """)
        print("brand_id column added successfully!")
    else:
        print("brand_id column already exists.")

print("Database setup complete!")
EOF

echo "Database setup complete. Starting gunicorn..."

# Start gunicorn
exec gunicorn --bind 0.0.0.0:8000 --workers 2 smartpharmacy.wsgi:application
