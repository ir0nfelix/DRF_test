# Развертывание учебного API проекта на сервере

Ниже описаны шаги для развертывания проекта после пулла изменений с репозитория (например, через `git pull`).
Предполагается, что на сервере установлен `docker` и `docker-compose`. Проект будет доступен по адресу `https://api.synagentic.ru` (домен для примера).

## Шаг 1. Сборка и запуск контейнеров

Перейдите в папку с проектом и выполните:

```bash
# Останавливаем старые контейнеры (если были)
docker-compose down

# Собираем образ и поднимаем контейнеры в фоне
docker-compose up --build -d

# Применяем миграции базы данных внутри контейнера
docker-compose exec web python manage.py migrate

# Создаем начальные данные (суперюзер admin и обычный student)
docker-compose exec web python manage.py setup_initial_data

# (Опционально) Собираем статику Django (нужно для корректного отображения админки)
docker-compose exec web python manage.py collectstatic --noinput
```

## Шаг 2. Настройка Nginx

В вашем конфигурационном файле Nginx нужно добавить новый блок `server` для обработки запросов к вашему API. Само приложение в Docker "слушает" порт `8000` (как указано в `docker-compose.yml`), поэтому Nginx будет перенаправлять трафик туда.

Пример конфига, который вы прислали, уже имеет редиректы и блоки серверов. Добавьте новый домен (например, `api.synagentic.ru`) в блок перенаправления с 80 на 443 порт, а затем создайте отдельный серверный блок для него.

### Дополненный `nginx.conf`

```nginx
server {
    listen 80 default_server;
    server_name _;
    return 444;
}

server {
    listen 443 ssl default_server;
    server_name _;
    ssl_reject_handshake on;
}

server {
    listen 80;
    listen [::]:80;
    # Добавили сюда ваш API-домен для редиректа на HTTPS
    server_name n8n.synagentic.ru labs.synagentic.ru api.synagentic.ru;

    return 301 https://$host$request_uri;
}

# ... (Остальные ваши серверные блоки для n8n и labs) ...

# НОВЫЙ БЛОК: Настройка для учебного API
server {
    listen 443 ssl;
    server_name api.synagentic.ru; # Укажите ваш рабочий домен для API

    ssl_certificate     /etc/ssl/crt/synagentic.ru.crt;
    ssl_certificate_key /etc/ssl/crt/synagentic.ru.key;

    # Обработка статики Django (админка, swagger)
    # Путь /app/staticfiles нужно пробросить через volumes в docker-compose,
    # либо проксировать запросы к статике через само приложение (Whitenoise).
    # Для учебного проекта проще использовать проброс порта 8000 напрямую:

    location / {
        proxy_pass http://127.0.0.1:8000/; # Порт 8000 из docker-compose
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Шаг 3. Что добавить в проект для продакшена (если Nginx не загружает стили)

Если админка Django загружается без стилей CSS, это потому что Nginx напрямую не видит файлы статики (они внутри контейнера).
Для учебного проекта проще всего добавить пакет `whitenoise` в проект Django, чтобы он сам раздавал свою статику.

Чтобы добавить `whitenoise`:
1. `pip install whitenoise` (добавить в `requirements.txt`)
2. В `settings.py` в массив `MIDDLEWARE` добавить `'whitenoise.middleware.WhiteNoiseMiddleware',` (сразу после `SecurityMiddleware`).
3. В `settings.py` добавить `STATIC_ROOT = BASE_DIR / 'staticfiles'`
4. Сделать коммит и заново запустить `docker-compose up --build -d`.

## Шаг 4. Перезапуск Nginx

После изменения конфига проверьте синтаксис и перезапустите Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```
