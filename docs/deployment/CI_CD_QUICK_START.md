# 🚀 LysoData-Miner CI/CD Quick Start

Простая система CI/CD для автоматического обновления приложения на сервере 4feb.

## ⚡ Быстрый старт (30 секунд)

```bash
# 1. Настройка системы
make -f Makefile.cicd cicd-setup

# 2. Ручное развертывание
make -f Makefile.cicd deploy

# 3. Автоматическое развертывание (опционально)
make -f Makefile.cicd watch-start

# 4. Webhook сервер (опционально)
make -f Makefile.cicd webhook-start-bg
```

## 📋 Основные команды

### 🚀 Развертывание
```bash
make -f Makefile.cicd deploy              # Полное развертывание
make -f Makefile.cicd deploy-frontend     # Только frontend
make -f Makefile.cicd deploy-backend      # Только backend
make -f Makefile.cicd deploy-dry-run      # Предварительный просмотр
```

### 👁️ Автоматический watcher
```bash
make -f Makefile.cicd watch-start         # Запуск
make -f Makefile.cicd watch-status        # Статус
make -f Makefile.cicd watch-logs          # Логи
make -f Makefile.cicd watch-stop          # Остановка
```

### 🔗 Webhook сервер
```bash
make -f Makefile.cicd webhook-start-bg    # Запуск в фоне
make -f Makefile.cicd webhook-test        # Тестирование
make -f Makefile.cicd webhook-status      # Статус
make -f Makefile.cicd webhook-stop        # Остановка
```

### ⚙️ Управление системой
```bash
make -f Makefile.cicd cicd-status         # Полный статус
make -f Makefile.cicd start-all           # Запуск всех сервисов
make -f Makefile.cicd stop-all            # Остановка всех сервисов
```

## 🎯 Сценарии использования

### Сценарий 1: Ручное развертывание
Для разработчиков, которые хотят контролировать процесс развертывания:

```bash
# Проверить что будет сделано
make -f Makefile.cicd deploy-dry-run

# Развернуть изменения
make -f Makefile.cicd deploy

# Проверить результат
make -f Makefile.cicd cicd-status
```

### Сценарий 2: Автоматическое развертывание
Для автоматического развертывания при изменениях в git:

```bash
# Запустить watcher
make -f Makefile.cicd watch-start

# Теперь любые изменения в main ветке будут автоматически развернуты
# Следить за процессом:
make -f Makefile.cicd watch-logs
```

### Сценарий 3: Удаленное развертывание
Для развертывания через HTTP API:

```bash
# Запустить webhook сервер
make -f Makefile.cicd webhook-start-bg

# Развернуть через HTTP (из любого места):
curl -X POST http://your-server:9000/deploy

# Или с опциями:
curl -X POST http://your-server:9000/deploy \
     -H "Content-Type: application/json" \
     -d '{"options": {"force_build": true}}'
```

## 🔧 Что происходит при развертывании

1. **Анализ изменений** - система определяет что изменилось (frontend/backend)
2. **Сборка образов** - создаются новые Docker образы только для измененных компонентов
3. **Push в Docker Hub** - образы загружаются в реестр `gimmyhat/lysodata-*:latest`
4. **Backup на сервере** - создается backup базы данных перед обновлением
5. **Обновление на сервере** - контейнеры обновляются новыми образами
6. **Health checks** - проверяется работоспособность приложения
7. **Уведомления** - отправляется статус развертывания

## 📊 Мониторинг

```bash
# Статус всей системы
make -f Makefile.cicd cicd-status

# Проверка удаленного сервера
ssh 4feb "docker ps"
ssh 4feb "curl -s http://localhost:8000/api/health/"

# Просмотр логов
make -f Makefile.cicd watch-logs
tail -f webhook_deploy.log
```

## 🚨 Решение проблем

### Проблема: Развертывание не работает
```bash
# Проверить подключение к серверу
ssh 4feb "echo 'OK'"

# Проверить Docker Hub аутентификацию
docker login

# Запустить диагностику
make -f Makefile.cicd deploy-dry-run
```

### Проблема: Watcher не запускается
```bash
# Проверить статус
make -f Makefile.cicd watch-status

# Перезапустить
make -f Makefile.cicd watch-stop
make -f Makefile.cicd watch-start
```

### Проблема: Webhook не отвечает
```bash
# Проверить статус
make -f Makefile.cicd webhook-status

# Тестировать endpoint
make -f Makefile.cicd webhook-test
```

## 🎉 Результат

После настройки у вас будет:

- ✅ **Ручное развертывание одной командой**: `make -f Makefile.cicd deploy`
- ✅ **Автоматическое развертывание** при изменениях в git
- ✅ **HTTP API для удаленного развертывания** через webhook
- ✅ **Интеллектуальное определение изменений** - обновляются только измененные компоненты
- ✅ **Автоматические backup'ы** перед каждым развертыванием
- ✅ **Health checks** после развертывания
- ✅ **Полное логирование** всех операций

## 🔗 Ссылки

- **Подробная документация**: [CI_CD_GUIDE.md](CI_CD_GUIDE.md)
- **Frontend**: http://89.169.171.236:3000
- **Backend API**: http://89.169.171.236:8000
- **API Docs**: http://89.169.171.236:8000/api/docs

---

**💡 Совет**: Начните с ручного развертывания, а затем переходите к автоматическому по мере необходимости. 