from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/production-operations", tags=["production-operations"])

class ProductionOperationResponse(BaseModel):
    id: int
    plan_id: int
    operation_name: str = ""
    sequence: int
    status: str = "pending"

@router.get("/", response_model=List[ProductionOperationResponse])
def list_operations():
    return []

@router.get("/{operation_id}", response_model=ProductionOperationResponse)
def get_operation(operation_id: int):
    raise HTTPException(status_code=404, detail="Not found")

@router.post("/", response_model=ProductionOperationResponse, status_code=201)
def create_operation(data: dict):
    return ProductionOperationResponse(id=1, plan_id=1, operation_name="Op1", sequence=1, status="pending")

@router.put("/{operation_id}", response_model=ProductionOperationResponse)
def update_operation(operation_id: int, data: dict):
    raise HTTPException(status_code=404, detail="Not found")

@router.delete("/{operation_id}", status_code=204)
def delete_operation(operation_id: int):
    pass
