web: python manage.py collectstatic --noinput && gunicorn fusion_force.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile -
release: python manage.py migrate --noinput