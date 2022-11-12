# Změť

google keep based personal knowledge database

## Features

- [x] authentization
- [x] csrf protection
- [x] bookmarks
- [x] redirections
- [x] labels
- [x] wall
- [x] search
- [x] images

## Run

```bash
poetry install
poetry shell
gunicorn zmet:app
```

then connect to the `localhost:8000`

## nginx

```conf
cat /etc/nginx/sites-enabled/zmet.krnak.cz.conf
# ZMET
server {
    server_name  zmet.krnak.cz;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

```bash
sudo certbot --nginx
sudo systemctl start nginx.service
```
