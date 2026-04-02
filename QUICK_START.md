# 🚀 Inicio Rápido - Usando tu Contenedor PostgreSQL Existente

Ya que tienes tu contenedor **postgres-learn** corriendo, aquí está la configuración específica para tu caso:

## 📋 Tu Configuración Actual

```
Contenedor: postgres-learn
Usuario: admin  
Contraseña: password123
Base de datos: learning
Puerto: 5432
Host: localhost
```

## ⚡ Configuración en 3 Pasos

### 1. Configurar Tablas de Analytics

Ejecutar uno de estos comandos para crear las tablas necesarias:

**Windows (PowerShell):**
```powershell
.\setup_existing_postgres.ps1
```

**Linux/Mac:**
```bash
chmod +x setup_existing_postgres.sh
./setup_existing_postgres.sh
```

### 2. Verificar Configuración

Tu archivo [.env](.env) ya está configurado con tus credenciales:
- ✅ Analytics DB: postgres-learn (puerto 5432)
- ⚠️ Source DB: Puerto 5433 (configurar con tu BD de inversiones real)

### 3. Ejecutar la Aplicación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python -m uvicorn app.main:app --reload
```

## 🌐 Acceder a la Aplicación

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Database Status**: http://localhost:8000/api/v1/health/database

## 🔧 Configuración de Base de Datos de Origen

Editar [.env](.env) líneas 7-11 con tu base de datos real de inversiones:

```env
SOURCE_DB_TYPE=postgresql  # o sqlserver, mysql
SOURCE_DB_HOST=tu_servidor
SOURCE_DB_PORT=tu_puerto
SOURCE_DB_NAME=tu_base_datos_inversiones
SOURCE_DB_USER=tu_usuario
SOURCE_DB_PASSWORD=tu_password
```

## 📊 Verificar Todo Funcionando

### 1. Verificar Contenedor PostgreSQL
```bash
docker ps | grep postgres-learn
```

### 2. Verificar Tablas Creadas
```bash
docker exec -it postgres-learn psql -U admin -d learning -c "\dt"
```

### 3. Verificar API
```bash
curl http://localhost:8000/api/v1/health/database
```

## 🎯 Principales Endpoints

Una vez configurado, podrás usar:

- **Portfolios**: `/api/v1/portfolios/`
- **Analysis**: `/api/v1/analysis/correlation`
- **KPIs**: `/api/v1/kpis/portfolio/{id}`
- **Export**: `/api/v1/export/powerbi`

## ❗ Troubleshooting

| Problema | Solución |
|----------|----------|
| Contenedor no responde | `docker start postgres-learn` |
| Error de conexión | Verificar credenciales en .env |
| Tablas no existen | Ejecutar `setup_existing_postgres.ps1` |
| Puerto ocupado | Cambiar SOURCE_DB_PORT en .env |

## 📁 Estructura de Archivos Importante

```
GobDatosAgent/
├── .env                          # ✅ Configurado para postgres-learn
├── setup_existing_postgres.ps1    # ✅ Script para tu contenedor
├── app/main.py                   # 🚀 Aplicación principal
└── requirements.txt              # 📦 Dependencias
```

---

## 🎉 ¡Listo para Usar!

Con estos pasos, tu Investment Data Analysis Agent estará conectado a tu contenedor existente y listo para procesar datos de inversión. 

El sistema usará:
- **postgres-learn** para almacenar resultados de análisis
- **Tu BD origen** para extraer datos de inversión
- **FastAPI** para exponer APIs
- **Power BI/Data Studio** para visualización