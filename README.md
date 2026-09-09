# Planetarium API

API service for planetarium management written on DRF

## Installation using GitHub

``` bash
git clone <repository-url>
cd Planetarium

cp .env.sample .env

docker compose up --build
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