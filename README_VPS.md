# Setup ENEMLIFE na VPS Ubuntu

## Pré-requisitos
- VPS Ubuntu 20.04 ou superior
- Acesso root ou sudo
- Domínio configurado (opcional)

## Passo a Passo

### 1. Conectar na VPS
```bash
ssh usuario@seu-ip-vps
```

### 2. Executar o script de setup
```bash
chmod +x setup_vps.sh
./setup_vps.sh
```

### 3. Configurar MySQL

Entre no MySQL:
```bash
sudo mysql -u root -p
```

Execute os comandos:
```sql
CREATE DATABASE enemlife CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'enemlife_user'@'localhost' IDENTIFIED BY 'sua_senha_segura';
GRANT ALL PRIVILEGES ON enemlife.* TO 'enemlife_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Configurar variáveis de ambiente

Copie o arquivo de exemplo e edite:
```bash
cp env.example .env
nano .env
```

Configure:
```
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=enemlife_user
DB_PASSWORD=sua_senha_segura
DB_NAME=enemlife
SECRET_KEY=gerar-uma-chave-secreta-aleatoria-aqui
JWT_SECRET_KEY=gerar-outra-chave-secreta-aleatoria-aqui
```

### 5. Inicializar banco de dados

```bash
source venv/bin/activate
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. Iniciar com PM2

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 7. Comandos úteis do PM2

```bash
pm2 status              # Ver status da aplicação
pm2 logs enemlife       # Ver logs em tempo real
pm2 restart enemlife    # Reiniciar aplicação
pm2 stop enemlife      # Parar aplicação
pm2 delete enemlife    # Remover da lista do PM2
pm2 monit              # Monitor em tempo real
```

### 8. Configurar Nginx (Opcional)

Crie o arquivo de configuração:
```bash
sudo nano /etc/nginx/sites-available/enemlife
```

Adicione:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:7000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ativar site:
```bash
sudo ln -s /etc/nginx/sites-available/enemlife /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Configurar SSL com Let's Encrypt (Opcional)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

## Atualizar aplicação

```bash
cd /var/www/enemlife
git pull
source venv/bin/activate
pip install -r requirements.txt
pm2 restart enemlife
```

## Troubleshooting

### Ver logs
```bash
pm2 logs enemlife
tail -f logs/combined.log
```

### Verificar MySQL
```bash
sudo systemctl status mysql
sudo mysql -u enemlife_user -p enemlife
```

### Verificar porta
```bash
sudo netstat -tlnp | grep 7000
```

