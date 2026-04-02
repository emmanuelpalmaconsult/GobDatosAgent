# 🔌 POWER BI CONNECTION OPTIONS
# Investment Data Analysis Agent - Todas las opciones de conexión

## 📋 ESCENARIOS Y SOLUCIONES

### ✅ ESCENARIO 1: Servidor online con SQL Server conectado
**Usar:** Endpoints originales con datos reales  
**Query:** PowerBI_Queries.txt (original)  
**URL Base:** http://localhost:8000

### 🔧 ESCENARIO 2: Servidor online SIN SQL Server  
**Usar:** Datos demo del servidor FastAPI  
**Query:** Ver queries demo abajo  
**URL Base:** http://localhost:8000

### 📱 ESCENARIO 3: Desarrollo offline
**Usar:** Datos estáticos demo  
**Query:** PowerBI_Demo_Data.txt  
**URL Base:** Ninguna (datos locales)

---

## 🔌 OPCIÓN 1: ENDPOINTS ORIGINALES (Datos Reales)

### Power Query para conexión principal:
```powerquery
let
    // Configuración base
    BaseURL = "http://localhost:8000",
    
    // Función para manejar errores HTTP
    GetJsonSafe = (url as text) =>
        let
            Source = try Json.Document(Web.Contents(url)) otherwise null
        in
            Source,
    
    // 1. FONDOS PRINCIPALES
    FundsUrl = BaseURL & "/api/v1/powerbi/funds",
    FundsRaw = GetJsonSafe(FundsUrl),
    FundsTable = if FundsRaw <> null then
        Table.FromRecords(FundsRaw)
    else
        #table({"FundName", "TotalAssets", "YTDReturn", "Status"}, 
               {{"Servidor Offline", 0, 0, "Offline"}}),
    
    // Convertir tipos de datos
    FundsTyped = Table.TransformColumnTypes(FundsTable, {
        {"FundID", type text},
        {"FundName", type text},
        {"TotalAssets", type number},
        {"YTDReturn", type number},
        {"RiskLevel", type text},
        {"AssetClass", type text},
        {"LaunchDate", type date},
        {"Status", type text}
    })

in
    FundsTyped
```

### Query para detalles completos:
```powerquery
let
    BaseURL = "http://localhost:8000",
    DetailsUrl = BaseURL & "/api/v1/powerbi/fund-details-all",
    Source = try Json.Document(Web.Contents(DetailsUrl)) otherwise [],
    
    // Expandir datos anidados
    Table = if List.Count(Source) > 0 then
        let
            RecordsTable = Table.FromRecords(Source),
            
            // Expandir posiciones si existen
            ExpandPositions = if Table.HasColumns(RecordsTable, "positions") then
                Table.ExpandListColumn(RecordsTable, "positions")
            else RecordsTable,
            
            // Expandir cash flows si existen  
            ExpandCashFlows = if Table.HasColumns(ExpandPositions, "cash_flows") then
                Table.ExpandListColumn(ExpandPositions, "cash_flows")
            else ExpandPositions
            
        in ExpandCashFlows
    else
        #table({"Message"}, {{"No data available"}})
        
in
    Table
```

---

## 🔌 OPCIÓN 2: DEMO ENDPOINTS (FastAPI sin SQL Server)

### Query para datos demo cuando SQL Server no está disponible:
```powerquery
let
    BaseURL = "http://localhost:8000",
    
    // Función demo que genera datos sintéticos
    CreateDemoData = () =>
        let
            DemoRecords = {
                [FundID = "DEMO001", FundName = "Growth Fund Alpha", 
                 TotalAssets = 2500000000, YTDReturn = 0.125, 
                 RiskLevel = "High", AssetClass = "Equity", 
                 LaunchDate = #date(2020, 1, 15), Status = "Active"],
                 
                [FundID = "DEMO002", FundName = "Balanced Portfolio", 
                 TotalAssets = 1800000000, YTDReturn = 0.083,
                 RiskLevel = "Medium", AssetClass = "Mixed", 
                 LaunchDate = #date(2019, 6, 30), Status = "Active"],
                 
                [FundID = "DEMO003", FundName = "Conservative Income", 
                 TotalAssets = 950000000, YTDReturn = 0.045,
                 RiskLevel = "Low", AssetClass = "Fixed Income", 
                 LaunchDate = #date(2021, 3, 10), Status = "Active"]
            }
        in
            Table.FromRecords(DemoRecords),
    
    // Intentar endpoint real primero, luego demo
    Source = try Json.Document(Web.Contents(BaseURL & "/api/v1/powerbi/funds"))
             otherwise null,
    
    FinalTable = if Source <> null then 
        Table.FromRecords(Source)
    else 
        CreateDemoData()

in
    FinalTable
```

---

## 🔌 OPCIÓN 3: DATOS OFFLINE (Para desarrollo)

### Usar tabla estática:
```powerquery
let
    Source = #table(
        type table [
            FundID = text,
            FundName = text, 
            TotalAssets = number,
            YTDReturn = number,
            RiskLevel = text,
            AssetClass = text,
            LaunchDate = date,
            Status = text
        ],
        {
            {"FUN001", "Aggressive Growth Fund", 2500000000, 0.1450, "High", "Equity", #date(2020,1,15), "Active"},
            {"FUN002", "Balanced Allocation", 1800000000, 0.0890, "Medium", "Mixed", #date(2019,6,30), "Active"},
            {"FUN003", "Income Plus", 1200000000, 0.0650, "Medium", "Fixed Income", #date(2021,3,10), "Active"},
            {"FUN004", "Conservative Bond", 950000000, 0.0420, "Low", "Fixed Income", #date(2020,9,22), "Active"},
            {"FUN005", "Real Estate Equity", 750000000, 0.0780, "Medium", "Real Estate", #date(2019,11,5), "Active"},
            {"FUN006", "Tech Innovation", 1100000000, 0.1680, "High", "Equity", #date(2021,7,12), "Active"},
            {"FUN007", "Global Diversified", 2100000000, 0.0920, "Medium", "Mixed", #date(2018,4,8), "Active"},
            {"FUN008", "Commodity Focus", 480000000, -0.0150, "High", "Commodity", #date(2022,1,20), "Active"}
        }
    )
in
    Source
```

---

## ⚙️ CONFIGURACIÓN AUTOMÁTICA

### Query que detecta automáticamente qué usar:
```powerquery
let
    BaseURL = "http://localhost:8000",
    
    // Test de conectividad
    TestConnection = () =>
        let
            TestResult = try Web.Contents(BaseURL & "/health", [Timeout = #duration(0,0,0,3)])
                        otherwise null
        in
            TestResult <> null,
    
    IsOnline = TestConnection(),
    
    // Datos según disponibilidad
    Data = if IsOnline then
        // Servidor online - usar endpoints reales
        let
            FundsData = try Json.Document(Web.Contents(BaseURL & "/api/v1/powerbi/funds"))
                       otherwise null
        in
            if FundsData <> null then
                Table.FromRecords(FundsData)
            else
                // Servidor online pero sin datos SQL - usar demo
                Table.FromRecords({
                    [FundID = "DEMO", FundName = "Demo Fund", 
                     TotalAssets = 1000000000, YTDReturn = 0.08,
                     Status = "Demo Mode"]
                })
    else
        // Offline - usar datos estáticos
        #table(
            {"FundID", "FundName", "TotalAssets", "YTDReturn", "Status"},
            {{"OFFLINE", "Offline Data", 1000000000, 0.05, "Offline"}}
        )

in
    Data
```

---

## 🎯 RECOMENDACIONES DE USO

### Para Desarrollo:
1. **Primer intento:** OPCIÓN 1 (endpoints originales)
2. **Si falla SQL Server:** OPCIÓN 2 (demo endpoints)  
3. **Si servidor offline:** OPCIÓN 3 (datos estáticos)

### Para Producción:
- **Solo OPCIÓN 1** con endpoints reales
- Implementar manejo robusto de errores
- Configurar refresh automático

### Para Demos/Training:
- **OPCIÓN 3** (datos estáticos)
- Datos consistentes y predecibles
- No depende de infraestructura

---

## 🔧 TROUBLESHOOTING

### Error "Data source not found":
```powerquery
// Agregar al inicio de cada query
let
    Source = try YourOriginalQuery otherwise #table({"Error"}, {{"Connection failed"}})
in
    Source
```

### Error de timeout:
```powerquery
Web.Contents(url, [Timeout = #duration(0,0,0,30)]) // 30 segundos
```

### Error de formato JSON:
```powerquery
let
    RawData = Web.Contents(url),
    JsonData = try Json.Document(RawData) otherwise []
in
    if List.Count(JsonData) > 0 then JsonData else []
```

¡Con estas opciones tendrás PowerBI funcionando en cualquier escenario! 🚀