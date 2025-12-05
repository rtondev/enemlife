#!/bin/bash

# Script simplificado para deploy na VPS
# Execute este script APÓS fazer upload dos arquivos do projeto

echo "=== Deploy ENEMLIFE ==="

# Verificar se estamos no diretório correto
if [ ! -f "app.py" ]; then
    echo "ERRO: app.py não encontrado!"
    echo "Certifique-se de estar no diretório do projeto (/var/www/enemlife ou ~/enemlife)"
    exit 1
fi

# Ativar ambiente virtual
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "Instalando dependências Python..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "ERRO: requirements.txt não encontrado!"
    exit 1
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo "Criando .env a partir de env.example..."
        cp env.example .env
        echo "IMPORTANTE: Edite o arquivo .env com suas configurações:"
        echo "nano .env"
        read -p "Pressione Enter após editar o .env..."
    else
        echo "AVISO: Arquivo .env não encontrado. Criando um básico..."
        cat > .env << EOF
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=rtondev
DB_PASSWORD="oy1kwlf0A#1"
DB_NAME=enemlife
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
FLASK_DEBUG=False
EOF
    fi
fi

# Criar diretório de logs
echo "Criando diretório de logs..."
mkdir -p logs

# Inicializar banco de dados
echo "Inicializando banco de dados..."
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Banco de dados inicializado!')"

# Verificar PM2
if ! command -v pm2 &> /dev/null; then
    echo "PM2 não encontrado. Instalando..."
    npm install -g pm2
fi

# Parar aplicação se já estiver rodando
pm2 delete enemlife 2>/dev/null || true

# Iniciar com PM2
echo "Iniciando aplicação com PM2..."
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

# Salvar configuração PM2
pm2 save

echo ""
echo "=== Deploy concluído! ==="
echo ""
echo "Status da aplicação:"
pm2 status
echo ""
echo "Para ver os logs:"
echo "  pm2 logs enemlife"
echo ""
echo "Para reiniciar:"
echo "  pm2 restart enemlife"

