module.exports = {
  apps: [{
    name: 'enemlife',
    script: './venv/bin/gunicorn',
    args: '--bind 0.0.0.0:7000 --workers 4 --timeout 120 wsgi:app',
    cwd: '/root/enemlife',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      DB_TYPE: 'mysql',
      DB_HOST: 'localhost',
      DB_PORT: '3306',
      DB_USER: 'rtondev',
      DB_PASSWORD: 'oy1kwlf0A#1',
      DB_NAME: 'enemlife',
      SECRET_KEY: 'sua-secret-key-aqui',
      JWT_SECRET_KEY: 'sua-jwt-secret-key-aqui'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
}

