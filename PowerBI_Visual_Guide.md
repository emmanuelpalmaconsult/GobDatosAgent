# 📊 POWER BI DASHBOARD DESIGN GUIDE
# Investment Data Analysis Agent - Visual Components

## 🎨 DASHBOARD LAYOUT (Lienzo 1920x1080)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🏦 INVESTMENT PORTFOLIO DASHBOARD                                  📅 May 2024  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  📈 [Total AUM]      💰 [Avg Return]      📊 [Active Funds]    🎯 [Top Perf.]  │
│     $X.X Billion        X.XX%               XX                   XX.X%          │
│                                                                                 │
├─────────────────────────────────┬───────────────────────────────────────────────┤
│                                 │                                               │
│   🏢 FUND OVERVIEW TABLE        │   📊 ASSET ALLOCATION PIE CHART              │
│   (Scrollable)                  │                                               │
│   ┌─────────────────────────┐    │         Equity 45%                           │
│   │Fund Name │AUM │Return│  │    │      Fixed Income 35%                        │
│   │Fund A    │$2B │12.5%│   │    │     Real Estate 15%                          │
│   │Fund B    │$1B │8.3% │   │    │      Commodity 5%                            │
│   └─────────────────────────┘    │                                               │
│                                 │                                               │
├─────────────────────────────────┼───────────────────────────────────────────────┤
│                                 │                                               │
│   📈 PERFORMANCE HISTOGRAM      │   🎯 RISK DISTRIBUTION BAR CHART             │
│     Y: Fund Count               │                                               │
│     X: Return Ranges            │      High │████████│ 8 funds                 │
│                                 │    Medium │██████████│ 12 funds             │
│     ████                        │       Low │████│ 5 funds                     │
│   ██████████                    │                                               │
│ 0-5% 5-10% 10-15% 15%+         │                                               │
│                                 │                                               │
└─────────────────────────────────┴───────────────────────────────────────────────┘
```

## 📋 PASO A PASO - CREACIÓN DE VISUALIZACIONES

### 1️⃣ KPI CARDS (Tarjetas)

**Tarjeta: Total AUM**
1. Panel Visualizaciones → Tarjeta
2. Campos → Arrastrar medida `[Total AUM]`
3. Formato → Etiqueta de datos → Unidades de pantalla: Billions
4. Color: Azul (#2E86C1)
5. Tamaño fuente: 32px

**Tarjeta: Average Return**
1. Panel Visualizaciones → Tarjeta  
2. Campos → Arrastrar medida `[Average Return]`
3. Formato → Etiqueta de datos → Formato: Percentage
4. Color: Verde si >5%, Rojo si <0%
5. Incluir título: "Average Portfolio Return"

### 2️⃣ TABLA PRINCIPAL (Fund Overview)

**Configuración:**
1. Panel Visualizaciones → Tabla
2. Valores → Arrastrar:
   - FundName
   - TotalAssets (formatear como currency)
   - YTDReturn (formatear como percentage)
   - RiskLevel
   - AssetClass

**Formato:**
- Filas: Alternar colores (blanco/#F8F9FA)
- Headers: Background #34495E, texto blanco
- Ordenar por: TotalAssets descendente
- Habilitar scroll

### 3️⃣ PIE CHART (Asset Allocation)

**Configuración:**
1. Panel Visualizaciones → Gráfico circular
2. Leyenda → AssetClass  
3. Valores → [Total AUM]

**Formato:**
- Colores personalizados:
  - Equity: #E74C3C (rojo)
  - Fixed Income: #3498DB (azul)
  - Real Estate: #F39C12 (naranja)
  - Commodity: #27AE60 (verde)
- Mostrar porcentajes
- Leyenda: Posición derecha

### 4️⃣ HISTOGRAM (Performance Distribution)

**Configuración:**
1. Panel Visualizaciones → Gráfico de columnas agrupadas
2. Eje X → Crear grupos de YTDReturn:
   - 0-5%, 5-10%, 10-15%, 15%+
3. Eje Y → COUNT de FundID
4. Título: "Performance Distribution"

**Formato:**
- Barras: Color gradiente verde a rojo
- Eje Y: Título "Number of Funds"
- Eje X: Rotar etiquetas 45°

### 5️⃣ BAR CHART (Risk Distribution)

**Configuración:**
1. Panel Visualizaciones → Gráfico de barras horizontales
2. Eje Y → RiskLevel
3. Eje X → COUNT de FundID

**Formato:**
- Colores por riesgo:
  - High: #E74C3C
  - Medium: #F39C12  
  - Low: #27AE60
- Mostrar valores en barras

## 🎨 TEMAS Y COLORES

### Color Palette Profesional
```css
Primary Blue:    #2E86C1
Secondary Blue:  #5DADE2
Success Green:   #27AE60
Warning Orange:  #F39C12
Danger Red:      #E74C3C
Dark Gray:       #34495E
Light Gray:      #ECF0F1
```

### Fuentes Recomendadas
- Títulos: **Segoe UI Bold, 16px**
- Subtítulos: **Segoe UI Semibold, 14px**
- Texto: **Segoe UI Regular, 12px**
- KPIs: **Segoe UI Bold, 24px**

## 📱 RESPONSIVE DESIGN

### Desktop (1920x1080)
- 4 KPIs horizontales arriba
- 2x2 grid visualizaciones principales  

### Tablet (1024x768)
- 2x2 KPIs grid
- Stack visualizaciones verticalmente

### Mobile (800x600)
- Stack todo verticalmente
- Reducir tamaños de fuente

## 🎯 INTERACTIVIDAD

### Cross-filtering habilitado entre:
- Tabla ↔ Pie Chart
- Risk Chart ↔ Performance Histogram
- Asset Allocation ↔ Fund Table

### Tooltips personalizados:
- Fund Table: Mostrar gestores y fechas
- Charts: Incluir medias de sector

## 🚀 PASOS SIGUIENTES

1. **Conectar datos** usando PowerBI_Queries.txt
2. **Crear medidas DAX** desde PowerBI_DAX_Measures.txt  
3. **Construir visualizaciones** siguiendo esta guía
4. **Aplicar formato** con color palette
5. **Probar interactividad** y filtros
6. **Publicar** al Power BI Service

¡Tu dashboard estará listo para impresionar a ejecutivos! 📊💼