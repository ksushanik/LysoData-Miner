# Technical Context - LysoData-Miner

## 🏗️ Архитектура системы

**LysoData-Miner** построен по современной микросервисной архитектуре с разделением на backend API, frontend SPA и базу данных, развернутую в Docker контейнерах.

### Общая архитектура
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   React SPA     │────│   FastAPI       │────│  PostgreSQL     │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌─────────────────┐                │
         └──────────────│     Nginx       │────────────────┘
                        │ Reverse Proxy   │
                        │   Port: 3000    │
                        └─────────────────┘
```

---

## 🗄️ База данных - PostgreSQL 15

### Схема данных (3NF нормализация)
```sql
-- Основные таблицы
test_categories (5 записей)
├── category_id (PK)
├── category_name (biochemical, physiological, metabolic, morphological, other)
└── description

tests (459 записей)
├── test_id (PK)
├── test_name
├── category_id (FK → test_categories)
└── description

strains (228 записей)
├── strain_id (PK)
├── scientific_name
├── full_name
├── strain_code
└── source_id (FK → sources)

collection_numbers (149 записей)
├── collection_id (PK)
├── strain_id (FK → strains)
├── collection_name (DSMZ, ATCC, JCM, etc.)
└── collection_number

sources (84 записи)
├── source_id (PK)
├── title
├── authors
├── year
└── doi

test_results (9,950 записей)
├── result_id (PK)
├── strain_id (FK → strains)
├── test_id (FK → tests)
├── result_value (positive/negative/variable/no_data)
└── numeric_value
```

### Ключевые индексы
```sql
-- Производительные индексы для быстрого поиска
CREATE INDEX idx_test_results_strain_test ON test_results(strain_id, test_id);
CREATE INDEX idx_test_results_value ON test_results(result_value);
CREATE INDEX idx_strains_scientific_name ON strains(scientific_name);
CREATE INDEX idx_tests_category ON tests(category_id);
CREATE INDEX idx_collection_numbers_strain ON collection_numbers(strain_id);
```

### Связи и целостность
- **Строгие foreign keys** для поддержания целостности данных
- **Каскадные операции** для связанных записей
- **Check constraints** для валидации значений
- **NOT NULL constraints** для обязательных полей

---

## ⚡ Backend - FastAPI + Python

### Технологический стек
```python
# Основные зависимости
FastAPI==0.68+          # Modern async web framework
SQLAlchemy==1.4+        # SQL toolkit and ORM
asyncpg==0.24+          # Async PostgreSQL driver
Pydantic==1.8+          # Data validation and settings
loguru==0.5+            # Advanced logging
python-multipart==0.0.5 # File upload support
```

### API Endpoints
```python
# Health and monitoring
GET  /api/health/           # Basic health check
GET  /api/health/db         # Database health with metrics

# Data access
GET  /api/tests/categories  # List test categories (5 items)
GET  /api/tests/            # List tests with filtering
GET  /api/strains/          # Search strains with details
GET  /api/species           # Species list for browser

# Core functionality  
POST /api/identification/identify  # Main identification algorithm

# Documentation
GET  /api/docs              # Swagger UI documentation
GET  /api/redoc             # ReDoc documentation
```

### Алгоритм идентификации
```python
async def identify_strains(test_results: List[TestResult]) -> List[StrainMatch]:
    """
    Основной алгоритм идентификации штаммов
    
    1. Построение SQL запроса с JOIN по результатам тестов
    2. Вычисление процента совпадения для каждого штамма
    3. Подсчет конфликтующих результатов  
    4. Ранжирование по confidence score
    5. Возврат топ-N результатов
    """
    # Время выполнения: ~50ms для типичного запроса
    # Память: ~10MB для обработки 228 штаммов
```

### Конфигурация и окружение
```bash
# Environment variables
DATABASE_URL=postgresql://user:pass@host:port/db
CORS_ORIGINS=http://localhost:3000,http://89.169.171.236:3000
LOG_LEVEL=INFO
API_PREFIX=/api
```

---

## 🎨 Frontend - React + TypeScript

### Технологический стек
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0", 
    "react-router-dom": "^6.0.0",
    "typescript": "^4.9.0",
    "axios": "^1.0.0",
    "tailwindcss": "^3.0.0"
  },
  "devDependencies": {
    "vite": "^4.0.0",
    "@types/react": "^18.0.0",
    "@vitejs/plugin-react": "^3.0.0"
  }
}
```

### Структура компонентов
```
frontend/src/
├── components/           # Переиспользуемые компоненты
│   ├── IdentificationForm.tsx
│   ├── TestSelector.tsx
│   ├── ResultsModal.tsx
│   └── Layout.tsx
├── pages/               # Основные страницы
│   ├── Dashboard.tsx    # Главная страница
│   ├── IdentificationTool.tsx
│   ├── StrainBrowser.tsx
│   ├── SpeciesBrowser.tsx
│   ├── StrainDetail.tsx
│   └── ComparePage.tsx
├── services/            # API интеграция
│   └── api.ts          # Axios client + endpoints
├── types/              # TypeScript типы
│   └── api.ts          # API response types
└── styles/             # Стили
    └── index.css       # Tailwind imports
```

### API интеграция
```typescript
// Автоматическое определение окружения
const isDevelopment = (window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1') && 
                      window.location.port === '3000';

const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000/api'  // Development (Vite dev server)
  : '/api';                      // Production (Nginx proxy)

// Axios client с автоконфигурацией
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
});
```

### UI/UX особенности
- **Responsive design** - адаптация под мобильные устройства
- **Loading states** - индикаторы загрузки для всех API вызовов
- **Error handling** - корректная обработка и отображение ошибок
- **Debounced search** - оптимизация поисковых запросов
- **TypeScript** - полная типизация для предотвращения ошибок

---

## 🐳 Развертывание - Docker

### Docker Compose конфигурация
```yaml
# config/docker/docker-compose.production.yml
services:
  backend:
    image: gimmyhat/lysodata-backend:latest
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql://lyso_user:lyso_pass@database:5432/lyso_db
    depends_on: [database]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: gimmyhat/lysodata-frontend:latest  
    ports: ["3000:80"]
    depends_on: [backend]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/"]
      interval: 30s
      timeout: 10s
      retries: 3

  database:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=lyso_db
      - POSTGRES_USER=lyso_user  
      - POSTGRES_PASSWORD=lyso_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U lyso_user -d lyso_db"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  lysodata_net:
    driver: bridge

volumes:
  postgres_data:
```

### Frontend Nginx конфигурация
```nginx
# frontend/nginx.conf
server {
    listen 80;
    
    # Serve React static files
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Optimize static file serving
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Dockerfile оптимизации
```dockerfile
# Frontend multi-stage build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 🌐 Production Environment

### Сервер конфигурация
```bash
# Удаленный сервер
Host: 89.169.171.236
OS: Linux (Ubuntu/CentOS)
Docker: 20.10+
Docker Compose: 2.0+

# Порты и сервисы
Frontend: http://89.169.171.236:3000 (Nginx)
Backend:  http://89.169.171.236:8000 (Internal, FastAPI)
Database: postgresql://localhost:5432  (Internal, PostgreSQL)

# Сеть Docker
Network: lysodata_lysodata_net
```

### Мониторинг и логирование
```bash
# Health checks
curl http://89.169.171.236:3000/api/health/     # API health
curl http://89.169.171.236:3000/api/health/db   # Database health

# Container logs
docker logs lysodata_backend --tail 50   # Backend logs
docker logs lysodata_web --tail 50       # Frontend/Nginx logs  
docker logs lysodata_db --tail 50        # PostgreSQL logs

# Container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Performance метрики
```bash
# API Response Times (production)
/api/health/        ~10ms
/api/tests/categories ~15ms
/api/tests/         ~25ms  
/api/strains/       ~40ms
/api/identification/identify ~50ms

# Database Queries
SELECT * FROM strains;           ~5ms  (228 records)
SELECT * FROM test_results;     ~15ms (9,950 records)
Complex JOIN queries            ~30ms (identification)

# Resource Usage
CPU: <20% average
Memory: ~500MB total (all containers)
Disk: ~100MB (database + logs)
Network: <1MB/s typical traffic
```

---

## 🔧 Development Environment

### Локальная разработка
```bash
# Backend development (FastAPI auto-reload)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend development (Vite HMR)
cd frontend  
npm install
npm run dev  # Runs on http://localhost:3000

# Database (Docker)
docker run -d \
  --name postgres-dev \
  -e POSTGRES_DB=lyso_db \
  -e POSTGRES_USER=lyso_user \
  -e POSTGRES_PASSWORD=lyso_pass \
  -p 5432:5432 \
  postgres:15-alpine
```

### Debug и тестирование
```bash
# API testing
curl -X GET http://localhost:8000/api/health/
curl -X GET http://localhost:8000/api/tests/categories
curl -X POST http://localhost:8000/api/identification/identify \
  -H "Content-Type: application/json" \
  -d '{"tests": [{"test_id": 1, "result": "positive"}]}'

# Frontend testing  
npm run build    # Production build test
npm run preview  # Preview production build
npm run lint     # TypeScript/ESLint checks
```

---

## 🛡️ Безопасность и надежность

### Принципы безопасности
- **CORS настройки** - только разрешенные домены
- **Input validation** - Pydantic схемы для всех API
- **SQL injection protection** - SQLAlchemy ORM
- **Error handling** - безопасные сообщения об ошибках
- **Health checks** - мониторинг состояния сервисов

### Backup и восстановление
```bash
# Database backup
docker exec lysodata_db pg_dump -U lyso_user lyso_db > backup.sql

# Database restore  
docker exec -i lysodata_db psql -U lyso_user lyso_db < backup.sql

# Container restart
docker-compose restart
docker-compose up -d --force-recreate
```

### Логирование
```python
# Backend logging (loguru)
logger.info("API request: {method} {path}", method=request.method, path=request.url.path)
logger.error("Database error: {error}", error=str(e))

# Nginx access logs
89.169.171.236 - - [timestamp] "GET /api/health/ HTTP/1.1" 200 135
89.169.171.236 - - [timestamp] "GET /api/species HTTP/1.1" 200 2847
```

---

## 🚀 Производительность и масштабирование

### Текущая оптимизация
- **Database indexing** - быстрые поиски по всем ключевым полям
- **SQL query optimization** - эффективные JOIN операции
- **Frontend lazy loading** - загрузка компонентов по требованию
- **API response caching** - кэширование редко изменяемых данных
- **Docker layer caching** - быстрая пересборка образов

### Потенциальные улучшения
- **Redis caching** - кэширование API ответов
- **Database connection pooling** - управление соединениями
- **CDN integration** - ускорение статических файлов
- **Horizontal scaling** - множественные backend экземпляры
- **Load balancing** - распределение нагрузки

---

## 📊 Мониторинг и аналитика

### Ключевые метрики
- **API uptime** - доступность сервиса (цель: 99.9%)
- **Response time** - время ответа API (цель: <100ms)
- **Error rate** - частота ошибок (цель: <1%)
- **Database performance** - время выполнения запросов
- **Resource utilization** - использование CPU/Memory/Disk

### Инструменты мониторинга
- **Docker health checks** - автоматическая проверка контейнеров
- **Nginx access logs** - анализ трафика и ошибок
- **Application logs** - детальное логирование операций
- **Database monitoring** - PostgreSQL метрики производительности

Система **LysoData-Miner** построена с использованием современных технологий и best practices, обеспечивая высокую производительность, надежность и удобство сопровождения. 