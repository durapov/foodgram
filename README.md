![workflows](https://github.com/durapov/foodgram/actions/workflows/main.yml/badge.svg)

# Foodgram — социальная сеть для размещения информации о рецептах

проект доступен здесь http://62.84.122.208:8000/

### Функции

* Регистрация пользователей.
* Добавить/редактировать/удалить информацию о рецепте

# Использованные технологии.

- [![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=cd5c5c)](https://www.python.org/)
- [![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=344CC7)](https://www.djangoproject.com/)
  [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=38761D)](https://www.django-rest-framework.org/)
- [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=0095b6)](https://www.postgresql.org/)
- [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=FF9900)](https://nginx.org/ru/)
  [![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=344CC7)](https://gunicorn.org/)
- [![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=38761D)](https://www.docker.com/)
  [![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=0095b6)](https://www.docker.com/)
  [![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=FF9900)](https://www.docker.com/products/docker-hub)
- [![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=cd5c5c)](https://github.com/features/actions)

## Как развернуть проект на удаленном сервере

#### 1. Форкнуть репозиторий и настроить в нем переменные окружения в окне Actions secrets and variables:

- ALLOWED_HOSTS: список хостов/доменов (через запятую без пробелов)
- DB_HOST: IP базы данных, или имя контейнера, где запущен сервер БД
- DB_PORT: порт, по которому Django будет обращаться к базе данных
- DOCKER_PASSWORD: пароль от вашего докер аккаунта
- DOCKER_USERNAME: username вашего докер аккаунта
- HOST: IP-адрес вашего сервера
- POSTGRES_DB: название БД
- POSTGRES_PASSWORD: пароль от БД
- POSTGRES_USER: логин БД
- SSH_KEY: содержимое закрытого ключа SSH для доступа к серверу
- SSH_PASSPHRASE: passphrase для доступа к серверу
- TELEGRAM_TO: ID вашего телеграм-аккаунта
- TELEGRAM_TOKEN: токен вашего телеграм-бота
- USER: ваше имя пользователя на сервере

#### 2. На удаленном сервере:

- установить Docker
- создать директорию проекта /kittygram
- в директории проекта разместить файл docker-compose.production.yml из папки infra
- в директории проекта создать файл .env с переменными окружения, которые указаны в файле .env.example (переменные
  описаны выше в пункте 1)

#### 3. Клонировать форкнутый репозиторий на локальный компьютер.

#### 4. Запуск проекта при пуше в Github (в ветку main).

Проект пройдёт встроенные тесты, создадутся необходимые файлы на сервере в директории ~/kittygram, будут запущены
необходимые контейнеры

## Автор

#### Dmitry Durapov

(на основе https://github.com/yandex-praktikum/foodgram)

для разработки
********
Находясь в папке infra, выполните команду docker-compose up.
При выполнении этой команды контейнер frontend,
описанный в docker-compose.yml, подготовит файлы,
необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения,
а по адресу http://localhost/api/docs/ — спецификацию API.

