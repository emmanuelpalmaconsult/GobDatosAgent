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
                Log-Success "Docker Compose (standalone) encontrado: $composeVersion"
            } else {
                throw "Docker Compose standalone no detectado"
            }
        } catch {
            try {
                $composeVersionV2 = docker compose version 2>&1
                if ($composeVersionV2 -match "Docker Compose version") {
                    Log-Success "Docker Compose (v2 plugin) encontrado: $composeVersionV2"
                    $script:UseComposeV2 = $true
                } else {
                    throw "Docker Compose v2 no detectado"
                }
            } catch {
                Log-Error "Docker Compose no encontrado. Instalarlo como plugin de Docker o como standalone."
                exit 1
            }
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
    
    $composeCommand = if ($script:UseComposeV2) { "docker compose" } else { "docker-compose" }

    try {
        switch ($InstallMode) {
            "quick" {
                Log-Info "Iniciando PostgreSQL solamente..."
                Invoke-Expression "$composeCommand up -d analytics-db"
            }
            "full" {
                Log-Info "Iniciando todos los servicios..."
                Invoke-Expression "$composeCommand --profile admin --profile cache up -d"
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
    
    # Verificar que el archivo .env existe
    if (-not (Test-Path ".env")) {
        Log-Error "El archivo .env no existe. Ejecuta el script de nuevo."
        exit 1
    }
    
    # Verificar que los contenedores Docker están corriendo (si aplica)
    if ($UseDocker) {
        $running = docker ps --filter "name=investment-analytics" --format "{{.Names}}"
        if ($running -eq "investment-analytics") {
            Log-Success "Contenedor PostgreSQL 'investment-analytics' está corriendo."
        } else {
            Log-Warning "Contenedor PostgreSQL 'investment-analytics' no está corriendo."
        }
        
        if ($InstallMode -eq "full") {
            $pgadminRunning = docker ps --filter "name=investment-pgadmin" --format "{{.Names}}"
            if ($pgadminRunning -eq "investment-pgadmin") {
                Log-Success "Contenedor pgAdmin 'investment-pgadmin' está corriendo."
            } else {
                Log-Warning "Contenedor pgAdmin 'investment-pgadmin' no está corriendo."
            }
            
            $redisRunning = docker ps --filter "name=investment-redis" --format "{{.Names}}"
            if ($redisRunning -eq "investment-redis") {
                Log-Success "Contenedor Redis 'investment-redis' está corriendo."
            } else {
                Log-Warning "Contenedor Redis 'investment-redis' no está corriendo."
            }
        }
    }
    
    Log-Success "Verificación completada."
}

# Función principal
function Main {
    Test-Prerequisites
    
    if ($InstallMode -eq "check") {
        Log-Success "Verificación de prerequisitos completada."
        exit 0
    }
    
    New-EnvFile
    Install-PythonDependencies
    
    if ($UseDocker) {
        Start-DockerServices
    } else {
        Log-Warning "Opción -NoDocker seleccionada. Debes configurar la base de datos manualmente."
    }
    
    Test-Installation
    
    Log-Success "¡Configuración completada!"
    Log-Info "Para iniciar la aplicación, ejecuta: uvicorn app.main:app --reload"
}

# Ejecutar función principal
Main
