"""
KENMEI KNOWLEDGE BASE API
=========================
FastAPI service providing network knowledge, incidents, and solutions data
for Copilot Studio agents to query.

Endpoints:
- GET /network/sites - Get cell sites info by location
- GET /network/incidents - Get active incidents in area
- GET /network/maintenance - Get scheduled maintenance
- GET /solutions/products - Get Kenmei product recommendations
- GET /solutions/cases - Get similar resolved cases
- POST /diagnostics/analyze - Analyze issue and get recommendations

Run with: uvicorn kenmei_knowledge_api:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum

app = FastAPI(
    title="Kenmei Knowledge Base API",
    description="Network intelligence API for Copilot Studio integration",
    version="1.0.0"
)

# Enable CORS for Copilot Studio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# DATA MODELS
# ============================================================================

class NetworkTechnology(str, Enum):
    LTE = "4G"
    NSA = "5G NSA"
    SA = "5G SA"
    VOLTE = "VoLTE"


class IssueType(str, Enum):
    COVERAGE = "coverage"
    SPEED = "speed"
    LATENCY = "latency"
    INTERFERENCE = "interference"
    HANDOVER = "handover"
    CALL_DROP = "call_drop"


class CellSite(BaseModel):
    site_id: str
    site_name: str
    location: str
    technologies: List[NetworkTechnology]
    sectors: int
    status: str  # active, maintenance, degraded
    coverage_radius_km: float
    coordinates: dict


class ActiveIncident(BaseModel):
    incident_id: str
    issue_type: IssueType
    affected_area: str
    affected_sites: List[str]
    severity: str  # critical, high, medium, low
    start_time: datetime
    estimated_resolution: Optional[datetime]
    status: str  # investigating, in_progress, resolved
    description: str
    affected_customers: int


class ScheduledMaintenance(BaseModel):
    maintenance_id: str
    sites: List[str]
    scheduled_start: datetime
    scheduled_end: datetime
    maintenance_type: str
    impact: str
    affected_services: List[str]
    notification_sent: bool


class KenmeiProduct(BaseModel):
    product_name: str
    category: str
    description: str
    use_cases: List[str]
    benefits: List[str]
    url: str


class SimilarCase(BaseModel):
    case_id: str
    issue_description: str
    root_cause: str
    solution_applied: str
    resolution_time_hours: float
    success_rate: float
    location_type: str


class DiagnosticRequest(BaseModel):
    location: str
    issue_type: str
    symptoms: List[str]
    network_technology: Optional[str] = None


class DiagnosticResponse(BaseModel):
    context_found: bool
    cell_sites_nearby: List[CellSite]
    active_incidents: List[ActiveIncident]
    scheduled_maintenance: List[ScheduledMaintenance]
    similar_cases: List[SimilarCase]
    recommended_products: List[KenmeiProduct]
    additional_context: str


# ============================================================================
# MOCK DATA (En producción vendría de base de datos real)
# ============================================================================

CELL_SITES_DB = {
    "valencia": [
        {
            "site_id": "VLC-001",
            "site_name": "Valencia Centro - Ayuntamiento",
            "location": "Plaza del Ayuntamiento, Valencia",
            "technologies": ["4G", "5G NSA", "5G SA"],
            "sectors": 3,
            "status": "active",
            "coverage_radius_km": 1.2,
            "coordinates": {"lat": 39.4699, "lon": -0.3763}
        },
        {
            "site_id": "VLC-002",
            "site_name": "Valencia Centro - Xàtiva",
            "location": "Calle Xàtiva, Valencia",
            "technologies": ["4G", "5G NSA"],
            "sectors": 3,
            "status": "degraded",
            "coverage_radius_km": 0.8,
            "coordinates": {"lat": 39.4665, "lon": -0.3769}
        },
        {
            "site_id": "VLC-003",
            "site_name": "Valencia Centro - Colón",
            "location": "Plaza de Colón, Valencia",
            "technologies": ["4G", "5G NSA", "5G SA"],
            "sectors": 3,
            "status": "active",
            "coverage_radius_km": 1.5,
            "coordinates": {"lat": 39.4731, "lon": -0.3719}
        }
    ],
    "paterna": [
        {
            "site_id": "PTR-001",
            "site_name": "Paterna Polígono Industrial",
            "location": "Polígono Industrial Vara de Quart, Paterna",
            "technologies": ["4G", "5G NSA"],
            "sectors": 3,
            "status": "active",
            "coverage_radius_km": 2.0,
            "coordinates": {"lat": 39.5167, "lon": -0.4500}
        },
        {
            "site_id": "PTR-002",
            "site_name": "Paterna Centro Tecnológico",
            "location": "Parc Tecnològic, Paterna",
            "technologies": ["4G", "5G NSA", "5G SA"],
            "sectors": 3,
            "status": "active",
            "coverage_radius_km": 1.8,
            "coordinates": {"lat": 39.5200, "lon": -0.4450}
        }
    ],
    "madrid": [
        {
            "site_id": "MAD-A3-280",
            "site_name": "A3 Autovía - KM 280",
            "location": "Autovía A3, KM 280",
            "technologies": ["4G", "VoLTE"],
            "sectors": 3,
            "status": "active",
            "coverage_radius_km": 3.5,
            "coordinates": {"lat": 39.7500, "lon": -1.2000}
        }
    ],
    "barcelona": [
        {
            "site_id": "BCN-M01",
            "site_name": "Barcelona Metro L1 - Arc Triomf",
            "location": "Metro L1, Estación Arc de Triomf",
            "technologies": ["4G", "VoLTE"],
            "sectors": 2,
            "status": "active",
            "coverage_radius_km": 0.3,
            "coordinates": {"lat": 41.3908, "lon": 2.1808}
        }
    ]
}

ACTIVE_INCIDENTS_DB = [
    {
        "incident_id": "INC-2024-1142",
        "issue_type": "interference",
        "affected_area": "Valencia Centro - Plaza Ayuntamiento",
        "affected_sites": ["VLC-001", "VLC-002"],
        "severity": "high",
        "start_time": datetime.now() - timedelta(hours=18),
        "estimated_resolution": datetime.now() + timedelta(hours=6),
        "status": "in_progress",
        "description": "PCI conflict detectado entre site VLC-001 sector 2 y VLC-002 sector 1 causando interferencia co-channel en banda 5G NSA. Kenmei AI ha identificado overshooting en VLC-002.",
        "affected_customers": 1250
    },
    {
        "incident_id": "INC-2024-1138",
        "issue_type": "coverage",
        "affected_area": "Paterna - Polígono Industrial Vara de Quart",
        "affected_sites": ["PTR-001"],
        "severity": "medium",
        "start_time": datetime.now() - timedelta(days=7),
        "estimated_resolution": datetime.now() + timedelta(hours=48),
        "status": "investigating",
        "description": "Degradación gradual de señal 5G detectada por Kenmei Geolocation. Análisis de drive test virtual muestra caída de RSRP en -10 dBm en última semana. Probable misconfiguration de tilt de antena.",
        "affected_customers": 450
    }
]

SCHEDULED_MAINTENANCE_DB = [
    {
        "maintenance_id": "MAINT-2024-0891",
        "sites": ["VLC-002"],
        "scheduled_start": datetime.now() - timedelta(hours=20),
        "scheduled_end": datetime.now() + timedelta(hours=4),
        "maintenance_type": "Software upgrade + antenna optimization",
        "impact": "Posibles cortes intermitentes de 5G NSA, fallback a 4G disponible",
        "affected_services": ["5G NSA"],
        "notification_sent": True
    }
]

KENMEI_PRODUCTS_DB = [
    {
        "product_name": "Kenmei AI Agents - Anomaly Detection",
        "category": "AI Agents",
        "description": "Detección automática de anomalías en redes móviles usando Machine Learning. Identifica patrones anormales en KPIs antes de que afecten a clientes.",
        "use_cases": [
            "Detección temprana de degradación de cobertura",
            "Identificación de interferencias (PCI conflicts, RSI)",
            "Predicción de fallos de handover",
            "Alertas automáticas de congestión de red"
        ],
        "benefits": [
            "Reduce MTTR (Mean Time To Repair) en 60%",
            "Detecta problemas 24-48h antes que métodos tradicionales",
            "Automatiza el 70% de diagnósticos de primer nivel"
        ],
        "url": "https://www.kenmei.ai/solutions/ai-products/anomalies"
    },
    {
        "product_name": "Kenmei Geolocation - Virtual Drive Testing",
        "category": "AI Products",
        "description": "Convierte datos de usuarios reales en análisis geo-localizado de calidad de red. Elimina la necesidad de drive tests físicos.",
        "use_cases": [
            "Validación de rollout 5G sin coste de drive testing",
            "Mapas de calor de cobertura en tiempo real",
            "Análisis de rutas (carreteras, ferrocarril, metro)",
            "Optimización de cobertura indoor"
        ],
        "benefits": [
            "Reduce costes de drive testing en 80%",
            "Cobertura 100x mayor que drive test manual",
            "Datos actualizados continuamente vs snapshots"
        ],
        "url": "https://www.kenmei.ai/solutions/ai-products/geolocation"
    },
    {
        "product_name": "Kenmei Telco Fabric",
        "category": "Data Fabric",
        "description": "Unifica datos de radio, core y operaciones en una capa única query-ready. Elimina silos de datos entre vendors.",
        "use_cases": [
            "Correlación de eventos entre RAN y Core",
            "Queries cross-vendor en segundos",
            "Dashboards unificados de KPIs multi-tecnología",
            "Data lake telco con semantic layer"
        ],
        "benefits": [
            "Reduce tiempo de troubleshooting de horas a minutos",
            "Elimina 80% de trabajo manual de correlación de logs",
            "Habilita uso de AI sobre datos unificados"
        ],
        "url": "https://www.kenmei.ai/solutions/telco-fabric"
    },
    {
        "product_name": "Kenmei Interference Detection",
        "category": "AI Products",
        "description": "Detecta y diagnostica automáticamente interferencias en redes móviles (PCI conflicts, inter-cell, external).",
        "use_cases": [
            "Detección de PCI conflicts en rollout 5G",
            "Identificación de interferencias externas (radar, military)",
            "Análisis de inter-cell interference",
            "Optimización automática de neighbor lists"
        ],
        "benefits": [
            "Identifica >95% de interferencias automáticamente",
            "Recomienda acciones correctivas específicas",
            "Integra con Telco Fabric para análisis multi-capa"
        ],
        "url": "https://www.kenmei.ai/solutions/ai-products/interference"
    }
]

SIMILAR_CASES_DB = [
    {
        "case_id": "CASE-5G-0782",
        "issue_description": "Pérdida de cobertura 5G en zona urbana con fallback a 4G",
        "root_cause": "PCI conflict entre dos sites cercanos debido a expansion de red. Overshooting de antena recién instalada",
        "solution_applied": "Ajuste de tilt mecánico de -2° en site VLC-002 sector 1 + reconfiguración de PCI de 156 a 289. Optimización MLB para balanceo de carga.",
        "resolution_time_hours": 8.5,
        "success_rate": 0.98,
        "location_type": "urban"
    },
    {
        "case_id": "CASE-5G-0654",
        "issue_description": "Fluctuación constante de señal 5G en polígono industrial",
        "root_cause": "Interferencia externa de radar meteorológico en banda n78 (3.5 GHz). Kenmei Interference Detection identificó patrón periódico cada 12 segundos.",
        "solution_applied": "Reconfiguración de carrier aggregation para evitar frecuencias afectadas. Activación de filtrado adaptativo. Escalado a autoridad de telecomunicaciones para coordinación de frecuencias.",
        "resolution_time_hours": 72.0,
        "success_rate": 0.92,
        "location_type": "industrial"
    },
    {
        "case_id": "CASE-4G-1023",
        "issue_description": "Baja velocidad de datos en autovía, calls OK pero datos lentos",
        "root_cause": "Congestión de backhaul en site A3-KM280. Saturación de enlace microwave en horas pico (95% utilización). Kenmei AI detectó patrón de degradación gradual.",
        "solution_applied": "Upgrade de backhaul de 1 Gbps a 10 Gbps fiber. Implementación de QoS en S1 interface. Activación de carrier aggregation para offload a banda adicional.",
        "resolution_time_hours": 120.0,
        "success_rate": 1.0,
        "location_type": "highway"
    },
    {
        "case_id": "CASE-VLT-0445",
        "issue_description": "Llamadas caídas en metro/túneles",
        "root_cause": "Handover failure entre outdoor macro cell y indoor DAS system. Misconfiguration en A3 event offset. Kenmei detectó RLF rate >15%.",
        "solution_applied": "Optimización de neighbor list, ajuste de A3 offset de 3dB a 1dB, configuración de TTT (Time To Trigger) de 320ms a 160ms. Activación de CS Fallback optimization.",
        "resolution_time_hours": 12.0,
        "success_rate": 0.95,
        "location_type": "underground"
    }
]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
def read_root():
    """API root - health check."""
    return {
        "service": "Kenmei Knowledge Base API",
        "status": "online",
        "version": "1.0.0",
        "endpoints": [
            "/network/sites",
            "/network/incidents",
            "/network/maintenance",
            "/solutions/products",
            "/solutions/cases",
            "/diagnostics/analyze"
        ]
    }


@app.get("/network/sites", response_model=List[CellSite])
def get_cell_sites(
    location: str = Query(..., description="Location to search (valencia, paterna, madrid, barcelona)")
):
    """
    Get cell site information for a specific location.
    
    Returns details about cell towers, technologies, coverage, and status.
    """
    location_key = location.lower()
    if location_key not in CELL_SITES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"No cell sites found for location: {location}. Available: {list(CELL_SITES_DB.keys())}"
        )
    
    return CELL_SITES_DB[location_key]


@app.get("/network/incidents", response_model=List[ActiveIncident])
def get_active_incidents(
    location: Optional[str] = Query(None, description="Filter by location/area"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, medium, low)")
):
    """
    Get active network incidents.
    
    Returns ongoing issues detected by Kenmei AI systems.
    """
    incidents = ACTIVE_INCIDENTS_DB.copy()
    
    if location:
        incidents = [inc for inc in incidents if location.lower() in inc["affected_area"].lower()]
    
    if severity:
        incidents = [inc for inc in incidents if inc["severity"] == severity.lower()]
    
    return incidents


@app.get("/network/maintenance", response_model=List[ScheduledMaintenance])
def get_scheduled_maintenance(
    active_only: bool = Query(True, description="Only show currently active maintenance")
):
    """
    Get scheduled maintenance windows.
    
    Returns planned maintenance activities that may affect service.
    """
    maintenance = SCHEDULED_MAINTENANCE_DB.copy()
    
    if active_only:
        now = datetime.now()
        maintenance = [
            m for m in maintenance
            if m["scheduled_start"] <= now <= m["scheduled_end"]
        ]
    
    return maintenance


@app.get("/solutions/products", response_model=List[KenmeiProduct])
def get_kenmei_products(
    category: Optional[str] = Query(None, description="Filter by category (AI Agents, AI Products, Data Fabric)")
):
    """
    Get Kenmei product catalog.
    
    Returns available Kenmei solutions that can address specific network issues.
    """
    products = KENMEI_PRODUCTS_DB.copy()
    
    if category:
        products = [p for p in products if category.lower() in p["category"].lower()]
    
    return products


@app.get("/solutions/cases", response_model=List[SimilarCase])
def get_similar_cases(
    location_type: Optional[str] = Query(None, description="Filter by location type (urban, industrial, highway, underground)")
):
    """
    Get similar resolved cases from knowledge base.
    
    Returns historical cases with proven solutions.
    """
    cases = SIMILAR_CASES_DB.copy()
    
    if location_type:
        cases = [c for c in cases if c["location_type"] == location_type.lower()]
    
    # Sort by success rate descending
    cases.sort(key=lambda x: x["success_rate"], reverse=True)
    
    return cases


@app.post("/diagnostics/analyze", response_model=DiagnosticResponse)
def analyze_diagnostic(request: DiagnosticRequest):
    """
    Comprehensive diagnostic analysis.
    
    Combines cell sites, incidents, maintenance, and historical cases
    to provide rich context for issue diagnosis.
    """
    location_key = request.location.lower()
    
    # Get cell sites
    cell_sites = []
    for key in CELL_SITES_DB:
        if key in location_key or location_key in key:
            cell_sites.extend(CELL_SITES_DB[key])
    
    # Get active incidents
    active_incidents = [
        inc for inc in ACTIVE_INCIDENTS_DB
        if location_key in inc["affected_area"].lower()
    ]
    
    # Get scheduled maintenance
    now = datetime.now()
    scheduled_maintenance = [
        m for m in SCHEDULED_MAINTENANCE_DB
        if m["scheduled_start"] <= now <= m["scheduled_end"]
    ]
    
    # Get similar cases
    # Determine location type from location string
    location_type = "urban"  # default
    if "poligono" in location_key or "industrial" in location_key:
        location_type = "industrial"
    elif "autovia" in location_key or "carretera" in location_key:
        location_type = "highway"
    elif "metro" in location_key or "tunel" in location_key:
        location_type = "underground"
    
    similar_cases = [c for c in SIMILAR_CASES_DB if c["location_type"] == location_type]
    similar_cases.sort(key=lambda x: x["success_rate"], reverse=True)
    
    # Recommend products based on issue type
    recommended_products = []
    issue_lower = request.issue_type.lower()
    
    if "interference" in issue_lower or "signal" in " ".join(request.symptoms).lower():
        recommended_products.append(KENMEI_PRODUCTS_DB[3])  # Interference Detection
    if "coverage" in issue_lower or "cobertura" in issue_lower:
        recommended_products.append(KENMEI_PRODUCTS_DB[1])  # Geolocation
    
    # Always recommend AI Agents for automatic detection
    recommended_products.append(KENMEI_PRODUCTS_DB[0])  # AI Agents
    
    # Build additional context
    context_parts = []
    
    if cell_sites:
        context_parts.append(f"Hay {len(cell_sites)} sites en el área: {', '.join([s['site_id'] for s in cell_sites])}")
    
    if active_incidents:
        context_parts.append(f"⚠️ ALERTA: Hay {len(active_incidents)} incidencias activas en la zona")
        for inc in active_incidents:
            context_parts.append(f"  - {inc['incident_id']}: {inc['description'][:150]}...")
    
    if scheduled_maintenance:
        context_parts.append(f"🔧 Hay mantenimiento programado activo que puede estar afectando")
    
    if similar_cases:
        context_parts.append(f"📚 Se encontraron {len(similar_cases)} casos similares resueltos con éxito")
    
    additional_context = "\n".join(context_parts) if context_parts else "No hay contexto adicional disponible"
    
    return DiagnosticResponse(
        context_found=len(cell_sites) > 0 or len(active_incidents) > 0,
        cell_sites_nearby=cell_sites,
        active_incidents=active_incidents,
        scheduled_maintenance=scheduled_maintenance,
        similar_cases=similar_cases[:3],  # Top 3 most relevant
        recommended_products=recommended_products,
        additional_context=additional_context
    )


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "KENMEI KNOWLEDGE BASE API" + " " * 33 + "║")
    print("║" + " " * 15 + "Intelligence Behind Mobile Networks - API" + " " * 22 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    print("🚀 API started successfully!")
    print("📡 Serving network intelligence data for Copilot Studio")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/")
    print("\n")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
