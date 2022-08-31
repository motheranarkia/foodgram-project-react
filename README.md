# Foodgram - сервис для публикации рецептов

## Технологии
* Django
* PostgresSql
* Docker-compose
* Nginx
* Workflow

## Как запустить проект:

Запуск приложения:
```
$ docker-compose up OR $ docker-compose up --build
```
Команда для выполнения миграций:
```
$ docker-compose exec web python manage.py migrate
```
Команда для заполнения базы начальными данными:
```
$ docker-compose exec web python manage.py loaddata fixtures.json 
```
## .env-файл:

```
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME=postgres
DB_PASSWORD=admin
DB_PORT=5432
DB_USER=postgres
```

