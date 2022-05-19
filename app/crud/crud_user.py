# email = obj_in.email,
# hashed_password = get_password_hash(obj_in.password),
# full_name = obj_in.full_name,
# is_superuser = obj_in.is_superuser,
# )
from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_userid(self, db: Session, *, userid: str) -> Optional[User]:
        return db.query(User).filter(User.userid == userid).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj: User = User(
            userid=obj_in.userid,
            hashed_password=get_password_hash(obj_in.password),
            # username=obj_in.username,
            # email=obj_in.email,
            # is_active=obj_in.is_active,
            # is_admin=obj_in.is_admin,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, userid: str, password: str) -> Optional[User]:
        user = self.get_by_userid(db, userid=userid)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_admin


user = CRUDUser(User)