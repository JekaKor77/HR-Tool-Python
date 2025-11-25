from flask import jsonify, request, redirect, make_response

from .exceptions import CSRFError
from .services.auth_service import AuthService


class AuthManager:

    def __init__(self, app=None):
        self.service = AuthService()
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.service.init_app(app)
        app.extensions["auth_manager"] = self

    def register(self, data):
        result, cookies = self.service.register(data)
        response = jsonify(result)
        cookies.apply_to(response)
        return response, 201

    def login(self, data):
        result, cookies = self.service.login(data)
        response = jsonify(result)
        cookies.apply_to(response)
        return response

    def logout(self):
        print("=== Logout called ===")
        print("Request cookies:", request.cookies)
        print("Request headers:", request.headers)

        try:
            result, cookies = self.service.logout()
            response = jsonify(result)
            cookies.apply_to(response)
            print("Logout successful, cookies applied:", cookies.cookies)
            return response
        except CSRFError:
            print("CSRF validation failed!")
            raise
        except Exception as e:
            print("Logout failed with exception:", e)
            raise

    def logout_all(self):
        result, cookies = self.service.logout_all()
        response = jsonify(result)
        cookies.apply_to(response)
        return response

    def refresh(self):
        result, cookies = self.service.refresh()
        response = jsonify(result)
        cookies.apply_to(response)
        return response

    def oauth_redirect(self, provider):
        return self.service.oauth_redirect(provider)

    def oauth_callback(self, provider):
        result, cookies = self.service.oauth_callback(provider)
        token = result.get('access_token', '')

        html = f"""
            <html>
              <body>
                <script>
                    sessionStorage.setItem('access_token', "{token}");
                    const params = new URLSearchParams(window.location.search);
                    const next = params.get('next') || '/';
                    window.location.replace(next);
                </script>
              </body>
            </html>
            """

        response = make_response(html)
        cookies.apply_to(response)
        return response
