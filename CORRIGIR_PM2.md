# Corrigir Erro PM2 - ENEMLIFE

## Problema
O PM2 está tentando executar o gunicorn como Node.js, causando erro.

## Solução Rápida

Execute estes comandos na VPS:

```bash
cd ~/enemlife

# Parar o processo atual
pm2 delete enemlife

# Opção 1: Usar script shell (RECOMENDADO)
chmod +x start.sh
pm2 start start.sh --name enemlife

# OU Opção 2: Usar caminho completo do gunicorn
pm2 start ./venv/bin/gunicorn --name enemlife -- \
    --bind 0.0.0.0:7000 \
    --workers 4 \
    --timeout 120 \
    --chdir /root/enemlife \
    wsgi:app

# Salvar
pm2 save

# Verificar
pm2 status
pm2 logs enemlife
```

## Solução Alternativa (usando ecosystem.config.js)

Se preferir usar o ecosystem.config.js:

```bash
cd ~/enemlife

# Parar processo atual
pm2 delete enemlife

# Editar ecosystem.config.js (já está corrigido)
# Agora iniciar
pm2 start ecosystem.config.js

# Salvar
pm2 save
```

## Verificar se está funcionando

```bash
pm2 status
pm2 logs enemlife --lines 50
curl http://localhost:7000
```

