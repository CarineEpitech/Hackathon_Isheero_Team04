# backend/routers/incidents.py
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/incidents", tags=["Signalements citoyens"])


class IncidentIn(BaseModel):
    type: str = Field(..., description="Type d'incident")
    description: str = Field(..., min_length=10, max_length=500)
    lat: float = Field(..., ge=6.0, le=12.5, description="Latitude (Bénin 6–12.5°N)")
    lon: float = Field(..., ge=0.7, le=3.9, description="Longitude (Bénin 0.7–3.9°E)")
    source: str = Field(default="citoyen")
    pseudo: Optional[str] = Field(default=None, max_length=50)
    contact: Optional[str] = Field(default=None, max_length=100)  # accepté, non stocké


@router.get("")
def list_incidents(validated_only: bool = False, hours: int = 48):
    from backend.services.reporting import load_recent
    df = load_recent(hours=hours)
    if validated_only:
        df = df[df["validated"] == 1]
    if df.empty:
        return {"count": 0, "incidents": []}
    # Normalize NaN / Timestamps for JSON serialization
    import math
    records = []
    for row in df.to_dict(orient="records"):
        clean = {}
        for k, v in row.items():
            if isinstance(v, float) and math.isnan(v):
                clean[k] = None
            elif hasattr(v, "isoformat"):
                clean[k] = v.isoformat()
            else:
                clean[k] = v
        records.append(clean)
    return {"count": len(records), "incidents": records}


@router.post("", status_code=201)
def create_incident(payload: IncidentIn):
    from backend.services.reporting import submit
    try:
        incident_id = submit(
            type_=payload.type,
            description=payload.description,
            lat=payload.lat,
            lon=payload.lon,
            source=payload.source,
            pseudo=payload.pseudo or "anonyme",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {
        "status": "created",
        "incident_id": incident_id,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Signalement reçu. En attente de validation.",
    }
