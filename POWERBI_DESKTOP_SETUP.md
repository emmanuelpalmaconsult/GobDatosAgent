# 📊 PowerBI Desktop Configuration Guide
## Investment Data Analysis Agent - Configuración Paso a Paso

### 🎯 **CONFIGURACIÓN STEP-BY-STEP**

---

## **PASO 1: CONECTAR PRIMERA FUENTE DE DATOS**

### 1.1 En PowerBI Desktop:
```
1. Inicio → "Obtener datos"
2. Seleccionar "Web" 
3. Hacer clic "Conectar"
```

### 1.2 Configurar URL:
```
URL: http://localhost:8000/api/v1/powerbi/funds
```

### 1.3 Autenticación:
```
- Seleccionar "Anónima" 
- Hacer clic "Conectar"
```

### ✅ **Resultado esperado:** 
PowerBI mostrará los datos de fondos en formato JSON/tabla

---

## **PASO 2: TRANSFORMAR DATOS PRINCIPALES**

### 2.1 En el Preview:
```
1. Hacer clic "Transformar datos" (NO "Cargar")
2. Se abrirá el Editor de Power Query
```

### 2.2 Renombrar Query:
```
- Clic derecho en "Table" → "Cambiar nombre"  
- Nuevo nombre: "Funds Overview"
```

### 2.3 Reemplazar Query con código optimizado:
```
1. En Editor Power Query → Ver → Editor avanzado
2. BORRAR todo el código existente
3. COPIAR y PEGAR el código de QUERY 1 desde PowerBI_Queries.txt
```

**Código a usar (QUERY 1):**
```powerquery
let
    // Conectar a API original
    Source = Json.Document(Web.Contents("http://localhost:8000/api/v1/powerbi/funds")),
    
    // Extraer array de datos (estructura del endpoint real)
    data = Source,
    
    // Si viene en formato array, usar eso; sino, crear tabla directo
    #"Data Source" = if Value.Is(data, type list) then
                        Table.FromList(data, Splitter.SplitByNothing(), null, null, ExtraValues.Error)
                     else  
                        Table.FromRecords({data}),
    
    // Expandir todas las columnas del endpoint real
    #"Expanded Column1" = Table.ExpandRecordColumn(#"Data Source", 
        if Value.Is(data, type list) then "Column1" else "column",
        {"PshipID", "FundName", "Status", "TotalAssets", "YTDReturn", 
         "RiskLevel", "AssetClass", "Currency", "LastUpdated"}),
    
    // Convertir tipos de datos
    #"Changed Type" = Table.TransformColumnTypes(#"Expanded Column1",{
        {"PshipID", Int64.Type},
        {"FundName", type text},
        {"Status", type text},
        {"TotalAssets", Currency.Type},
        {"YTDReturn", Percentage.Type},
        {"RiskLevel", type text},
        {"AssetClass", type text},
        {"Currency", type text}
    }),
    
    // Agregar columnas calculadas
    #"Added AUM Billions" = Table.AddColumn(#"Changed Type", "AUM_Billions", 
        each [TotalAssets] / 1000000000, Currency.Type),
    
    #"Added Risk Category" = Table.AddColumn(#"Added AUM Billions", "RiskCategory", 
        each if [RiskLevel] = "Low" then "Low Risk" 
             else if [RiskLevel] = "Medium" then "Medium Risk" 
             else "High Risk"),
             
    #"Added Return Category" = Table.AddColumn(#"Added Risk Category", "ReturnCategory",
        each if [YTDReturn] < 0 then "Negative"
             else if [YTDReturn] < 0.05 then "Below 5%"
             else if [YTDReturn] < 0.15 then "5%-15%"
             else "Above 15%")
in
    #"Added Return Category"
```

---

## **PASO 3: AGREGAR KPIs DASHBOARD**

### 3.1 Crear nueva Query:
```
1. En Power Query Editor → Nueva consulta → Consulta en blanco
2. Renombrar a "KPIs Dashboard"
```

### 3.2 Código para KPIs:
```powerquery
let
    Source = Json.Document(Web.Contents("http://localhost:8000/api/v1/kpis/dashboard")),
    
    // Extraer métricas del endpoint real
    kpis = Source,
    
    // Crear tabla con estructura adaptada a respuesta real
    KPITable = if Record.HasFields(kpis, "total_aum") then
        #table(
            {"KPI_Name", "Value", "Format_Type"},
            {
                {"Total AUM", kpis[total_aum], "Currency"},
                {"Average Return", kpis[avg_return], "Percentage"}, 
                {"Active Funds", kpis[active_funds], "Number"},
                {"Top Fund", kpis[top_fund_return], "Percentage"}
            }
        )
    else
        // Fallback si la estructura es diferente
        Record.ToTable(kpis),
    
    #"Changed Type" = Table.TransformColumnTypes(KPITable,{
        {"Value", type number}
    })
in
    #"Changed Type"
```

---

## **PASO 4: CERRAR Y APLICAR**

### 4.1 Finalizar configuración:
```
1. Archivo → Cerrar y aplicar
2. PowerBI cargará las tablas al modelo de datos
```

### ✅ **Resultado esperado:**
```
- Tabla "Funds Overview" con todos los fondos
- Tabla "KPIs Dashboard" con métricas principales
- Datos listos para visualización
```

---

## **PASO 5: CREAR VISUALIZACIONES BÁSICAS**

### 5.1 KPI Cards (Tarjetas):
```
1. Visualizaciones → Tarjeta
2. Arrastrar "Value" desde "KPIs Dashboard"
3. Filtrar por "KPI_Name" = "Total AUM"
4. Repetir para otros KPIs
```

### 5.2 Tabla de Fondos:
```
1. Visualizaciones → Tabla
2. Arrastrar campos desde "Funds Overview":
   - FundName
   - TotalAssets  
   - YTDReturn
   - Status
   - RiskLevel
```

### 5.3 Gráfico de Distribución:
```
1. Visualizaciones → Gráfico circular
2. Leyenda: AssetClass
3. Valores: TotalAssets (Sum)
```

---

## **PASO 6: CONFIGURAR DRILL-DOWN (OPCIONAL)**

### 6.1 Crear parámetro para Drill-Down:
```
1. Transformar datos → Administrar parámetros → Nuevo parámetro
2. Nombre: "SelectedFundID"
3. Tipo: Número entero
4. Valor actual: 1
```

### 6.2 Query para Posiciones:
```
1. Nueva consulta → Consulta en blanco
2. Nombre: "Fund Positions"
3. Usar código QUERY 4 de PowerBI_Queries.txt
```

---

## **🔧 SOLUCIÓN DE PROBLEMAS**

### ❌ Error de conexión:
```
1. Verificar servidor: http://localhost:8000/docs
2. Comprobar firewall/antivirus
3. Reiniciar PowerBI Desktop
```

### ❌ Error de formato de datos:
```
1. Ir a Transformar datos
2. Ver tipo de datos en columnas 
3. Ajustar tipos según estructura real
```

### ❌ Query no funciona:
```
1. Verificar endpoint en navegador primero
2. Copiar estructura JSON real
3. Adaptar código de query según respuesta
```

---

## **📊 RESULTADOS ESPERADOS**

### Dashboard básico debe mostrar:
```
✅ KPI Cards: AUM Total, Promedio Return, Fondos Activos
✅ Tabla: Lista de todos los fondos con métricas
✅ Pie Chart: Distribución por tipo de activo  
✅ Bar Chart: Top fondos por performance
```

### Datos de ejemplo esperados:
```
- Fondos activos del sistema real
- Assets en CLP (millones/billones)
- Returns en porcentaje
- Clasificación de riesgo
- Status Active/Inactive
```

---

## **🎯 PRÓXIMOS PASOS**

1. **Styling**: Aplicar tema corporativo
2. **Interactividad**: Configurar drill-down entre páginas  
3. **Filtros**: Agregar slicers por fecha, tipo, riesgo
4. **Métricas avanzadas**: Sharpe ratio, volatilidad, benchmark
5. **Automatización**: Scheduled refresh cuando esté en producción

---

**🚀 ¡Dashboard Investment Data Analysis Agent listo para uso ejecutivo!** 📈