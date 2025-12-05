# Comandos Rápidos - Deploy ENEMLIFE

## Situação Atual
Você já tem:
- ✅ MySQL instalado
- ✅ Node.js e PM2 instalados
- ✅ Python instalado
- ✅ Arquivo .env criado com suas credenciais
- ✅ Diretório ~/enemlife criado

## O que falta: Fazer upload dos arquivos do projeto

### Opção 1: Usando SCP (do seu computador Windows)

No PowerShell do seu computador Windows:
```powershell
cd C:\Users\rtond\OneDrive\Desktop\enempro
scp -r * root@seu-ip-vps:~/enemlife/
```

### Opção 2: Usando WinSCP ou FileZilla
1. Baixe WinSCP ou FileZilla
2. Conecte na VPS (SFTP)
3. Navegue até ~/enemlife
4. Faça upload de TODOS os arquivos do projeto

### Opção 3: Usando Git (se tiver repositório)
```bash
cd ~/enemlife
git clone https://seu-repositorio.git .
```

## Depois do upload, na VPS execute:

```bash
cd ~/enemlife
chmod +x deploy.sh
./deploy.sh
```

## Se der erro, execute manualmente:

```bash
cd ~/enemlife

# Criar/ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretório de logs
mkdir -p logs

# Inicializar banco
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Iniciar com PM2
pm2 start gunicorn --name enemlife -- \
    --bind 0.0.0.0:7000 \
    --workers 4 \
    --timeout 120 \
    wsgi:app

pm2 save
pm2 startup
```

## Verificar se está funcionando:

```bash
pm2 status
pm2 logs enemlife
curl http://localhost:7000
```

