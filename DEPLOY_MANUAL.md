# Deploy Manual - ENEMLIFE na VPS Ubuntu

## Passo 1: Fazer Upload dos Arquivos

### Opção A: Usando SCP (do Windows PowerShell)
```powershell
# No PowerShell do Windows
cd C:\Users\rtond\OneDrive\Desktop\enempro
scp -r * root@seu-ip-vps:~/enemlife/
```

### Opção B: Usando WinSCP
1. Baixe e instale WinSCP
2. Conecte na VPS:
   - Protocolo: SFTP
   - Host: seu-ip-vps
   - Usuário: root
   - Senha: sua senha
3. Navegue até `~/enemlife` na VPS
4. Faça upload de TODOS os arquivos do projeto

## Passo 2: Conectar na VPS
```bash
ssh root@seu-ip-vps
```

## Passo 3: Navegar para o Diretório
```bash
cd ~/enemlife
```

## Passo 4: Verificar se os Arquivos Estão Lá
```bash
ls -la
# Deve mostrar: app.py, requirements.txt, wsgi.py, etc.
```

## Passo 5: Criar Ambiente Virtual Python
```bash
python3 -m venv venv
```

## Passo 6: Ativar Ambiente Virtual
```bash
source venv/bin/activate
# Você verá (venv) no início da linha
```

## Passo 7: Atualizar pip
```bash
pip install --upgrade pip
```

## Passo 8: Instalar Dependências
```bash
pip install -r requirements.txt
```

Se der erro, instale manualmente:
```bash
pip install Flask==2.3.3
pip install Flask-SQLAlchemy==3.0.5
pip install Flask-JWT-Extended==4.5.3
pip install Flask-CORS==4.0.0
pip install Werkzeug==2.3.7
pip install python-dotenv==1.0.0
pip install bcrypt==4.0.1
pip install PyMySQL==1.1.0
pip install gunicorn==21.2.0
```

## Passo 9: Verificar/Criar Arquivo .env
```bash
nano .env
```

Certifique-se de que está assim:
```
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=rtondev
DB_PASSWORD="oy1kwlf0A#1"
DB_NAME=enemlife
SECRET_KEY=sua-secret-key-aqui-2025
JWT_SECRET_KEY=sua-jwt-secret-key-aqui
FLASK_ENV=production
FLASK_DEBUG=False
```

Salve com: `Ctrl+X`, depois `Y`, depois `Enter`

## Passo 10: Criar Diretório de Logs
```bash
mkdir -p logs
```

## Passo 11: Verificar MySQL
```bash
# Verificar se MySQL está rodando
sudo systemctl status mysql

# Se não estiver, iniciar:
sudo systemctl start mysql
```

## Passo 12: Criar Banco de Dados (se ainda não criou)
```bash
sudo mysql -u root -p
```

No MySQL, execute:
```sql
CREATE DATABASE IF NOT EXISTS enemlife CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'rtondev'@'localhost' IDENTIFIED BY 'oy1kwlf0A#1';
GRANT ALL PRIVILEGES ON enemlife.* TO 'rtondev'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Passo 13: Inicializar Banco de Dados
```bash
# Certifique-se de que o ambiente virtual está ativado
source venv/bin/activate

# Inicializar tabelas
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Banco inicializado!')"
```

Se der erro, tente:
```bash
python3
```
Depois no Python:
```python
from app import app, db
app.app_context().push()
db.create_all()
exit()
```

## Passo 14: Testar se a Aplicação Funciona
```bash
# Ainda com venv ativado
gunicorn --bind 0.0.0.0:7000 --workers 2 wsgi:app
```

Se funcionar, você verá algo como:
```
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:7000
```

Pare com: `Ctrl+C`

## Passo 15: Instalar PM2 (se ainda não tiver)
```bash
npm install -g pm2
```

## Passo 16: Iniciar com PM2

### Opção A: Usando ecosystem.config.js (se tiver o arquivo)
```bash
pm2 start ecosystem.config.js
```

### Opção B: Comando direto (recomendado)
```bash
pm2 start gunicorn --name enemlife -- \
    --bind 0.0.0.0:7000 \
    --workers 4 \
    --timeout 120 \
    --chdir ~/enemlife \
    wsgi:app
```

## Passo 17: Salvar Configuração PM2
```bash
pm2 save
pm2 startup
```

O `pm2 startup` vai mostrar um comando. Execute o comando que ele mostrar.

## Passo 18: Verificar Status
```bash
pm2 status
pm2 logs enemlife
```

## Passo 19: Testar Aplicação
```bash
curl http://localhost:7000
```

Ou abra no navegador: `http://seu-ip-vps:7000`

## Comandos Úteis do PM2

```bash
pm2 status              # Ver status
pm2 logs enemlife       # Ver logs em tempo real
pm2 restart enemlife    # Reiniciar
pm2 stop enemlife       # Parar
pm2 delete enemlife    # Remover
pm2 monit               # Monitor em tempo real
```

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'app'"
```bash
# Certifique-se de estar no diretório correto
cd ~/enemlife
source venv/bin/activate
```

### Erro: "Can't connect to MySQL"
```bash
# Verificar se MySQL está rodando
sudo systemctl status mysql

# Verificar credenciais no .env
cat .env
```

### Erro: "Port 7000 already in use"
```bash
# Ver o que está usando a porta
sudo netstat -tlnp | grep 7000

# Parar processo anterior
pm2 delete enemlife
```

### Ver logs detalhados
```bash
pm2 logs enemlife --lines 100
tail -f logs/combined.log
```

### Reiniciar tudo
```bash
pm2 delete enemlife
source venv/bin/activate
pm2 start gunicorn --name enemlife -- \
    --bind 0.0.0.0:7000 \
    --workers 4 \
    --timeout 120 \
    --chdir ~/enemlife \
    wsgi:app
pm2 save
```

