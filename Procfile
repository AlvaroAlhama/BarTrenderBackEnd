% prepara el repositorio para su despliegue. 
release: sh -c 'cd barTrenderBackEnd && python manage.py migrate && python ./manage.py flush --noinput && python ./manage.py loaddata db.json'
% especifica el comando para lanzar barTrenderBackEnd
web: sh -c 'cd barTrenderBackEnd && gunicorn barTrenderBackEnd.wsgi --log-file -'