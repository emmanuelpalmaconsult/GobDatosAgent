#!/bin/bash

# =============================================================================
# Investment Data Analysis Agent - Setup Script
# =============================================================================
# Este script configura automáticamente el entorno completo para la aplicación
# Uso: ./setup.sh [opciones]

set -e  # Exit on any error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración por defecto
DEFAULT_POSTGRES_PASSWORD="analytics_password_$(date +%s)"
DEFAULT_PGADMIN_PASSWORD="admin_password_$(date +%s)"

# Función para mostrar uso
show_help() {
    echo -e "${BLUE}Investment Data Analysis Agent - Setup Script${NC}"
    echo ""
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help              Mostrar esta ayuda"
    echo "  -f, --full              Instalación completa (PostgreSQL + pgAdmin + Redis)"
    echo "  -q, --quick             Instalación rápida (solo PostgreSQL)"  
    echo "  -c, --check             Verificar prerequisitos solamente"
    echo "  -d, --dev               Modo desarrollo con datos de prueba"
    echo "  --postgres-pass PASS    Password para PostgreSQL (auto-generado si no se especifica)"
    echo "  --pgadmin-pass PASS     Password para pgAdmin"
    echo "  --no-docker             No usar Docker (configuración manual)"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --quick                    # Instalación básica"
    echo "  $0 --full                     # Instalación completa"  
    echo "  $0 --dev --postgres-pass mypass123  # Desarrollo con password específico"
}

# Variables por defecto
INSTALL_MODE="quick"
POSTGRES_PASSWORD=""
PGADMIN_PASSWORD=""
USE_DOCKER=true
DEVELOPMENT_MODE=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--full)
            INSTALL_MODE="full"
            shift
            ;;
        -q|--quick)
            INSTALL_MODE="quick"
            shift
            ;;
        -c|--check)
            INSTALL_MODE="check"
            shift
            ;;
        -d|--dev)
            DEVELOPMENT_MODE=true
            shift
            ;;
        --postgres-pass)
            POSTGRES_PASSWORD="$2"
            shift 2
            ;;
        --pgadmin-pass)
            PGADMIN_PASSWORD="$2"
            shift 2
            ;;
        --no-docker)
            USE_DOCKER=false
            shift
            ;;
        *)
            echo -e "${RED}Opción desconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Función para logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar prerequisitos
check_prerequisites() {
    log_info "Verificando prerequisitos..."
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python encontrado: $PYTHON_VERSION"
    else
        log_error "Python 3 no encontrado. Instalarlo primero."
        exit 1
    fi
    
    # Verificar pip
    if command -v pip3 &> /dev/null; then
        log_success "pip encontrado"
    else
        log_error "pip no encontrado. Instalarlo primero."
        exit 1
    fi
    
    if [ "$USE_DOCKER" = true ]; then
        # Verificar Docker
        if command -v docker &> /dev/null; then
            log_success "Docker encontrado"
        else
            log_error "Docker no encontrado. Instalarlo primero o usar --no-docker"
            exit 1
        fi
        
        # Verificar Docker Compose
        if command -v docker-compose &> /dev/null; then
            log_success "Docker Compose encontrado"
        else
            log_error "Docker Compose no encontrado. Instalarlo primero."
            exit 1
        fi
        
        # Verificar que Docker esté corriendo
        if docker info &> /dev/null; then
            log_success "Docker está corriendo"
        else
            log_error "Docker no está corriendo. Iniciarlo primero."
            exit 1
        fi
    fi
}

# Generar passwords si no se especificaron
generate_passwords() {
    if [ -z "$POSTGRES_PASSWORD" ]; then
        POSTGRES_PASSWORD=$DEFAULT_POSTGRES_PASSWORD
        log_info "Password para PostgreSQL auto-generado"
    fi
    
    if [ -z "$PGADMIN_PASSWORD" ]; then
        PGADMIN_PASSWORD=$DEFAULT_PGADMIN_PASSWORD
        log_info "Password para pgAdmin auto-generado"
    fi
}

# Crear archivo .env
create_env_file() {
    log_info "Creando archivo .env..."
    
    cat > .env << EOF
# ==============================================
# SOURCE DATABASE CONFIGURATION (Tu BD Existente)
# ==============================================
# Cambiar estos valores por tu base de datos real

# Tipo de base de datos: postgresql, sqlserver, mysql
SOURCE_DB_TYPE=postgresql
SOURCE_DB_HOST=localhost
SOURCE_DB_PORT=5433
SOURCE_DB_NAME=InvestmentSource
SOURCE_DB_USER=source_user
SOURCE_DB_PASSWORD=source_password

# ==============================================
# ANALYTICS DATABASE CONFIGURATION (PostgreSQL Docker)
# ==============================================

ANALYTICS_DB_HOST=localhost
ANALYTICS_DB_PORT=5432
ANALYTICS_DB_NAME=InvestmentAnalytics
ANALYTICS_DB_USER=analytics_user
ANALYTICS_DB_PASSWORD=${POSTGRES_PASSWORD}

# ==============================================
# APPLICATION CONFIGURATION
# ==============================================

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Logging
LOG_LEVEL=INFO

# Analytics
ENABLE_AI_ANALYSIS=true
CACHE_EXPIRY_HOURS=24
MAX_CORRELATION_RECORDS=10000

# ==============================================
# OPTIONAL SERVICES
# ==============================================

# pgAdmin (si se instala)
PGADMIN_EMAIL=admin@investment.local
PGADMIN_PASSWORD=${PGADMIN_PASSWORD}

# Redis Cache (si se instala)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ==============================================
# DEVELOPMENT/TESTING
# ==============================================

DEVELOPMENT_MODE=${DEVELOPMENT_MODE}
CREATE_TEST_DATA=false
EOF

    log_success "Archivo .env creado"
}

# Instalar dependencias Python
install_python_deps() {
    log_info "Instalando dependencias Python..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "Dependencias Python instaladas"
    else
        log_error "Archivo requirements.txt no encontrado"
        exit 1
    fi
}

# Configurar Docker
setup_docker() {
    log_info "Configurando servicios Docker..."
    
    case $INSTALL_MODE in
        quick)
            log_info "Iniciando PostgreSQL solamente..."
            docker-compose up -d analytics-db
            ;;
        full)
            log_info "Iniciando todos los servicios..."
            docker-compose --profile admin --profile cache up -d
            ;;
    esac
    
    # Esperar a que PostgreSQL esté listo
    log_info "Esperando a que PostgreSQL esté listo..."
    sleep 10
    
    # Verificar conexión
    max_attempts=30
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if docker exec investment-analytics pg_isready -U analytics_user -d InvestmentAnalytics &> /dev/null; then
            log_success "PostgreSQL está listo"
            break
        else
            if [ $attempt -eq $max_attempts ]; then
                log_error "PostgreSQL no responde después de $max_attempts intentos"
                exit 1
            fi
            log_info "Esperando PostgreSQL... (intento $attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
}

# Verificar instalación
verify_installation() {
    log_info "Verificando instalación..."
    
    # Verificar PostgreSQL
    if docker exec investment-analytics psql -U analytics_user -d InvestmentAnalytics -c "SELECT COUNT(*) FROM table_configuration;" &> /dev/null; then
        log_success "Base de datos PostgreSQL configurada correctamente"
    else
        log_error "Error en configuración de PostgreSQL"
        return 1
    fi
    
    # Verificar aplicación Python
    if python3 -c "import app.main" &> /dev/null; then
        log_success "Aplicación Python configurada correctamente"  
    else
        log_error "Error en configuración de aplicación Python"
        return 1
    fi
    
    return 0
}

# Mostrar información final
show_final_info() {
    echo ""
    echo -e "${GREEN}🎉 Instalación completada exitosamente! 🎉${NC}"
    echo ""
    echo -e "${BLUE}Información de conexión:${NC}"
    echo "┌─────────────────────────────────────────────┐"
    echo "│ PostgreSQL Analytics:                       │"
    echo "│   Host: localhost:5432                      │"
    echo "│   Database: InvestmentAnalytics             │"
    echo "│   User: analytics_user                      │"
    echo "│   Password: ${POSTGRES_PASSWORD:0:20}...              │"
    echo "└─────────────────────────────────────────────┘"
    
    if [ "$INSTALL_MODE" = "full" ]; then
        echo ""
        echo "┌─────────────────────────────────────────────┐"
        echo "│ pgAdmin Web Interface:                      │"
        echo "│   URL: http://localhost:8080                │"
        echo "│   Email: admin@investment.local             │"
        echo "│   Password: ${PGADMIN_PASSWORD:0:20}...              │"
        echo "└─────────────────────────────────────────────┘"
        
        echo ""
        echo "┌─────────────────────────────────────────────┐"
        echo "│ Redis Cache:                                │"
        echo "│   Host: localhost:6379                      │"
        echo "│   Database: 0                               │"
        echo "└─────────────────────────────────────────────┘"
    fi
    
    echo ""
    echo -e "${YELLOW}Próximos pasos:${NC}"
    echo "1. Editar archivo .env con tu información de BD origen" 
    echo "2. Ejecutar: python -m uvicorn app.main:app --reload"
    echo "3. Abrir: http://localhost:8000/docs"
    echo "4. Configurar tus tablas origen en /api/v1/admin/tables"
    echo ""
    echo -e "${YELLOW}Comandos útiles:${NC}"
    echo "• Ver logs: docker-compose logs -f"
    echo "• Parar servicios: docker-compose down"
    echo "• Reiniciar: docker-compose restart"
    echo "• Backup BD: docker exec investment-analytics pg_dump -U analytics_user InvestmentAnalytics > backup.sql"
    echo ""
    echo -e "${BLUE}¡La aplicación está lista para usar! 🚀${NC}"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║        Investment Data Analysis Agent - Setup Script        ║"
    echo "║              Configuración Automática del Sistema           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Solo verificar prerequisitos
    if [ "$INSTALL_MODE" = "check" ]; then
        check_prerequisites
        log_success "Todos los prerequisitos están correctos"
        exit 0
    fi
    
    # Ejecutar setup completo
    check_prerequisites
    generate_passwords
    create_env_file
    install_python_deps
    
    if [ "$USE_DOCKER" = true ]; then
        setup_docker
    else
        log_warning "Configuración manual de base de datos requerida (--no-docker especificado)"
    fi
    
    if verify_installation; then
        show_final_info
    else
        log_error "La verificación falló. Revisar logs para más detalles."
        exit 1
    fi
}

# Ejecutar función principal
main