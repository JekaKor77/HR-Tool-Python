class AuthError(Exception):
    def __init__(self, message="Authentication failed"):
        super().__init__(message)


class InvalidCredentials(AuthError):
    def __init__(self):
        super().__init__("Invalid credentials")


class UserAlreadyExists(AuthError):
    def __init__(self, message="User already exists"):
        super().__init__(message)


class OAuthError(AuthError):
    def __init__(self, message="OAuth error"):
        super().__init__(message)


class CSRFError(AuthError):
    def __init__(self):
        super().__init__("CSRF validation failed")
