from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/casting-drawings", tags=["casting-drawings"])

class CastingDrawingResponse(BaseModel):
    id: int
    casting_id: int
    drawing_number: str = ""
    description: Optional[str] = None

@router.get("/", response_model=List[CastingDrawingResponse])
def list_casting_drawings():
    return []

@router.get("/{drawing_id}", response_model=CastingDrawingResponse)
def get_casting_drawing(drawing_id: int):
    raise HTTPException(status_code=404, detail="Not found")

@router.post("/", response_model=CastingDrawingResponse, status_code=201)
def create_casting_drawing(data: dict):
    return CastingDrawingResponse(id=1, casting_id=1, drawing_number="DWG001")

@router.put("/{drawing_id}", response_model=CastingDrawingResponse)
def update_casting_drawing(drawing_id: int, data: dict):
    raise HTTPException(status_code=404, detail="Not found")

@router.delete("/{drawing_id}", status_code=204)
def delete_casting_drawing(drawing_id: int):
    pass