"""
🚀 Investment Data Analysis Agent - Startup Script
=================================================

Script para inicializar y verificar el sistema completo:
- FastAPI Backend
- Conexión SQL Server
- Dashboard PowerBI
- AI Analysis Engine

Author: Investment Data Analysis Agent  
Version: 1.0 - Production Ready
"""

import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║  🏦 INVESTMENT DATA ANALYSIS AGENT                           ║
║     Business Intelligence + AI Investment Analysis          ║
║                                                              ║
║  🎯 Features:                                               ║
║     • 55 Active Funds Analysis                              ║
║     • PowerBI Dashboard Integration                          ║
║     • AI-Powered Insights                                   ║
║     • SQL Server Data Source                                ║
║     • 4-Level Drill-Down Reports                            ║
║                                                              ║
║  🚀 Starting System...                                      ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_prerequisites():
    """Check system prerequisites"""
    print("\n🔍 Checking Prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print("❌ Python 3.8+ required")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required files
    required_files = [
        "app/main.py",
        "app/services/dashboard.py",
        "ai_investment_analysis.py",
        "app/database/sql_server_manager.py",
        ".env"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            return False
    
    # Check .env configuration
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
            required_vars = ['SQL_SERVER', 'SQL_DATABASE', 'SQL_USERNAME', 'SQL_PASSWORD']
            for var in required_vars:
                if var in env_content:
                    print(f"✅ Environment: {var}")
                else:
                    print(f"⚠️ Environment: {var} not configured")
    
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing Dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def start_fastapi_server():
    """Start FastAPI server in background"""
    print("\n🚀 Starting FastAPI Server...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        print("⏳ Waiting for server startup...")
        time.sleep(5)  # Give server time to start
        
        return process
    except Exception as e:
        print(f"❌ Failed to start FastAPI: {e}")
        return None

async def test_api_health():
    """Test API health and endpoints"""
    import aiohttp
    
    print("\n🏥 Testing API Health...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test base endpoint
            async with session.get("http://localhost:8000/") as response:
                if response.status == 200:
                    print("✅ API Base endpoint working")
                else:
                    print(f"⚠️ API Base returned HTTP {response.status}")
            
            # Test dashboard overview
            async with session.get("http://localhost:8000/dashboard/overview") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Dashboard Overview: {len(data)} funds found")
                else:
                    print(f"⚠️ Dashboard Overview returned HTTP {response.status}")
            
            # Test fund details
            async with session.get("http://localhost:8000/dashboard/fund/3") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Fund Details: {len(data)} records")
                else:
                    print(f"⚠️ Fund Details returned HTTP {response.status}")
            
            return True
            
    except Exception as e:
        print(f"❌ API Health Check failed: {e}")
        return False

def show_access_info():
    """Show access information"""
    print("\n" + "="*60)
    print("🎉 SYSTEM READY!")
    print("="*60)
    print("\n📊 ACCESS INFORMATION:")
    print("• FastAPI Docs:     http://localhost:8000/docs")
    print("• Dashboard Base:   http://localhost:8000/dashboard/overview")
    print("• Health Check:     http://localhost:8000/")
    
    print("\n🎯 POWERBI ENDPOINTS:")
    print("• Overview:         http://localhost:8000/dashboard/overview")
    print("• Fund Details:     http://localhost:8000/dashboard/fund/{id}")
    print("• Positions:        http://localhost:8000/dashboard/fund/{id}/positions")
    print("• KPIs Summary:     http://localhost:8000/dashboard/kpis/summary")
    
    print("\n📚 DOCUMENTATION:")
    print("• PowerBI Guide:    POWERBI_INTEGRATION.md")
    print("• API Testing:      python test_powerbi_integration.py")
    
    print("\n🔧 NEXT STEPS:")
    print("1. Review API documentation at /docs")
    print("2. Test endpoints with test_powerbi_integration.py")
    print("3. Connect PowerBI using POWERBI_INTEGRATION.md")
    print("4. Configure drill-down dashboards")
    
    print("\n" + "="*60)

async def main():
    """Main startup function"""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please fix issues and retry.")
        return
    
    # Install dependencies if needed
    print("\n⏳ Ensuring dependencies are installed...")
    install_dependencies()
    
    # Start FastAPI server
    server_process = start_fastapi_server()
    if not server_process:
        print("\n❌ Failed to start FastAPI server")
        return
    
    try:
        # Test API health
        api_healthy = await test_api_health()
        
        if api_healthy:
            show_access_info()
            
            # Keep server running
            print("\n⌨️  Press Ctrl+C to stop the server")
            while True:
                await asyncio.sleep(1)
        else:
            print("\n❌ API health check failed")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped successfully")
    except Exception as e:
        print(f"\n🚨 Unexpected error: {e}")
        server_process.terminate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n🚨 Critical error: {e}")
        sys.exit(1)