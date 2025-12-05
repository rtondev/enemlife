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

# Criar ambiente virtual
echo "Criando ambiente virtual..."
cd $PROJECT_DIR
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

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
    cp env.example .env
    echo "Por favor, edite o arquivo .env com suas configurações:"
    echo "nano .env"
    read -p "Pressione Enter após editar o .env..."
fi

# Criar diretório de logs
echo "Criando diretório de logs..."
mkdir -p logs

# Inicializar banco de dados
echo "Inicializando banco de dados..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"

# Configurar PM2
echo "Configurando PM2..."
pm2 start ecosystem.config.js
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

