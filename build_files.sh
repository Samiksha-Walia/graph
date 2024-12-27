#!/bin/bash

echo "BUILD START"

# Install dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt || exit 1

# Collect static files
python3 manage.py collectstatic --noinput --clear || exit 1

echo "BUILD END"
