#!/bin/bash
# Script to run Django migrations

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Migrations completed successfully!"
