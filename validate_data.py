#!/usr/bin/env python3
"""
🔍 INVESTMENT DATA VALIDATOR
Valida y genera informe de datos antes de usar en Power BI
"""

import json
import requests
import pandas as pd
from datetime import datetime
import os
from typing import Dict, List, Optional

class InvestmentDataValidator:
    """Valida datos del Investment Data Analysis Agent"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "server_status": None,
            "data_quality": {},
            "summary_stats": {},
            "recommendations": []
        }
    
    def check_server_health(self) -> bool:
        """Verifica si el servidor está funcionando"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.report["server_status"] = "✅ Online" if response.status_code == 200 else "❌ Error"
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            self.report["server_status"] = f"❌ Offline: {str(e)}"
            return False
    
    def validate_funds_data(self) -> Optional[List[Dict]]:
        """Valida datos de fondos"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/powerbi/funds", timeout=10)
            
            if response.status_code != 200:
                self.report["data_quality"]["funds"] = f"❌ HTTP {response.status_code}"
                return None
            
            funds_data = response.json()
            
            # Validaciones
            validations = {
                "total_funds": len(funds_data),
                "has_required_fields": all(
                    key in fund for fund in funds_data 
                    for key in ["FundName", "TotalAssets", "YTDReturn"]
                ),
                "positive_aum": sum(1 for fund in funds_data if fund.get("TotalAssets", 0) > 0),
                "valid_returns": sum(1 for fund in funds_data if isinstance(fund.get("YTDReturn"), (int, float))),
                "unique_funds": len(set(fund.get("FundName", "") for fund in funds_data)),
                "asset_classes": list(set(fund.get("AssetClass", "Unknown") for fund in funds_data)),
                "risk_levels": list(set(fund.get("RiskLevel", "Unknown") for fund in funds_data))
            }
            
            self.report["data_quality"]["funds"] = validations
            
            # Estadísticas resumidas  
            if funds_data:
                df = pd.DataFrame(funds_data)
                stats = {
                    "total_aum": df["TotalAssets"].sum() if "TotalAssets" in df.columns else 0,
                    "avg_return": df["YTDReturn"].mean() if "YTDReturn" in df.columns else 0,
                    "best_performer": df["YTDReturn"].max() if "YTDReturn" in df.columns else 0,
                    "worst_performer": df["YTDReturn"].min() if "YTDReturn" in df.columns else 0,
                    "return_std": df["YTDReturn"].std() if "YTDReturn" in df.columns else 0
                }
                self.report["summary_stats"]["funds"] = stats
            
            return funds_data
            
        except Exception as e:
            self.report["data_quality"]["funds"] = f"❌ Error: {str(e)}"
            return None
    
    def validate_fund_details(self) -> bool:
        """Valida endpoint de detalles de fondos"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/powerbi/fund-details-all", timeout=10)
            
            if response.status_code != 200:
                self.report["data_quality"]["fund_details"] = f"❌ HTTP {response.status_code}"
                return False
            
            details_data = response.json()
            validations = {
                "total_records": len(details_data),
                "has_positions": any("positions" in detail for detail in details_data),
                "has_cash_flows": any("cash_flows" in detail for detail in details_data)
            }
            
            self.report["data_quality"]["fund_details"] = validations
            return True
            
        except Exception as e:
            self.report["data_quality"]["fund_details"] = f"❌ Error: {str(e)}"
            return False
    
    def check_data_freshness(self, funds_data: List[Dict]) -> None:
        """Verifica qué tan actualizados están los datos"""
        if not funds_data:
            return
        
        # Buscar campos de fecha
        date_fields = []
        for fund in funds_data[:3]:  # Revisar primeros 3 fondos
            for key, value in fund.items():
                if "date" in key.lower() or "time" in key.lower():
                    date_fields.append((key, value))
        
        self.report["data_quality"]["date_fields"] = date_fields
    
    def generate_recommendations(self) -> None:
        """Genera recomendaciones basadas en validación"""
        recommendations = []
        
        # Server status
        if self.report["server_status"] and "Offline" in self.report["server_status"]:
            recommendations.append("🚨 Servidor offline - Usar datos demo para desarrollo")
        
        # Data quality
        funds_quality = self.report["data_quality"].get("funds", {})
        
        if isinstance(funds_quality, dict):
            if funds_quality.get("total_funds", 0) == 0:
                recommendations.append("⚠️ No hay datos de fondos - Verificar conexión SQL Server")
            
            if not funds_quality.get("has_required_fields", True):
                recommendations.append("⚠️ Faltan campos requeridos en datos de fondos")
            
            if funds_quality.get("unique_funds", 0) != funds_quality.get("total_funds", 0):
                recommendations.append("⚠️ Fondos duplicados detectados")
        
        # Performance stats
        fund_stats = self.report["summary_stats"].get("funds", {})
        if fund_stats:
            if fund_stats.get("avg_return", 0) < 0:
                recommendations.append("📊 Rendimiento promedio negativo - Revisar estrategia")
            
            if fund_stats.get("return_std", 0) > 0.2:
                recommendations.append("📈 Alta volatilidad detectada - Considerar gestión de riesgo")
        
        if not recommendations:
            recommendations.append("✅ Datos validados correctamente - Proceder con Power BI")
        
        self.report["recommendations"] = recommendations
    
    def save_report(self, filename: str = "data_validation_report.json") -> None:
        """Guarda el informe de validación"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"📄 Informe guardado: {filename}")
    
    def print_summary(self) -> None:
        """Imprime resumen ejecutivo"""
        print("\n" + "="*60)
        print("🔍 INVESTMENT DATA VALIDATION REPORT")
        print("="*60)
        
        print(f"⏰ Timestamp: {self.report['timestamp']}")
        print(f"🌐 Server Status: {self.report['server_status']}")
        
        # Data Quality Summary
        print(f"\n📊 DATA QUALITY:")
        for endpoint, quality in self.report['data_quality'].items():
            if isinstance(quality, dict):
                total = quality.get('total_funds', quality.get('total_records', 'N/A'))
                print(f"  {endpoint}: {total} registros")
            else:
                print(f"  {endpoint}: {quality}")
        
        # Summary Stats
        if 'funds' in self.report['summary_stats']:
            stats = self.report['summary_stats']['funds']
            print(f"\n💰 PORTFOLIO SUMMARY:")
            print(f"  Total AUM: ${stats.get('total_aum', 0):,.0f}")
            print(f"  Average Return: {stats.get('avg_return', 0):.2%}")
            print(f"  Best Performer: {stats.get('best_performer', 0):.2%}")
            print(f"  Worst Performer: {stats.get('worst_performer', 0):.2%}")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        for rec in self.report['recommendations']:
            print(f"  {rec}")
        
        print("="*60)

def main():
    """Función principal"""
    print("🚀 Iniciando validación de datos de inversión...")
    
    validator = InvestmentDataValidator()
    
    # 1. Verificar servidor
    print("1️⃣ Verificando estado del servidor...")
    server_ok = validator.check_server_health()
    
    if not server_ok:
        print("⚠️ Servidor no disponible - Usando datos demo")
        # Aquí podrías cargar datos demo si el servidor está offline
    
    # 2. Validar datos de fondos
    print("2️⃣ Validando datos de fondos...")
    funds_data = validator.validate_funds_data()
    
    # 3. Validar detalles de fondos
    print("3️⃣ Validando detalles de fondos...")
    validator.validate_fund_details()
    
    # 4. Verificar frescura de datos
    print("4️⃣ Verificando frescura de datos...")
    validator.check_data_freshness(funds_data)
    
    # 5. Generar recomendaciones
    print("5️⃣ Generando recomendaciones...")
    validator.generate_recommendations()
    
    # 6. Mostrar y guardar informe
    validator.print_summary()
    validator.save_report()
    
    print("\n✅ Validación completada!")
    print("📋 Revisar 'data_validation_report.json' para detalles completos")

if __name__ == "__main__":
    main()