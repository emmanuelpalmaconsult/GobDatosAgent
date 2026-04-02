"""
🧪 Test Script para PowerBI Dashboard Integration
=================================================

Este script valida que todos los endpoints del dashboard estén funcionando
correctamente antes de conectar PowerBI.

Author: Investment Data Analysis Agent
Version: 1.0
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

class DashboardTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    async def test_endpoint(self, session: aiohttp.ClientSession, 
                           endpoint: str, description: str) -> Dict[str, Any]:
        """Test individual endpoint"""
        try:
            start_time = datetime.now()
            async with session.get(f"{self.base_url}{endpoint}") as response:
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "endpoint": endpoint,
                        "description": description,
                        "status": "✅ PASS",
                        "response_time": f"{response_time:.2f}s",
                        "record_count": len(data) if isinstance(data, list) else 1,
                        "data_sample": data[:2] if isinstance(data, list) else str(data)[:100] + "..."
                    }
                else:
                    return {
                        "endpoint": endpoint,
                        "description": description,
                        "status": f"❌ FAIL (HTTP {response.status})",
                        "response_time": f"{response_time:.2f}s",
                        "record_count": 0,
                        "data_sample": await response.text()
                    }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "description": description,
                "status": f"🚨 ERROR: {str(e)}",
                "response_time": "N/A",
                "record_count": 0,
                "data_sample": str(e)
            }

    async def run_all_tests(self) -> None:
        """Run comprehensive dashboard tests"""
        
        # Test endpoints definition
        test_endpoints = [
            # Level 1: Overview
            ("/dashboard/overview", "📊 Level 1: Fund Overview"),
            ("/dashboard/overview?date_filter=2026-03-31", "📊 Level 1: Overview con filtro fecha"),
            
            # Level 2: Fund Details (usando fund_id = 3 como ejemplo)
            ("/dashboard/fund/3", "📈 Level 2: Fund Details para ORANGE"),
            ("/dashboard/fund/3?start_date=2025-01-01&end_date=2026-03-31", "📈 Level 2: Fund Details con rango"),
            
            # Level 3: Positions
            ("/dashboard/fund/3/positions", "🎯 Level 3: Posiciones de ORANGE"),
            ("/dashboard/fund/3/positions?date_filter=2026-03-31&min_weight=0.01", "🎯 Level 3: Posiciones filtradas"),
            
            # Level 4: KPIs
            ("/dashboard/kpis/summary", "📊 Level 4: KPIs Resumen"),
            ("/dashboard/kpis/summary?date_filter=2026-03-31", "📊 Level 4: KPIs con filtro"),
            
            # Comparativo
            ("/dashboard/compare/performance", "⚖️ Comparativo: Performance"),
            ("/dashboard/compare/performance?funds=3,4,5&date_filter=2026-03-31", "⚖️ Comparativo: Performance múltiple"),
            
            # Health Check
            ("/", "❤️ Health Check: API Base"),
        ]
        
        print("🚀 Iniciando Tests del Dashboard PowerBI...")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # Test each endpoint
            for endpoint, description in test_endpoints:
                result = await self.test_endpoint(session, endpoint, description)
                self.test_results.append(result)
                
                # Print real-time results
                print(f"{result['status']} {result['description']}")
                print(f"   ⏱️ Tiempo: {result['response_time']} | 📊 Registros: {result['record_count']}")
                
                if "PASS" in result['status']:
                    print(f"   🔍 Muestra: {str(result['data_sample'])[:100]}...")
                else:
                    print(f"   ⚠️ Error: {result['data_sample']}")
                print()
        
        await self.generate_report()
    
    async def generate_report(self) -> None:
        """Generate comprehensive test report"""
        
        passed_tests = len([r for r in self.test_results if "PASS" in r['status']])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("=" * 60)
        print("📋 REPORTE FINAL DE TESTING")
        print("=" * 60)
        print(f"✅ Tests Pasados: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Failed tests detail
        failed_tests = [r for r in self.test_results if "PASS" not in r['status']]
        if failed_tests:
            print("\n❌ TESTS FALLIDOS:")
            for test in failed_tests:
                print(f"   • {test['endpoint']} - {test['data_sample']}")
        
        # Performance analysis
        avg_response_time = sum([float(r['response_time'].replace('s', '')) 
                                for r in self.test_results 
                                if r['response_time'] != 'N/A']) / len(self.test_results)
        
        print(f"\n⚡ Performance Promedio: {avg_response_time:.2f}s")
        
        # PowerBI Readiness
        print("\n🎯 ESTADO POWERBI:")
        if success_rate >= 90:
            print("   ✅ LISTO PARA POWERBI - Todos los endpoints principales funcionan")
        elif success_rate >= 70:
            print("   ⚠️ PARCIALMENTE LISTO - Revisar endpoints fallidos")
        else:
            print("   ❌ NO LISTO - Múltiples problemas de conectividad")
        
        # Next steps
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Verificar que FastAPI esté corriendo en localhost:8000")
        print("   2. Confirmar conexión a SQL Server")
        print("   3. Validar datos de fondos en tabla GD_Fondos")
        print("   4. Si todo está OK → Conectar PowerBI usando POWERBI_INTEGRATION.md")

async def test_specific_fund_data():
    """Test specific fund data to validate real numbers"""
    print("\n🔬 TESTING DATOS ESPECÍFICOS DE FONDOS")
    print("-" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test Overview for data validation
            async with session.get(f"{base_url}/dashboard/overview") as response:
                if response.status == 200:
                    funds = await response.json()
                    print(f"📊 Total Fondos Encontrados: {len(funds)}")
                    
                    # Show top 5 funds with details
                    for i, fund in enumerate(funds[:5]):
                        print(f"   {i+1}. {fund.get('fund_name', 'N/A')}: ${fund.get('total_assets', 0):,.0f}")
                        print(f"      YTD Return: {fund.get('ytd_return', 0):.2f}%")
                        print(f"      Risk Level: {fund.get('risk_level', 'N/A')}")
                        print()
                    
                    # Test specific fund drill-down
                    if funds:
                        fund_id = funds[0].get('fund_id')
                        print(f"🔍 Testing drill-down para Fund ID: {fund_id}")
                        
                        async with session.get(f"{base_url}/dashboard/fund/{fund_id}") as detail_response:
                            if detail_response.status == 200:
                                details = await detail_response.json()
                                print(f"   ✅ Fund Details: {len(details)} registros históricos")
                            else:
                                print(f"   ❌ Fund Details failed: HTTP {detail_response.status}")
                        
                        async with session.get(f"{base_url}/dashboard/fund/{fund_id}/positions") as pos_response:
                            if pos_response.status == 200:
                                positions = await pos_response.json()
                                print(f"   ✅ Positions: {len(positions)} posiciones encontradas")
                            else:
                                print(f"   ❌ Positions failed: HTTP {pos_response.status}")
                else:
                    print(f"❌ No se pudo conectar al overview: HTTP {response.status}")
                    
    except Exception as e:
        print(f"🚨 Error en testing específico: {e}")

async def main():
    """Main testing function"""
    print("🎯 Investment Data Analysis Agent - Dashboard Testing")
    print("Validando conectividad para PowerBI Integration...")
    print()
    
    # Initialize tester
    tester = DashboardTester()
    
    # Run all endpoint tests
    await tester.run_all_tests()
    
    # Test specific fund data
    await test_specific_fund_data()
    
    print("\n" + "="*60)
    print("🎉 TESTING COMPLETADO!")
    print("Ver POWERBI_INTEGRATION.md para instrucciones de conexión")
    print("="*60)

if __name__ == "__main__":
    # Run the async testing
    asyncio.run(main())