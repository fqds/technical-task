В приложении используются python3.9 и django4.1
# Инструкция по установке:
1) Клонируем репозиторий и создаем в папке с ним виртуальное окружение `python -m venv venv`
2) Заходим в виртуальное окружение и устанавливаем необходимые библиотеки `pip install -r requirements.txt`
3) Создаем базу данных `create database test_db'`, пользователя `create user django;` и выдаем права пользователю `grant all privileges on database test_db to django;`. Данные по умолчанию в репозитории: 
```
DB_NAME = "test_db"
DB_USER = "django"
DB_PASSWORD = "password"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
4) Выполняем команду `python manage.py migrate`
5) В siteMain/settings.py присваиваем переменной  `TELEGRAM_ID` значение, равное айди вашего телеграмм аккаунта
6) Запускаем сервер `python manage.py runserver`
