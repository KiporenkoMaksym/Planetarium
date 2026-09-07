# Planetarium API

API service for planetarium management written on DRF

## Installation using GitHub

``` bash
git clone 
cd Planetarium
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
set DB_HOST=<db>
set DB_NAME=<planetarium>
set DB_USER=<postgres>
set DB_PASSWORD=<postgres>
set SECRET_KEY=<django-insecure-$%)n4*)n$w$95g7sb-3bi9zhqw2m^ahc)mgex4go9v)1uh_u79>
python app_service/manage.py migrate
python app_service/manage.py runserver
```

## Run with docker
Docker should be installed

```bash
docker-compose build
docker-compose up
```

## Getting access
 - create user via /api/user/register/

 - get access token via /api/token/

## Features
 - JWT authenticated
 - Admin panel /admin/
 - Documentation is located at /api/doc/swagger/ 
 - Managing reservation and tickets 
 - Creating astronomy shows with show themes 
 - Creating planetarium domes 
 - Adding astronomy show session 
 - Filtering astronomy shows and show sessions