# 🚀 LysoData-Miner: Быстрое развертывание с Docker Hub

## ✨ Что создано

Создана полная система развертывания LysoData-Miner с использованием готовых образов Docker Hub:

### 📦 Файлы системы

1. **docker-compose.hub.yml** - Конфигурация сервисов для Docker Hub
2. **env.hub.example** - Шаблон конфигурации окружения  
3. **scripts/build_and_push.sh** - Сборка и публикация образов
4. **scripts/deploy_hub.sh** - Развертывание системы
5. **Makefile.hub** - Управление через make команды
6. **DOCKER_HUB_DEPLOYMENT.md** - Полная документация

### 🐳 Docker Hub образы

- **gimmyhat/lysodata-backend** - FastAPI backend + PostgreSQL драйвер
- **gimmyhat/lysodata-frontend** - React + Nginx  

## 🎯 Преимущества подхода

✅ **Упрощение развертывания** - только 3 файла на сервере
✅ **Быстрота** - нет сборки на месте
✅ **Консистентность** - одинаковые образы везде
✅ **Версионирование** - легкое переключение версий
✅ **Автоинициализация** - база данных настраивается автоматически

## ⚡ Сценарии использования

### Сценарий 1: Разработчик публикует новую версию

```bash
# 1. Сборка и публикация образов
./scripts/build_and_push.sh v1.2.0

# 2. Подготовка файлов для сервера
make -f Makefile.hub remote-files
```

### Сценарий 2: Развертывание на удаленном сервере

```bash
# 1. Скопировать 3 файла на сервер:
scp deploy-package/* user@server:/opt/lysodata/

# 2. На сервере:
cd /opt/lysodata
./deploy_hub.sh
```

### Сценарий 3: Обновление системы

```bash
# 1. Изменить версию в .env
BACKEND_VERSION=v1.2.0
FRONTEND_VERSION=v1.2.0

# 2. Обновить
./deploy_hub.sh restart
```

## 🔧 Команды управления

### Makefile команды

```bash
# Сборка и публикация
make -f Makefile.hub build-and-push VERSION=v1.0.0

# Развертывание
make -f Makefile.hub hub-deploy

# Управление
make -f Makefile.hub hub-status
make -f Makefile.hub hub-logs
make -f Makefile.hub hub-restart

# Подготовка для удаленного сервера
make -f Makefile.hub remote-files
```

### Прямые команды

```bash
# Сборка образов
./scripts/build_and_push.sh v1.0.0

# Развертывание
./scripts/deploy_hub.sh start
./scripts/deploy_hub.sh status
./scripts/deploy_hub.sh logs
```

## 📁 Минимальные файлы для сервера

Для развертывания нужны только:

```
deploy-package/
├── docker-compose.hub.yml    # Конфигурация сервисов
├── .env                      # Настройки (из env.hub.example)
└── deploy_hub.sh             # Скрипт управления
```

## 🌐 Результат развертывания

После успешного запуска доступны:

- **Frontend**: http://localhost:3000 
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5434
- **pgAdmin**: http://localhost:8080

## 📊 Автоматическая инициализация

При первом запуске система автоматически:

1. ✅ Создает схему PostgreSQL
2. ✅ Настраивает таблицы и индексы  
3. ✅ Загружает справочные данные
4. ✅ Импортирует тестовые данные (если доступны)

## 🔄 Workflow для команды

### Разработчик

```bash
# 1. Разработка локально
make dev

# 2. Сборка и тестирование образов  
make -f Makefile.hub build-images

# 3. Локальное тестирование
make -f Makefile.hub hub-deploy

# 4. Публикация на Docker Hub
make -f Makefile.hub push-images
```

### DevOps / Администратор

```bash
# 1. Получить файлы развертывания
make -f Makefile.hub remote-files

# 2. Настроить .env для продакшн
vi deploy-package/.env

# 3. Развернуть на сервере
scp deploy-package/* server:/opt/lysodata/
ssh server 'cd /opt/lysodata && ./deploy_hub.sh'
```

## 🛡️ Безопасность

### Обязательные изменения в .env

```bash
# Измените пароли!
POSTGRES_PASSWORD=your_secure_password_here

# Настройте порты если нужно
DB_PORT=5434
BACKEND_PORT=8000  
WEB_PORT=3000
```

### Рекомендации для продакшн

1. 🔒 Используйте HTTPS (Nginx/Traefik proxy)
2. 🔥 Настройте firewall
3. 💾 Регулярные backup'ы
4. 🔄 Мониторинг health checks

## 🚨 Устранение проблем

### Образы не найдены
```bash
# Проверить доступность
make -f Makefile.hub check-hub

# Собрать локально
make -f Makefile.hub build-images
```

### Порты заняты
```bash
# Изменить в .env
DB_PORT=5435
BACKEND_PORT=8001
WEB_PORT=3001
```

### База не инициализируется
```bash
# Проверить логи
docker logs lysodata_init

# Полная переустановка
./deploy_hub.sh clean
./deploy_hub.sh start
```

## 🎉 Заключение

Система Docker Hub развертывания LysoData-Miner обеспечивает:

- **Максимальное упрощение** развертывания
- **Профессиональный подход** к версионированию
- **Быстрые итерации** разработки и развертывания
- **Консистентность** между окружениями
- **Автоматизацию** всех рутинных операций

Готово к продуктивному использованию! 🚀 