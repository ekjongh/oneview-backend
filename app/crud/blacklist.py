from sqlalchemy.orm import Session

from .. import models, schemas

def create_blacklist(db: Session, token: schemas.TokenCreate, user_id: int):
    db_blacklist:schemas.TokenCreate = models.Blacklist(token=token.token, owner_id=user_id)
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist

def get_blacklist(db: Session, token: str):
    return db.query(models.Blacklist).filter(models.Blacklist.token == token).first()