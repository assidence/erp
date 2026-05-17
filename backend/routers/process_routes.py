from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/process-routes", tags=["process-routes"])

class ProcessRouteResponse(BaseModel):
    id: int
    name: str = ""
    description: Optional[str] = None

@router.get("/", response_model=List[ProcessRouteResponse])
def list_routes():
    return []

@router.get("/{route_id}", response_model=ProcessRouteResponse)
def get_route(route_id: int):
    raise HTTPException(status_code=404, detail="Not found")

@router.post("/", response_model=ProcessRouteResponse, status_code=201)
def create_route(data: dict):
    return ProcessRouteResponse(id=1, name=data.get("name","Route"))

@router.put("/{route_id}", response_model=ProcessRouteResponse)
def update_route(route_id: int, data: dict):
    raise HTTPException(status_code=404, detail="Not found")

@router.delete("/{route_id}", status_code=204)
def delete_route(route_id: int):
    pass
