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
- [x] pages
- [ ] gallery

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
}
```

```bash
pacman -S certbot certbot-nginx
certbot --nginx
systemctl start nginx.service
```
add
```conf
cat /etc/nginx/sites-enabled/zmet.krnak.cz.conf
...
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
...
```

# access tokens

ucet pro kazdeho -> group notes , share by ^@user ^group

```python
H = lambda x: b64_urlsafe_encode(sha256(x)[:15])
tokens_secret = H(b"/tokens?sk=" + app_secret)
purpose = b"view" | b"edit" | b"admin"
token = H(b"note/" + note_id.encode() + b"/" + <purpose> + tokens_secret)

pasw_secret = H(b"passwords?sk=" + app_secret)
user_password = H(b"password?user=" + user_name + b"&sk=" + pasw_secret)
```
