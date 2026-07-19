#!/usr/bin/env bash
# exit on error
set -o errexit

# Move into the Backend directory
cd Backend

# Install requirements
pip install -r requirements.txt

# Run collectstatic
python manage.py collectstatic --noinput
