from authlib.integrations.flask_client import OAuth
from flask import url_for

from app_config import settings
from auth.exceptions import OAuthError
from auth.schemas import OAuthProfile


class OAuthService:
    def __init__(self):
        self.oauth = OAuth()

        self.google = None
        self.github = None
        self.linkedin = None

    def init_app(self, app):
        self.oauth.init_app(app)

        self.google = self.oauth.register(
            name="google",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            api_base_url="https://openidconnect.googleapis.com/v1/",
            client_kwargs={'scope': 'openid email profile'}
        )

        self.github = self.oauth.register(
            name='github',
            client_id=settings.GITHUB_CLIENT_ID,
            client_secret=settings.GITHUB_CLIENT_SECRET,
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'}
        )

        self.linkedin = self.oauth.register(
            name='linkedin',
            client_id=settings.LINKEDIN_CLIENT_ID,
            client_secret=settings.LINKEDIN_CLIENT_SECRET,
            access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
            authorize_url='https://www.linkedin.com/oauth/v2/authorization',
            api_base_url='https://api.linkedin.com/v2/',
            client_kwargs={'scope': 'r_liteprofile r_emailaddress'}
        )

    def redirect(self, provider: str):
        client = getattr(self, provider)
        return client.authorize_redirect(
            url_for("auth.oauth_callback", provider=provider, _external=True)
        )

    def fetch_user(self, provider: str) -> OAuthProfile:
        client = getattr(self, provider)
        token = client.authorize_access_token()

        if provider == "google":
            info = client.get("userinfo").json()
            return OAuthProfile(
                email=info["email"],
                first_name=info.get("given_name", ""),
                last_name=info.get("family_name", ""),
                provider="google",
                oauth_id=info["sub"]
            )

        if provider == "github":
            info = client.get("user").json()
            email = info.get("email")

            if not email:
                emails = client.get("user/emails").json()
                email = next((e["email"] for e in emails if e.get("primary")), None)

            if not email:
                raise OAuthError("GitHub email not available")

            name_parts = (info.get("name") or "").split(" ")

            return OAuthProfile(
                email=email,
                first_name=name_parts[0],
                last_name=name_parts[1] if len(name_parts) > 1 else "",
                provider="github",
                oauth_id=str(info["id"])
            )

        if provider == "linkedin":
            profile = client.get("me").json()
            email_data = client.get(
                "emailAddress?q=members&projection=(elements*(handle~))"
            ).json()

            return OAuthProfile(
                email=email_data["elements"][0]["handle~"]["emailAddress"],
                first_name=profile.get("localizedFirstName", ""),
                last_name=profile.get("localizedLastName", ""),
                provider="linkedin",
                oauth_id=profile["id"]
            )

        raise OAuthError("Unknown provider")

