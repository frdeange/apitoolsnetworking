# 🛠️ Kenmei Knowledge Base API

FastAPI service que proporciona datos de red, incidencias y soluciones para que el agente de Copilot Studio pueda consultar información contextual.

## 🚀 Cómo ejecutar

```bash
cd tools
uvicorn kenmei_knowledge_api:app --reload --port 8000
```

O simplemente:

```bash
python kenmei_knowledge_api.py
```

## 📡 Endpoints disponibles

### 1. **GET /network/sites**
Obtiene información de celdas/antenas por ubicación.

**Parámetros:**
- `location` (query): valencia, paterna, madrid, barcelona

**Ejemplo:**
```bash
curl "http://localhost:8000/network/sites?location=valencia"
```

**Respuesta:**
```json
[
  {
    "site_id": "VLC-001",
    "site_name": "Valencia Centro - Ayuntamiento",
    "location": "Plaza del Ayuntamiento, Valencia",
    "technologies": ["4G", "5G NSA", "5G SA"],
    "sectors": 3,
    "status": "active",
    "coverage_radius_km": 1.2,
    "coordinates": {"lat": 39.4699, "lon": -0.3763}
  }
]
```

---

### 2. **GET /network/incidents**
Obtiene incidencias activas en la red.

**Parámetros:**
- `location` (query, opcional): filtrar por área
- `severity` (query, opcional): critical, high, medium, low

**Ejemplo:**
```bash
curl "http://localhost:8000/network/incidents?location=valencia&severity=high"
```

**Respuesta:**
```json
[
  {
    "incident_id": "INC-2024-1142",
    "issue_type": "interference",
    "affected_area": "Valencia Centro - Plaza Ayuntamiento",
    "affected_sites": ["VLC-001", "VLC-002"],
    "severity": "high",
    "start_time": "2024-11-16T04:00:00",
    "estimated_resolution": "2024-11-17T10:00:00",
    "status": "in_progress",
    "description": "PCI conflict detectado entre site VLC-001 sector 2...",
    "affected_customers": 1250
  }
]
```

---

### 3. **GET /network/maintenance**
Obtiene mantenimientos programados.

**Parámetros:**
- `active_only` (query, default=true): solo mantenimientos activos ahora

**Ejemplo:**
```bash
curl "http://localhost:8000/network/maintenance?active_only=true"
```

---

### 4. **GET /solutions/products**
Obtiene catálogo de productos Kenmei.

**Parámetros:**
- `category` (query, opcional): AI Agents, AI Products, Data Fabric

**Ejemplo:**
```bash
curl "http://localhost:8000/solutions/products?category=AI%20Agents"
```

**Respuesta:**
```json
[
  {
    "product_name": "Kenmei AI Agents - Anomaly Detection",
    "category": "AI Agents",
    "description": "Detección automática de anomalías...",
    "use_cases": ["Detección temprana de degradación...", ...],
    "benefits": ["Reduce MTTR en 60%", ...],
    "url": "https://www.kenmei.ai/solutions/ai-products/anomalies"
  }
]
```

---

### 5. **GET /solutions/cases**
Obtiene casos similares resueltos.

**Parámetros:**
- `location_type` (query, opcional): urban, industrial, highway, underground

**Ejemplo:**
```bash
curl "http://localhost:8000/solutions/cases?location_type=urban"
```

**Respuesta:**
```json
[
  {
    "case_id": "CASE-5G-0782",
    "issue_description": "Pérdida de cobertura 5G en zona urbana...",
    "root_cause": "PCI conflict entre dos sites cercanos...",
    "solution_applied": "Ajuste de tilt mecánico de -2°...",
    "resolution_time_hours": 8.5,
    "success_rate": 0.98,
    "location_type": "urban"
  }
]
```

---

### 6. **POST /diagnostics/analyze** ⭐ (El más importante)
Análisis comprehensivo combinando toda la info.

**Body:**
```json
{
  "location": "valencia centro",
  "issue_type": "coverage",
  "symptoms": ["no_signal", "5g_fallback"],
  "network_technology": "5G"
}
```

**Respuesta:**
```json
{
  "context_found": true,
  "cell_sites_nearby": [...],
  "active_incidents": [...],
  "scheduled_maintenance": [...],
  "similar_cases": [...],
  "recommended_products": [...],
  "additional_context": "Hay 3 sites en el área: VLC-001, VLC-002, VLC-003\n⚠️ ALERTA: Hay 1 incidencias activas en la zona..."
}
```

---

## 🎯 Uso desde Copilot Studio

1. **Configura la API como Custom Connector** en Power Platform
2. **Importa el OpenAPI spec** desde http://localhost:8000/openapi.json
3. **Usa los endpoints** en tus Topics de Copilot Studio:

```
User: "No tengo cobertura 5G en Valencia centro"

Topic Flow:
1. Extract location: "valencia"
2. Call API: GET /network/incidents?location=valencia
3. Call API: POST /diagnostics/analyze
4. Show results to user
```

---

## 📊 Datos incluidos

### Ubicaciones soportadas:
- ✅ Valencia (3 sites)
- ✅ Paterna (2 sites)
- ✅ Madrid A3 (1 site)
- ✅ Barcelona Metro (1 site)

### Incidencias activas:
- PCI conflict en Valencia Centro (high severity)
- Degradación señal en Paterna Industrial (medium severity)

### Productos Kenmei:
- AI Agents - Anomaly Detection
- Geolocation - Virtual Drive Testing
- Telco Fabric
- Interference Detection

### Casos históricos:
- 4 casos resueltos con diferentes tipos de problemas

---

## 🔧 Extensión

Para añadir más datos, edita las constantes en `kenmei_knowledge_api.py`:

- `CELL_SITES_DB` - Añadir más ubicaciones y sites
- `ACTIVE_INCIDENTS_DB` - Añadir más incidencias
- `KENMEI_PRODUCTS_DB` - Añadir más productos
- `SIMILAR_CASES_DB` - Añadir más casos históricos

---

## 📖 Documentación interactiva

Accede a http://localhost:8000/docs para ver la documentación Swagger interactiva donde puedes probar todos los endpoints.

---

## 🎨 Próximos pasos

1. Ejecuta la API: `python kenmei_knowledge_api.py`
2. Prueba los endpoints desde tu navegador o Postman
3. Configura el Custom Connector en Power Platform
4. Crea tu agente en Copilot Studio con estos datos
5. ¡Integra con el workflow!
