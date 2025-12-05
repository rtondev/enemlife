# Guia Rápido de Deploy - ENEMLIFE

## Passo 1: Enviar arquivos para a VPS

### Opção A: Usando SCP (do seu computador local)
```bash
# Navegue até a pasta do projeto no seu computador
cd C:\Users\rtond\OneDrive\Desktop\enempro

# Envie todos os arquivos para a VPS
scp -r * root@seu-ip-vps:/var/www/enemlife/
# ou
scp -r * root@seu-ip-vps:~/enemlife/
```

### Opção B: Usando Git (recomendado)
```bash
# Na VPS
cd /var/www
git clone https://seu-repositorio.git enemlife
cd enemlife
```

### Opção C: Usando SFTP/FTP
Use um cliente como FileZilla ou WinSCP para fazer upload dos arquivos.

## Passo 2: Conectar na VPS
```bash
ssh root@seu-ip-vps
```

## Passo 3: Navegar para o diretório do projeto
```bash
cd /var/www/enemlife
# ou
cd ~/enemlife
```

## Passo 4: Verificar se os arquivos estão lá
```bash
ls -la
# Deve mostrar: app.py, requirements.txt, wsgi.py, ecosystem.config.js, etc.
```

## Passo 5: Executar o script de deploy
```bash
chmod +x deploy.sh
./deploy.sh
```

## Passo 6: Verificar se está funcionando
```bash
# Ver status
pm2 status

# Ver logs
pm2 logs enemlife

# Testar se a aplicação está respondendo
curl http://localhost:7000
```

## Se algo der errado

### Verificar logs
```bash
pm2 logs enemlife --lines 50
```

### Verificar se a porta está aberta
```bash
sudo netstat -tlnp | grep 7000
```

### Reiniciar aplicação
```bash
pm2 restart enemlife
```

### Reinstalar dependências
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Configurar Nginx (opcional - para usar domínio)

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

Ativar:
```bash
sudo ln -s /etc/nginx/sites-available/enemlife /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

