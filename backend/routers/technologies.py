from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/technologies", tags=["technologies"])

class TechnologyResponse(BaseModel):
    id: int
    name: str = ""
    description: Optional[str] = None

@router.get("/", response_model=List[TechnologyResponse])
def list_technologies():
    return []

@router.get("/{tech_id}", response_model=TechnologyResponse)
def get_technology(tech_id: int):
    raise HTTPException(status_code=404, detail="Not found")

@router.post("/", response_model=TechnologyResponse, status_code=201)
def create_technology(data: dict):
    return TechnologyResponse(id=1, name=data.get("name","Tech"))

@router.put("/{tech_id}", response_model=TechnologyResponse)
def update_technology(tech_id: int, data: dict):
    raise HTTPException(status_code=404, detail="Not found")

@router.delete("/{tech_id}", status_code=204)
def delete_technology(tech_id: int):
    pass
