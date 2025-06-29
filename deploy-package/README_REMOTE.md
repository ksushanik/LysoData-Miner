# 🚀 LysoData-Miner - Развертывание на сервере

## 📦 Содержимое пакета

- `docker-compose.hub.yml` - конфигурация Docker сервисов
- `.env` - настройки окружения  
- `deploy_hub.sh` - скрипт управления
- `README_REMOTE.md` - эта инструкция

## ⚡ Быстрый запуск (30 секунд)

```bash
# 1. Отредактируйте настройки (ОБЯЗАТЕЛЬНО!)
vi .env

# 2. Запустите систему
./deploy_hub.sh
```

## 🔧 Обязательные настройки в .env

Перед запуском ОБЯЗАТЕЛЬНО измените:

```bash
# Поменяйте пароль базы данных!
POSTGRES_PASSWORD=ваш_надежный_пароль

# Проверьте порты (если заняты - измените)
DB_PORT=5434        # PostgreSQL
BACKEND_PORT=8000   # API 
WEB_PORT=3000      # Веб-интерфейс
PGADMIN_PORT=8080  # Админка БД
```

## 🌐 После запуска доступно

- **Веб-интерфейс**: http://ваш-сервер:3000
- **API**: http://ваш-сервер:8000
- **Документация API**: http://ваш-сервер:8000/docs
- **Админка БД**: http://ваш-сервер:8080

## 🎛️ Команды управления

```bash
./deploy_hub.sh status    # Статус
./deploy_hub.sh logs      # Логи  
./deploy_hub.sh restart   # Перезапуск
./deploy_hub.sh stop      # Остановка
./deploy_hub.sh pull      # Обновление
```

## 🛡️ Безопасность для продакшн

1. **Измените пароли** в .env
2. **Настройте firewall**:
   ```bash
   ufw allow 3000  # Веб-интерфейс
   ufw allow 8000  # API
   # НЕ открывайте 5434 (база данных)
   ```
3. **Используйте HTTPS** (Nginx/Cloudflare)

## 🚨 Если что-то не работает

```bash
# Проверить логи
./deploy_hub.sh logs

# Проверить порты
netstat -tuln | grep -E "(3000|8000|5434)"

# Полная переустановка
./deploy_hub.sh clean
./deploy_hub.sh start
```

## 📊 Проверка работы

```bash
# API health check
curl http://localhost:8000/api/health/

# Веб-интерфейс
curl http://localhost:3000
```

---

**🎉 Готово!** LysoData-Miner развернут и готов к работе.

📧 Поддержка: создайте issue в GitHub проекта 