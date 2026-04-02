# 📊 PowerBI Dashboard Configuration Guide
## Investment Data Analysis Agent - Demo Mode

### 🎯 **CONFIGURACIÓN RÁPIDA**

#### **Servidor Demo Activo:**
- **URL Base**: `http://localhost:8001`
- **Documentación**: `http://localhost:8001/docs`
- **Modo**: Demo con 52 fondos sintéticos
- **AUM Total**: $397+ mil millones CLP

---

## 🔗 **ENDPOINTS PARA POWERBI**

### **1. 📈 OVERVIEW EJECUTIVO** 
```
URL: http://localhost:8001/api/v1/powerbi-demo/funds-overview
Método: GET
Uso: Tabla principal para drill-down por fondos
```

**Campos Clave:**
- `PshipID` - ID único del fondo (clave para relaciones)
- `FundName` - Nombre del fondo  
- `TotalAssets` - Assets bajo gestión (CLP)
- `YTDReturn` - Retorno año a la fecha (%)
- `FundType` - Tipo de fondo (Equity, Fixed Income, etc.)
- `RiskLevel` - Nivel de riesgo (1-5)

### **2. 💼 POSICIONES POR FONDO**
```
URL: http://localhost:8001/api/v1/powerbi-demo/fund-positions/{fund_id}
Método: GET
Uso: Drill-down desde overview hacia posiciones detalladas
```

**Campos Clave:**
- `SecurityName` - Nombre del instrumento
- `AssetClass` - Clase de activo
- `MarketValue` - Valor de mercado (CLP)
- `Weight` - Peso en el portafolio (%)
- `Sector` - Sector económico

### **3. 📊 PERFORMANCE HISTÓRICA**
```
URL: http://localhost:8001/api/v1/powerbi-demo/fund-performance/{fund_id}
Método: GET
Uso: Gráficos de series temporales de performance
```

**Campos Clave:**
- `Date` - Fecha (YYYY-MM-DD)
- `NAV` - Valor cuota del fondo
- `MonthlyReturn` - Retorno mensual (%)
- `AccumulatedReturn` - Retorno acumulado (%)
- `Benchmark` - Valor del benchmark

### **4. 🎯 KPIs EJECUTIVOS**
```
URL: http://localhost:8001/api/v1/powerbi-demo/kpis-dashboard
Método: GET
Uso: Métricas principales para dashboard ejecutivo
```

**Estructura KPIs:**
```json
{
  "aum_total": {"value": 397000000000, "change_pct": 5.2},
  "average_return": {"value": 6.78, "benchmark": 6.5},
  "active_funds": {"value": 52, "percentage": 100},
  "risk_score": {"portfolio_risk": 3.9, "risk_level": "Medium"},
  "top_fund": {"name": "Fondo Epsilon 15", "return": 23.8}
}
```

### **5. 📋 ANALYTICS AGREGADOS**
```
URL: http://localhost:8001/api/v1/powerbi-demo/portfolio-analytics
Método: GET
Uso: Distribuciones y análisis agregado del portafolio
```

---

## 🛠 **CONFIGURACIÓN EN POWERBI DESKTOP**

### **Paso 1: Conectar Fuente de Datos**
1. **Obtener Datos** → **Web** 
2. **URL**: `http://localhost:8001/api/v1/powerbi-demo/funds-overview`
3. **Ok** → **Transformar Datos**

### **Paso 2: Configurar Consultas Principales**

#### **Query 1: Funds Overview**
```powerquery
let
    Source = Json.Document(Web.Contents("http://localhost:8001/api/v1/powerbi-demo/funds-overview")),
    data = Source[data],
    #"Converted to Table" = Table.FromList(data, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    #"Expanded Column1" = Table.ExpandRecordColumn(#"Converted to Table", "Column1", 
        {"PshipID", "FundName", "FundType", "TotalAssets", "YTDReturn", "RiskLevel", "Currency"})
in
    #"Expanded Column1"
```

#### **Query 2: KPIs Dashboard**
```powerquery
let
    Source = Json.Document(Web.Contents("http://localhost:8001/api/v1/powerbi-demo/kpis-dashboard")),
    kpis = Source[kpis],
    #"Converted to Table" = Record.ToTable(kpis)
in
    #"Converted to Table"
```

### **Paso 3: Configurar Drill-Down**

#### **Relaciones:**
- **Tabla Principal**: Funds Overview (`PshipID` como clave)
- **Drill-Down**: Fund Positions (usar parámetro `PshipID` en URL)
- **Performance**: Fund Performance (usar parámetro `PshipID` en URL)

#### **Parámetros Dinámicos:**
```powerquery
// Crear parámetro para Fund ID seleccionado
let
    SelectedFundID = 1, // Esto se actualizará dinámicamente
    Source = Json.Document(Web.Contents("http://localhost:8001/api/v1/powerbi-demo/fund-positions/" & Number.ToText(SelectedFundID)))
in
    Source
```

---

## 🎨 **DISEÑO DEL DASHBOARD**

### **Página 1: Executive Overview**
```
┌─────────────────┬─────────────────┐
│   KPI CARDS     │  AUM BY TYPE    │
│  Total AUM      │   (Pie Chart)   │
│  Avg Return     │                 │  
│  Active Funds   │                 │
└─────────────────┼─────────────────┤
│           FUNDS TABLE             │
│  (Click for drill-down)           │
│  PshipID | Name | Assets | Return │
└───────────────────────────────────┘
```

### **Página 2: Fund Detail (Drill-Down)**
```
┌─────────────────┬─────────────────┐
│ FUND HEADER     │ PERFORMANCE     │
│ Name + Assets   │ (Line Chart)    │
├─────────────────┼─────────────────┤
│   POSITIONS     │   SECTOR        │
│   (Table)       │ ALLOCATION      │
│                 │ (Donut Chart)   │
└─────────────────┴─────────────────┘
```

### **Elementos Visuales Recomendados:**

#### **KPI Cards:**
- Total AUM (formato moneda CLP)
- Average YTD Return (formato porcentaje)
- Number of Active Funds
- Portfolio Risk Score

#### **Charts:**
- **Pie Chart**: AUM by Fund Type
- **Bar Chart**: Top 10 Funds by Performance  
- **Line Chart**: Historical Performance (drill-down)
- **Donut Chart**: Asset Allocation by Sector
- **Table**: Fund Positions (drill-down)

---

## ⚡ **REFRESH & ACTUALIZACIÓN**

### **Configuración de Refresh:**
```powerbi
// En Data Source Settings
Source = Web.Contents("http://localhost:8001/", [
    RelativePath = "api/v1/powerbi-demo/funds-overview",
    Headers = [
        #"Content-Type" = "application/json",
        #"Accept" = "application/json"
    ]
])
```

### **Refresh Schedule:**
- **Manual Refresh**: Inmediato
- **Scheduled Refresh**: Cada 15 minutos (demo)
- **Real-time**: Configurar cuando esté en producción

---

## 🔄 **DRILL-DOWN CONFIGURATION**

### **Configurar Acción de Drill-Down:**
1. **Seleccionar tabla de fondos**
2. **Format** → **Interactions** 
3. **Add Action**: "Drill-down to positions"
4. **Target**: Nueva página
5. **Pass Parameter**: `PshipID`

### **Parámetros URL Dinámicos:**
```powerquery
let
    BaseURL = "http://localhost:8001/api/v1/powerbi-demo/fund-positions/",
    SelectedFund = [PshipID], // Viene del drill-down
    FullURL = BaseURL & Number.ToText(SelectedFund),
    Source = Json.Document(Web.Contents(FullURL))
in
    Source[positions]
```

---

## 🎯 **TESTING & VALIDACIÓN**

### **Checklist de Validación:**
- [ ] ✅ Conexión exitosa a endpoints
- [ ] ✅ 52 fondos cargados correctamente  
- [ ] ✅ Drill-down funcionando
- [ ] ✅ KPIs actualizándose
- [ ] ✅ Charts renderizando datos
- [ ] ✅ Refresh manual funcionando

### **URLs de Test:**
```bash
# Test básico
curl http://localhost:8001/api/v1/health

# Test fondos
curl http://localhost:8001/api/v1/powerbi-demo/funds-overview

# Test posiciones
curl http://localhost:8001/api/v1/powerbi-demo/fund-positions/1

# Test KPIs
curl http://localhost:8001/api/v1/powerbi-demo/kpis-dashboard
```

---

## 📞 **TROUBLESHOOTING**

### **Problemas Comunes:**
1. **Error de conexión**: Verificar que servidor esté en `localhost:8001`
2. **Datos vacíos**: Confirmar formato JSON en endpoints
3. **Drill-down no funciona**: Verificar parámetros en URLs
4. **Refresh lento**: Optimizar queries o reducir timeout

### **Logs y Debug:**
- **Servidor logs**: Terminal donde corre `uvicorn`
- **PowerBI logs**: Query diagnostics en PowerBI Desktop
- **API docs**: `http://localhost:8001/docs` para test manual

---

**🎉 ¡Dashboard PowerBI listo para desarrollo!** 
**Todos los endpoints demo funcionando con datos realistas de 52 fondos de inversión** 🚀