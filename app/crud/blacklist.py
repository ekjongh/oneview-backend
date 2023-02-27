from sqlalchemy.orm import Session

from .. import models, schemas

def create_blacklist(db: Session, token: str, user_id: str):
    id = f"{token}_{user_id}"
    db_blacklist = models.Blacklist(id=id, token=token, owner_id=user_id)
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist

def get_blacklist(db: Session, token: str):
    return db.query(models.Blacklist).filter(models.Blacklist.token == token).first()