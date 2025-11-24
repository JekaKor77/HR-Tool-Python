from auth.cookies import CookiePack
from auth.exceptions import InvalidCredentials, AuthError
from auth.repositories.refresh_token_repository import RefreshTokenRepository
from auth.repositories.user_repository import UserRepository
from auth.schemas import UserRegister, OAuthProfile, UserOauthRegister
from auth.services.oauth_service import OAuthService
from auth.services.token_service import TokenService
from auth.utils import verify_password


class AuthService:
    def __init__(self):
        self.tokens = TokenService()
        self.oauth = OAuthService()

    def init_app(self, app):
        self.oauth.init_app(app)

    def register(self, data: dict):
        csrf = self.tokens.make_csrf()

        user_data = UserRegister(**data)
        user = UserRepository.register_user(user_data)

        cookies = CookiePack()
        cookies.set("csrf_token", csrf, secure=False, samesite="Lax")

        return {"message": "User registered", "user": user}, cookies

    def login(self, data: dict):
        self.tokens.check_csrf()

        email = data.get("email")
        password = data.get("password")

        user = UserRepository.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentials()

        access = self.tokens.create_access(str(user.id))
        refresh = self.tokens.issue_refresh(str(user.id))

        cookies = CookiePack()
        cookies.set(
            "refresh_token",
            refresh,
            httponly=True,
            secure=False,
            samesite="Strict",
            path="/auth/refresh"
        )
        cookies.set(
            "csrf_token",
            self.tokens.make_csrf(),
            secure=False,
            samesite="Lax"
        )

        return {"access_token": access}, cookies

    def logout(self):
        self.tokens.check_csrf()

        refresh = self.tokens.get_refresh_from_request()
        if refresh:
            RefreshTokenRepository.revoke(refresh)

        cookies = CookiePack()
        cookies.delete("refresh_token", path="/auth/refresh")

        return {"message": "logged out"}, cookies

    def logout_all(self):
        refresh = self.tokens.get_refresh_from_request()
        if refresh:
            try:
                user_id = self.tokens.validate_refresh()
                RefreshTokenRepository.revoke_all_for_user(user_id)
            except AuthError:
                pass

        cookies = CookiePack()
        cookies.delete("refresh_token", path="/auth/refresh")

        return {"message": "logged out from all devices"}, cookies

    def refresh(self):
        self.tokens.check_csrf()

        user_id = self.tokens.validate_refresh()

        new_access = self.tokens.create_access(user_id)
        new_refresh = self.tokens.issue_refresh(user_id)

        cookies = CookiePack()
        cookies.set(
            "refresh_token",
            new_refresh,
            httponly=True,
            secure=False,
            samesite="Strict",
            path="/auth/refresh"
        )
        cookies.set(
            "csrf_token",
            self.tokens.make_csrf(),
            secure=False,
            samesite="Lax"
        )

        return {"access_token": new_access}, cookies

    def oauth_redirect(self, provider: str):
        return self.oauth.redirect(provider)

    def oauth_callback(self, provider: str):
        profile: OAuthProfile = self.oauth.fetch_user(provider)
        user = UserRepository.get_user_by_email(profile.email)

        if not user:
            reg = UserOauthRegister(
                first_name=profile.first_name,
                last_name=profile.last_name,
                email=profile.email,
                oauth_provider=profile.provider,
                oauth_id=profile.oauth_id
            )
            user = UserRepository.register_oauth_user(reg)

        RefreshTokenRepository.revoke_all_for_user(str(user.id))

        new_access = self.tokens.create_access(str(user.id))
        new_refresh = self.tokens.issue_refresh(str(user.id))

        cookies = CookiePack()
        cookies.set(
            "refresh_token",
            new_refresh,
            httponly=True,
            secure=False,
            samesite="Strict",
            path="/auth/refresh"
        )
        cookies.set(
            "csrf_token",
            self.tokens.make_csrf(),
            secure=False,
            samesite="Lax"
        )

        return {"access_token": new_access}, cookies