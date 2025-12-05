#!/bin/bash

# Script de setup para VPS Ubuntu
# Execute: chmod +x setup_vps.sh && ./setup_vps.sh

echo "=== Setup ENEMLIFE na VPS Ubuntu ==="

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
echo "Instalando Python e dependências..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y mysql-server mysql-client libmysqlclient-dev
sudo apt install -y nginx
sudo apt install -y git

# Instalar Node.js e PM2
echo "Instalando Node.js e PM2..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# Criar diretório do projeto (ajuste o caminho conforme necessário)
PROJECT_DIR="/var/www/enemlife"
echo "Criando diretório do projeto em $PROJECT_DIR..."
sudo mkdir -p $PROJECT_DIR
sudo chown -R $USER:$USER $PROJECT_DIR

echo ""
echo "=========================================="
echo "IMPORTANTE: Faça upload dos arquivos do projeto para $PROJECT_DIR"
echo "Use um dos métodos:"
echo "  1. SCP: scp -r * usuario@vps:$PROJECT_DIR/"
echo "  2. Git: git clone seu-repositorio $PROJECT_DIR"
echo "  3. SFTP/FTP: Use FileZilla ou WinSCP"
echo ""
echo "Depois de fazer upload, execute: ./deploy.sh"
echo "=========================================="
echo ""

# Verificar se os arquivos já estão lá
if [ -f "$PROJECT_DIR/app.py" ]; then
    echo "Arquivos encontrados! Continuando setup..."
    cd $PROJECT_DIR
    
    # Criar ambiente virtual
    echo "Criando ambiente virtual..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    # Instalar dependências Python
    echo "Instalando dependências Python..."
    pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "AVISO: requirements.txt não encontrado. Instalando dependências básicas..."
        pip install Flask Flask-SQLAlchemy Flask-JWT-Extended Flask-CORS Werkzeug python-dotenv bcrypt PyMySQL gunicorn
    fi
else
    echo "Arquivos do projeto não encontrados em $PROJECT_DIR"
    echo "Por favor, faça upload dos arquivos primeiro e depois execute ./deploy.sh"
    exit 1
fi

# Configurar MySQL
echo "Configurando MySQL..."
echo "Por favor, execute os seguintes comandos no MySQL:"
echo "CREATE DATABASE enemlife CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "CREATE USER 'enemlife_user'@'localhost' IDENTIFIED BY 'sua_senha_aqui';"
echo "GRANT ALL PRIVILEGES ON enemlife.* TO 'enemlife_user'@'localhost';"
echo "FLUSH PRIVILEGES;"
echo ""
read -p "Pressione Enter após configurar o MySQL..."

# Criar arquivo .env
echo "Criando arquivo .env..."
if [ ! -f .env ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "Por favor, edite o arquivo .env com suas configurações:"
        echo "nano .env"
        read -p "Pressione Enter após editar o .env..."
    else
        echo "Criando .env básico..."
        cat > .env << 'EOF'
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
EOF
        echo "Arquivo .env criado. Edite se necessário: nano .env"
    fi
fi

# Criar diretório de logs
echo "Criando diretório de logs..."
mkdir -p logs

# Inicializar banco de dados
echo "Inicializando banco de dados..."
if python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('OK')" 2>/dev/null; then
    echo "Banco de dados inicializado com sucesso!"
else
    echo "ERRO ao inicializar banco de dados. Verifique as configurações do MySQL e o arquivo .env"
    echo "Você pode tentar novamente depois com: python3 -c \"from app import app, db; app.app_context().push(); db.create_all()\""
fi

# Configurar PM2
echo "Configurando PM2..."
if [ -f "ecosystem.config.js" ]; then
    pm2 start ecosystem.config.js
else
    echo "ecosystem.config.js não encontrado. Iniciando manualmente..."
    pm2 start gunicorn --name enemlife -- \
        --bind 0.0.0.0:7000 \
        --workers 4 \
        --timeout 120 \
        --chdir $(pwd) \
        wsgi:app
fi
pm2 save
pm2 startup

echo ""
echo "=== Setup concluído! ==="
echo "Para gerenciar a aplicação:"
echo "  pm2 status          - Ver status"
echo "  pm2 logs enemlife   - Ver logs"
echo "  pm2 restart enemlife - Reiniciar"
echo "  pm2 stop enemlife   - Parar"
echo "  pm2 delete enemlife - Remover"

