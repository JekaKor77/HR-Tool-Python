
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from auth.exceptions import UserAlreadyExists, AuthError
from auth.schemas import UserRead, UserOauthRegister, UserRegister
from db.models import RolesEnum, User
from auth.utils import hash_password
from db.session import sync_session_factory


class UserRepository:
    @staticmethod
    def get_user_by_email(email: str):
        try:
            with sync_session_factory() as session:
                query = select(User).where(User.email == email)
                result = session.execute(query)
                return result.scalar_one_or_none()
        except Exception as e:
            raise AuthError("Failed to fetch user") from e

    @staticmethod
    def register_user(data: UserRegister):
        try:
            with sync_session_factory() as session:
                hashed_pw = hash_password(data.password)
                user = User(
                    first_name=data.first_name,
                    last_name=data.last_name,
                    email=data.email,
                    password_hash=hashed_pw,
                    role=RolesEnum.interviewer
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                return UserRead.model_validate(user).model_dump()

        except IntegrityError:
            raise UserAlreadyExists()
        except Exception as e:
            raise AuthError("Failed to register user") from e

    @staticmethod
    def register_oauth_user(data: UserOauthRegister):
        try:
            with sync_session_factory() as session:
                user = User(
                    first_name=data.first_name,
                    last_name=data.last_name,
                    email=data.email,
                    oauth_provider=data.oauth_provider,
                    oauth_id=data.oauth_id,
                    role=RolesEnum.interviewer
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                return user

        except IntegrityError:
            session.rollback()
            raise UserAlreadyExists("User already exists or OAuth ID duplicated")
        except Exception as e:
            session.rollback()
            raise AuthError("Failed to register OAuth user") from e
