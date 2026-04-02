# 📊 PowerBI Dashboard Setup - Investment Data Analysis Agent
## Configuración Paso a Paso con Datos REALES de SQL Server

### 🎯 **ESTADO ACTUAL CONFIRMADO:**
- ✅ **52 fondos reales** de SQL Server GD_EG_001  
- ✅ **PshipIDs correctos**: ORANGE=3, PIONERO=5, MONEDA RV=7
- ✅ **4 endpoints optimizados** para PowerBI listos
- ✅ **Drill-down funcionando** con datos reales

---

## 📋 **FASE 1: CONEXIÓN DE DATOS**

### **Paso 1.1: Abrir PowerBI Desktop** 
1. Iniciar **PowerBI Desktop**
2. Seleccionar **"Obtener datos"** 
3. Elegir **"Web"** como origen de datos

### **Paso 1.2: Configurar las 4 Conexiones Web**

#### **🔗 Conexión 1: Fund Overview**  
```
URL: http://localhost:8000/api/v1/powerbi/funds
Nombre de tabla: FundOverview
```

#### **🔗 Conexión 2: Fund Details (Ejemplo con ORANGE)** 
```
URL: http://localhost:8000/api/v1/powerbi/fund-details/3
Nombre de tabla: FundDetails
```

#### **🔗 Conexión 3: Fund Positions (Ejemplo con ORANGE)**
```
URL: http://localhost:8000/api/v1/powerbi/fund-positions/3  
Nombre de tabla: FundPositions
```

#### **🔗 Conexión 4: Fund KPIs (Ejemplo con ORANGE)**
```
URL: http://localhost:8000/api/v1/powerbi/fund-kpis/3
Nombre de tabla: FundKPIs
```

### **Paso 1.3: Transformar Datos**
1. En **Editor de Power Query**:
   - FundOverview: **No requiere transformación**
   - FundDetails: Cambiar tipo de columna **Date** a Date
   - FundPositions: Verificar tipos numéricos 
   - FundKPIs: Verificar tipos numéricos
2. **Aplicar** cambios y **Cerrar**

---

## 📊 **FASE 2: CONFIGURAR RELACIONES**

### **Paso 2.1: Crear Relaciones en Vista Modelo**
1. Ir a **Vista de Modelo** (ícono de diagrama)
2. Crear las siguientes relaciones:

```
FundOverview[PshipID] ←→ FundDetails[PshipID] (Uno a Muchos)
FundOverview[PshipID] ←→ FundPositions[PshipID] (Uno a Muchos)  
FundOverview[PshipID] ←→ FundKPIs[PshipID] (Uno a Muchos)
```

### **Paso 2.2: Configurar Filtros**
- Establecer **FundOverview** como tabla principal
- Configurar filtrado cruzado **bidireccional** en todas las relaciones

---

## 📈 **FASE 3: CREAR VISUALIZACIONES**

### **🏠 Página 1: OVERVIEW DASHBOARD** 

#### **Visual 1: Resumen de Fondos (Card Visual)**
- **Fuente**: FundOverview
- **Campo**: Count of PshipID  
- **Título**: "Total Fondos Activos"

#### **Visual 2: Total Assets (Card Visual)**
- **Fuente**: FundOverview
- **Campo**: Sum of TotalAssets
- **Formato**: Billones CLP
- **Título**: "Total Assets Under Management"

#### **Visual 3: Fund Performance Table**
- **Tipo**: Table
- **Fuente**: FundOverview
- **Campos**: FundName, TotalAssets, YTDReturn, RiskLevel
- **Configurar**: Click para drill-down

#### **Visual 4: Asset Class Distribution (Pie Chart)**
- **Fuente**: FundOverview  
- **Legend**: AssetClass
- **Values**: Count of PshipID

### **🔍 Página 2: FUND DETAILS (Drill-Down)**

#### **Visual 5: NAV Evolution (Line Chart)**
- **Fuente**: FundDetails
- **Axis**: Date
- **Values**: NAV
- **Título**: "NAV Evolution - [FundName]"

#### **Visual 6: Daily Returns (Bar Chart)**
- **Fuente**: FundDetails
- **Axis**: Date  
- **Values**: DailyReturn
- **Colores**: Conditional (positive=green, negative=red)

### **📋 Página 3: POSITIONS ANALYSIS** 

#### **Visual 7: Top Holdings (Bar Chart)**
- **Fuente**: FundPositions
- **Axis**: AssetName
- **Values**: MarketValue
- **Sort**: Descending by MarketValue

#### **Visual 8: Asset Allocation (Treemap)**
- **Group**: AssetType
- **Values**: MarketValue
- **Colors**: By AssetType

### **📊 Página 4: KPIs & PERFORMANCE**

#### **Visual 9: Performance Metrics (Multi-row Card)**
- **Fuente**: FundKPIs
- **Fields**: TotalReturn1Y, TotalReturn3Y, TotalReturn5Y
- **Formato**: Percentage with 2 decimals

#### **Visual 10: Risk Metrics (Gauge Charts)**
- **Volatility**: Min=0, Max=30, Target=15
- **Sharpe Ratio**: Min=-1, Max=3, Target=1.5
- **Beta**: Min=0, Max=2, Target=1

---

## ⚡ **FASE 4: CONFIGURAR DRILL-DOWN DINÁMICO**

### **Paso 4.1: Configurar Navigation**
1. **En Fund Performance Table**:
   - Click derecho → **Drill through** → **Enable**
   - Target page: **Fund Details**
   - Drill through field: **PshipID**

### **Paso 4.2: Dynamic URL Parameters** 
Para hacer drill-down dinámico con diferentes fondos:

```dax
Dynamic URL = 
"http://localhost:8000/api/v1/powerbi/fund-details/" & 
SELECTEDVALUE(FundOverview[PshipID])
```

### **Paso 4.3: Configurar Filtros de Página**
- **Fund Details page**: Filtro por FundName  
- **Positions page**: Filtro por FundName
- **KPIs page**: Filtro por FundName

---

## 🔄 **FASE 5: AUTOMATIZACIÓN Y REFRESH**

### **Paso 5.1: Configurar Refresh**
1. **Archivo** → **Opciones y configuración** → **Configuración de origen de datos**
2. Set refresh interval: **15 minutes**
3. Enable **automatic refresh**

### **Paso 5.2: Error Handling**
```dax
Error Handling = 
IF(
    ISBLANK(SELECTEDVALUE(FundOverview[PshipID])),
    "Select a fund to view details",
    "Data loaded successfully"
)
```

---

## ✅ **RESULTADO ESPERADO:**
1. **Página Overview**: 52 fondos reales listados
2. **Click en ORANGE**: Drill-down a detalles específicos  
3. **Navigation fluida**: Entre las 4 páginas
4. **Data refreshes**: Automático cada 15 minutos
5. **Real-time**: Datos actualizados de SQL Server

---

## 🚀 **SIGUIENTE PASO:**
¿Tienes PowerBI Desktop abierto? ¿Prefieres que te guíe paso a paso mientras lo configuras?