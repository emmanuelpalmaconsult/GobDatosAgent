# =============================================================================
# Investment Data Analysis Agent - Setup Script (Windows PowerShell)
# =============================================================================
# Este script configura automáticamente el entorno completo para la aplicación
# Uso: .\setup.ps1 [parámetros]

param(
    [switch]$Help,
    [switch]$Full,
    [switch]$Quick,
    [switch]$Check, 
    [switch]$Dev,
    [string]$PostgresPassword = "",
    [string]$PgAdminPassword = "",
    [switch]$NoDocker
)

# Configuración por defecto
$DefaultPostgresPassword = "analytics_password_$(Get-Date -Format 'yyyyMMddHHmmss')"
$DefaultPgAdminPassword = "admin_password_$(Get-Date -Format 'yyyyMMddHHmmss')"

# Colores para output
function Write-ColorOutput($ForegroundColor) {
    # store the current color
    $fc = $host.UI.RawUI.ForegroundColor
    # set the new color
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    # output
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    # restore the original color
    $host.UI.RawUI.ForegroundColor = $fc
}

function Log-Info($message) {
    Write-ColorOutput Blue "[INFO] $message"
}

function Log-Success($message) {
    Write-ColorOutput Green "[SUCCESS] $message"
}

function Log-Warning($message) {
    Write-ColorOutput Yellow "[WARNING] $message"
}

function Log-Error($message) {
    Write-ColorOutput Red "[ERROR] $message"
}

# Función para mostrar ayuda
function Show-Help {
    Write-ColorOutput Blue "Investment Data Analysis Agent - Setup Script (Windows)"
    Write-Host ""
    Write-Host "Uso: .\setup.ps1 [parámetros]"
    Write-Host ""
    Write-Host "Parámetros:"
    Write-Host "  -Help                    Mostrar esta ayuda"
    Write-Host "  -Full                    Instalación completa (PostgreSQL + pgAdmin + Redis)"
    Write-Host "  -Quick                   Instalación rápida (solo PostgreSQL)"  
    Write-Host "  -Check                   Verificar prerequisitos solamente"
    Write-Host "  -Dev                     Modo desarrollo con datos de prueba"
    Write-Host "  -PostgresPassword PASS   Password para PostgreSQL (auto-generado si no se especifica)"
    Write-Host "  -PgAdminPassword PASS    Password para pgAdmin"
    Write-Host "  -NoDocker               No usar Docker (configuración manual)"
    Write-Host ""
    Write-Host "Ejemplos:"
    Write-Host "  .\setup.ps1 -Quick                              # Instalación básica"
    Write-Host "  .\setup.ps1 -Full                               # Instalación completa"  
    Write-Host "  .\setup.ps1 -Dev -PostgresPassword 'mypass123'  # Desarrollo con password específico"
}

# Mostrar ayuda si se solicitó
if ($Help) {
    Show-Help
    exit 0
}

# Configurar variables según parámetros
$InstallMode = if ($Full) { "full" } elseif ($Check) { "check" } else { "quick" }
$UseDocker = -not $NoDocker
$DevelopmentMode = $Dev

# Generar passwords si no se especificaron
if (-not $PostgresPassword) {
    $PostgresPassword = $DefaultPostgresPassword
    Log-Info "Password para PostgreSQL auto-generado"
}

if (-not $PgAdminPassword) {
    $PgAdminPassword = $DefaultPgAdminPassword
    Log-Info "Password para pgAdmin auto-generado"
}

# Verificar prerequisitos
function Test-Prerequisites {
    Log-Info "Verificando prerequisitos..."
    
    # Verificar Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+\.\d+)") {
            Log-Success "Python encontrado: $($matches[1])"
        } else {
            throw "Python no encontrado o versión no detectada"
        }
    } catch {
        Log-Error "Python 3 no encontrado. Instalarlo primero desde https://python.org"
        exit 1
    }
    
    # Verificar pip
    try {
        $pipVersion = pip --version 2>&1
        if ($pipVersion) {
            Log-Success "pip encontrado"
        }
    } catch {
        Log-Error "pip no encontrado. Instalarlo primero."
        exit 1
    }
    
    if ($UseDocker) {
        # Verificar Docker
        try {
            $dockerVersion = docker --version 2>&1
            if ($dockerVersion -match "Docker version") {
                Log-Success "Docker encontrado: $dockerVersion"
            } else {
                throw "Docker no detectado correctamente"
            }
        } catch {
            Log-Error "Docker no encontrado. Instalarlo desde https://docker.com/get-started o usar -NoDocker"
            exit 1
        }
        
        # Verificar Docker Compose
        try {
            $composeVersion = docker-compose --version 2>&1
            if ($composeVersion -match "docker-compose version") {
                Log-Success "Docker Compose encontrado: $composeVersion"
            } else {
                throw "Docker Compose no detectado"
            }
        } catch {
            Log-Error "Docker Compose no encontrado. Instalarlo primero."
            exit 1
        }
        
        # Verificar que Docker esté corriendo
        try {
            docker info | Out-Null
            Log-Success "Docker está corriendo"
        } catch {
            Log-Error "Docker no está corriendo. Iniciarlo primero (Docker Desktop)."
            exit 1
        }
    }
}

# Crear archivo .env
function New-EnvFile {
    Log-Info "Creando archivo .env..."
    
$envContent = @"
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
ANALYTICS_DB_PASSWORD=$PostgresPassword

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
PGADMIN_PASSWORD=$PgAdminPassword

# Redis Cache (si se instala)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# ==============================================
# DEVELOPMENT/TESTING
# ==============================================

DEVELOPMENT_MODE=$($DevelopmentMode.ToString().ToLower())
CREATE_TEST_DATA=false
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Log-Success "Archivo .env creado"
}

# Instalar dependencias Python
function Install-PythonDependencies {
    Log-Info "Instalando dependencias Python..."
    
    if (Test-Path "requirements.txt") {
        try {
            pip install -r requirements.txt
            Log-Success "Dependencias Python instaladas"
        } catch {
            Log-Error "Error instalando dependencias Python: $($_.Exception.Message)"
            exit 1
        }
    } else {
        Log-Error "Archivo requirements.txt no encontrado"
        exit 1
    }
}

# Configurar Docker
function Start-DockerServices {
    Log-Info "Configurando servicios Docker..."
    
    try {
        switch ($InstallMode) {
            "quick" {
                Log-Info "Iniciando PostgreSQL solamente..."
                docker-compose up -d analytics-db
            }
            "full" {
                Log-Info "Iniciando todos los servicios..."
                docker-compose --profile admin --profile cache up -d
            }
        }
        
        # Esperar a que PostgreSQL esté listo
        Log-Info "Esperando a que PostgreSQL esté listo..."
        Start-Sleep -Seconds 10
        
        # Verificar conexión
        $maxAttempts = 30
        $attempt = 1
        
        while ($attempt -le $maxAttempts) {
            try {
                docker exec investment-analytics pg_isready -U analytics_user -d InvestmentAnalytics | Out-Null
                Log-Success "PostgreSQL está listo"
                break
            } catch {
                if ($attempt -eq $maxAttempts) {
                    Log-Error "PostgreSQL no responde después de $maxAttempts intentos"
                    exit 1
                }
                Log-Info "Esperando PostgreSQL... (intento $attempt/$maxAttempts)"
                Start-Sleep -Seconds 2
                $attempt++
            }
        }
    } catch {
        Log-Error "Error configurando Docker: $($_.Exception.Message)"
        exit 1
    }
}

# Verificar instalación
function Test-Installation {
    Log-Info "Verificando instalación..."
    
    try {
        # Verificar PostgreSQL
        docker exec investment-analytics psql -U analytics_user -d InvestmentAnalytics -c "SELECT COUNT(*) FROM table_configuration;" | Out-Null
        Log-Success "Base de datos PostgreSQL configurada correctamente"
        
        # Verificar aplicación Python
        python -c "import app.main" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Log-Success "Aplicación Python configurada correctamente"
            return $true
        } else {
            Log-Error "Error en configuración de aplicación Python"
            return $false
        }
    } catch {
        Log-Error "Error en verificación: $($_.Exception.Message)"
        return $false
    }
}

# Mostrar información final
function Show-FinalInfo {
    Write-Host ""
    Write-ColorOutput Green "🎉 Instalación completada exitosamente! 🎉"
    Write-Host ""
    Write-ColorOutput Blue "Información de conexión:"
    Write-Host "┌─────────────────────────────────────────────┐"
    Write-Host "│ PostgreSQL Analytics:                       │"
    Write-Host "│   Host: localhost:5432                      │"
    Write-Host "│   Database: InvestmentAnalytics             │"
    Write-Host "│   User: analytics_user                      │"
    Write-Host "│   Password: $($PostgresPassword.Substring(0, [Math]::Min(20, $PostgresPassword.Length)))...              │"
    Write-Host "└─────────────────────────────────────────────┘"
    
    if ($InstallMode -eq "full") {
        Write-Host ""
        Write-Host "┌─────────────────────────────────────────────┐"
        Write-Host "│ pgAdmin Web Interface:                      │"
        Write-Host "│   URL: http://localhost:8080                │"
        Write-Host "│   Email: admin@investment.local             │"
        Write-Host "│   Password: $($PgAdminPassword.Substring(0, [Math]::Min(20, $PgAdminPassword.Length)))...              │"
        Write-Host "└─────────────────────────────────────────────┘"
        
        Write-Host ""
        Write-Host "┌─────────────────────────────────────────────┐"
        Write-Host "│ Redis Cache:                                │"
        Write-Host "│   Host: localhost:6379                      │"
        Write-Host "│   Database: 0                               │"
        Write-Host "└─────────────────────────────────────────────┘"
    }
    
    Write-Host ""
    Write-ColorOutput Yellow "Próximos pasos:"
    Write-Host "1. Editar archivo .env con tu información de BD origen" 
    Write-Host "2. Ejecutar: python -m uvicorn app.main:app --reload"
    Write-Host "3. Abrir: http://localhost:8000/docs"
    Write-Host "4. Configurar tus tablas origen en /api/v1/admin/tables"
    Write-Host ""
    Write-ColorOutput Yellow "Comandos útiles:"
    Write-Host "• Ver logs: docker-compose logs -f"
    Write-Host "• Parar servicios: docker-compose down"
    Write-Host "• Reiniciar: docker-compose restart"
    Write-Host "• Backup BD: docker exec investment-analytics pg_dump -U analytics_user InvestmentAnalytics > backup.sql"
    Write-Host ""
    Write-ColorOutput Blue "¡La aplicación está lista para usar! 🚀"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

function Main {
    Write-ColorOutput Blue @"
╔══════════════════════════════════════════════════════════════╗
║        Investment Data Analysis Agent - Setup Script        ║
║              Configuración Automática del Sistema           ║
║                        (Windows)                            ║
╚══════════════════════════════════════════════════════════════╝
"@
    
    # Solo verificar prerequisitos
    if ($InstallMode -eq "check") {
        Test-Prerequisites
        Log-Success "Todos los prerequisitos están correctos"
        exit 0
    }
    
    # Ejecutar setup completo
    try {
        Test-Prerequisites
        New-EnvFile
        Install-PythonDependencies
        
        if ($UseDocker) {
            Start-DockerServices
        } else {
            Log-Warning "Configuración manual de base de datos requerida (-NoDocker especificado)"
        }
        
        if (Test-Installation) {
            Show-FinalInfo
        } else {
            Log-Error "La verificación falló. Revisar logs para más detalles."
            exit 1
        }
    } catch {
        Log-Error "Error durante la instalación: $($_.Exception.Message)"
        exit 1
    }
}

# Ejecutar función principal
Main