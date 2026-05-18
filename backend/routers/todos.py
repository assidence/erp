"""
Todos API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.all_models import Todo
from backend.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from backend.config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.get("/", response_model=list[TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    """List all todos, ordered by created_at desc."""
    todos = db.query(Todo).order_by(Todo.created_at.desc()).all()
    return todos


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a single todo by ID."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
def create_todo(data: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo."""
    todo = Todo(
        content=data.content,
        is_done=1 if data.is_done else 0,
        due_date=data.due_date,
        completed_at=data.completed_at
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    logger.info(f"Created todo id={todo.id}")
    return todo


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, data: TodoUpdate, db: Session = Depends(get_db)):
    """Update a todo (toggle done, edit content)."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    if data.content is not None:
        todo.content = data.content
    if data.is_done is not None:
        todo.is_done = 1 if data.is_done else 0
        todo.completed_at = datetime.now() if data.is_done else None
    if data.due_date is not None:
        todo.due_date = data.due_date
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo."""
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()


@router.post("/cleanup-checked", status_code=status.HTTP_204_NO_CONTENT)
def cleanup_checked_todos(db: Session = Depends(get_db)):
    """Delete all checked todos (auto-cleanup)."""
    db.query(Todo).filter(Todo.is_done == 1).delete()
    db.commit()
    logger.info("Cleaned up checked todos")
