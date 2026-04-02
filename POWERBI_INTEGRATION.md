# 📊 PowerBI Dashboard Integration Guide

## 🚀 Conexión PowerBI con Investment Data Analysis Agent

### 📋 **Endpoints Disponibles para Dashboard**

#### 🎯 **Jerarquía de Drill-Down**

1. **NIVEL 1 - Vista General**: `/dashboard/overview`
2. **NIVEL 2 - Detalle Fondo**: `/dashboard/fund/{fund_id}`
3. **NIVEL 3 - Posiciones**: `/dashboard/fund/{fund_id}/positions`
4. **NIVEL 4 - KPIs**: `/dashboard/kpis/summary`
5. **COMPARATIVO**: `/dashboard/compare/performance`

---

## 🔧 **Configuración en PowerBI**

### 1. **Conectar Fuente de Datos**

```powerbi
Origen de Datos: Web
URL Base: http://localhost:8000
Autenticación: Ninguna (desarrollo)
```

### 2. **URLs Específicas por Nivel**

#### **📊 Overview Dashboard (Nivel 1)**
```
http://localhost:8000/dashboard/overview?date_filter=2026-03-31
```
**Campos Principales:**
- `fund_id` (Relación)
- `fund_name` (Título)
- `total_assets` (Métrica)
- `ytd_return` (Performance)
- `risk_level` (Filtro)
- `asset_class` (Categorización)

#### **📈 Fund Details (Nivel 2)**
```
http://localhost:8000/dashboard/fund/3?start_date=2025-01-01&end_date=2026-03-31
```
**Campos Principales:**
- `date` (Eje X - Temporal)
- `nav` (Métrica Principal)
- `total_assets` (Área/Volumen)
- `ytd_return` (Performance)
- `unrealized_pnl` (P&L)

#### **🎯 Positions (Nivel 3)**
```
http://localhost:8000/dashboard/fund/3/positions?date_filter=2026-03-31&min_weight=0.01
```
**Campos Principales:**
- `instrument_name` (Etiquetas)
- `market_value` (Tamaño)
- `weight_percent` (Porcentaje)
- `unrealized_pnl` (Color/Performance)
- `asset_class` (Filtro)

#### **📊 KPIs Summary**
```
http://localhost:8000/dashboard/kpis/summary?date_filter=2026-03-31
```
**Métricas de Cards:**
- `total_funds`
- `total_aum`
- `avg_ytd_return`
- `total_positions`

---

## 🎨 **Diseño de Dashboard**

### **Página 1: Executive Overview**
```
┌─────────────────────────────────────────────────┐
│  🏦 Investment Portfolio Dashboard              │
├─────────────────────────────────────────────────┤
│ [55 Funds] [₿669B AUM] [📈3.35%] [200 Pos]    │
├─────────────────────────────────────────────────┤
│                                                 │
│  📊 Fund Performance (Scatter Chart)           │
│  X: Total Assets | Y: YTD Return               │
│  Size: Position Count | Color: Risk Level      │
│  🔍 DRILL-DOWN: Click → Fund Details           │
│                                                 │
├─────────────────────────────────────────────────┤
│ 📈 Top Performers     │ ⚠️ Risk Alerts         │
│ 1. PIONERO: 6.60%     │ • High Vol: ALTURAS II │
│ 2. ORANGE: 0.11%      │ • Drawdown: MONEDA GSI │
│ 3. MONEDA RV: -       │ • Concentration Risk   │
└─────────────────────────────────────────────────┘
```

### **Página 2: Fund Details (Drill-Down)**
```
┌─────────────────────────────────────────────────┐
│ 📊 [FUND_NAME] - Detailed Analysis             │
├─────────────────────────────────────────────────┤
│                                                 │
│  📈 NAV Evolution (Line Chart)                 │
│  Time Series: NAV, Total Assets, Returns       │
│                                                 │
├─────────────────────────────────────────────────┤
│ 🎯 Top Holdings (Treemap)      │ 📊 Metrics   │
│ Size: Market Value              │ YTD: X.XX%   │
│ Color: Unrealized P&L           │ NAV: $X,XXX  │
│ 🔍 DRILL-DOWN: Click → Positions│ Assets: $XB  │
└─────────────────────────────────────────────────┘
```

### **Página 3: Position Analysis (Drill-Down)**
```
┌─────────────────────────────────────────────────┐
│ 🎯 [FUND_NAME] - Position Details              │
├─────────────────────────────────────────────────┤
│                                                 │
│  📊 Asset Allocation (Donut Chart)             │
│  By Asset Class + Weight                       │
│                                                 │
├─────────────────────────────────────────────────┤
│ 📋 Position Table              │ 📈 P&L Chart │
│ Instrument | MV | Weight | P&L │ Winners/Losers│
│ [Filter by Asset Class]        │              │
└─────────────────────────────────────────────────┘
```

---

## ⚙️ **Configuración de Drill-Down en PowerBI**

### **Step 1: Crear Relaciones**
```powerbi
Modelo de Datos:
Overview[fund_id] → FundDetails[fund_id]
FundDetails[fund_id] → Positions[fund_id]
```

### **Step 2: Configurar Drill-Down**
1. **Visual de Overview**: Habilitar drill-down por `fund_id`
2. **Action**: Navegar a página "Fund Details"
3. **Filter**: Pasar `fund_id` como filtro
4. **Bookmark**: Guardar estado de filtros

### **Step 3: Botones de Navegación**
```powerbi
Botón "Back to Overview":
Acción: Navegar a página "Executive Overview"
Limpiar filtros: fund_id

Botón "View Positions":
Acción: Navegar a página "Position Analysis"
Mantener filtros: fund_id, date_filter
```

---

## 📱 **Filtros Interactivos**

### **Filtros Globales** (Todas las páginas)
- **📅 Date Range**: Slider temporal
- **⚠️ Risk Level**: Low, Medium, High
- **💰 Asset Size**: Large Cap, Mid Cap, Small Cap

### **Filtros Específicos**
- **Fund Details**: Currency, Time Period
- **Positions**: Asset Class, Min Weight, P&L Type

---

## 🔄 **Actualización de Datos**

### **Refresh Automático**
```powerbi
Configuración:
- Frecuencia: 30 minutos
- Horario: 8:00 AM - 6:00 PM
- Días: Lunes a Viernes
```

### **Parámetros Dinámicos**
```powerbi
@DateFilter = FORMAT(TODAY(), "yyyy-mm-dd")
@FundID = SELECTEDVALUE(Overview[fund_id])
```

---

## 🚀 **Optimizaciones de Performance**

### **Query Folding**
- Usar parámetros en URLs
- Filtrar en origen (API)
- Limitar registros con `min_weight`

### **Caché Inteligente**
- Overview: Actualizar cada hora
- Fund Details: Actualizar al drill-down
- Positions: Actualizar diario

---

## 📊 **Métricas Calculadas Sugeridas**

```dax
// Performance Score
Performance Score = 
IF([ytd_return] > 0.05, "High",
   IF([ytd_return] > 0.02, "Medium", "Low"))

// Risk-Adjusted Return
Risk Adjusted Return = [ytd_return] / [nav_volatility]

// Asset Concentration
Concentration Risk = 
CALCULATE(
    COUNT(Positions[position_id]),
    Positions[weight_percent] > 5
) / COUNT(Positions[position_id])
```

---

## 🎯 **Testing Checklist**

### ✅ **Funcionalidad**
- [ ] Overview carga correctamente
- [ ] Drill-down fund específico funciona
- [ ] Positions drill-down funciona
- [ ] Filtros interactivos responden
- [ ] KPIs se actualizan

### ✅ **Performance**
- [ ] Carga < 5 segundos
- [ ] Drill-down < 3 segundos
- [ ] Refresh completo < 30 segundos

### ✅ **UX/UI**
- [ ] Colores consistentes
- [ ] Responsive design
- [ ] Tooltips informativos
- [ ] Navegación intuitiva

---

## 🆘 **Troubleshooting**

### **Errores Comunes**

1. **"Data source not found"**
```
Solución: Verificar que FastAPI esté corriendo en localhost:8000
```

2. **"Timeout error"**
```
Solución: Aumentar timeout en PowerBI > Options > Data Load
```

3. **"Invalid JSON"**
```
Solución: Verificar formato de fecha YYYY-MM-DD
```

4. **"No data returned"**
```
Solución: Verificar fund_id existe y date_filter válido
```

---

## 🎉 **¡Dashboard Listo!**

Con esta configuración tendrás un **dashboard PowerBI profesional** con:
- ✅ **4 niveles de drill-down**
- ✅ **Navegación intuitiva**
- ✅ **KPIs en tiempo real**
- ✅ **Performance optimizado**
- ✅ **Visualizaciones interactivas**