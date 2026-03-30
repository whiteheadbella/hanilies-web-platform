web: sh -c 'python manage.py migrate --noinput && gunicorn hanilies_cakeshoppe_event.wsgi:application --bind 0.0.0.0:$PORT --access-logfile - --error-logfile - --log-level info --capture-output'
