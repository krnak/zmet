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
pip install poetry
poetry install
poetry shell
gunicorn zmet:app
```

then connect to the `localhost:8000`

## vps settings

```bash
ufw allow 22/tcp
ufw reload
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_id.pub
```

```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload
pacman -S nginx
```

```conf
cat /etc/nginx/nginx.conf
http {
    ...
    include sites-enabled/*;
}
```

```conf
cat /etc/nginx/sites-enabled/zmet.krnak.cz.conf
server {
    server_name  zmet.krnak.cz;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

```bash
pacman -S certbot certbot-nginx
certbot --nginx
systemctl start nginx.service
```
