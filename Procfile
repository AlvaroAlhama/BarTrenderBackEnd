% prepara el repositorio para su despliegue. 
release: sh -c 'cd barTrenderBackEnd && python manage.py flush --noinput && python manage.py migrate && python ./manage.py loaddata db.json'
web: sh -c 'cd barTrenderBackEnd && gunicorn barTrenderBackEnd.wsgi --log-file -'
