from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.models.user import User


def get_or_create_default_user(db: Session) -> User:
    """Return the configured default user, creating it when it does not exist."""
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == settings.DEFAULT_USERNAME,
                User.email == settings.DEFAULT_EMAIL,
            )
        )
        .first()
    )
    if user:
        if not user.is_active:
            user.is_active = True
            db.commit()
            db.refresh(user)
        return user

    user = User(
        email=settings.DEFAULT_EMAIL,
        username=settings.DEFAULT_USERNAME,
        hashed_password=security.get_password_hash(settings.DEFAULT_PASSWORD),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
    if user:
        if not user.is_active:
            user.is_active = True
            db.commit()
            db.refresh(user)
        return user

    user = User(
        email=settings.DEFAULT_EMAIL,
        username=settings.DEFAULT_USERNAME,
        hashed_password=security.get_password_hash(settings.DEFAULT_PASSWORD),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
