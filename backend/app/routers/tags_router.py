from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=List[schemas.TagOut])
def list_tags(q: Optional[str] = None, db: Session = Depends(get_db), user: models.User = Depends(auth.get_current_user)):
    query = db.query(models.SymptomTag)
    if q:
        query = query.filter(models.SymptomTag.name.ilike(f"%{q}%"))
    return query.order_by(models.SymptomTag.name).limit(50).all()
