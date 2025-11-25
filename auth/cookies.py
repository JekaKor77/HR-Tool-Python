

class CookiePack:
    def __init__(self):
        self.cookies = []

    def set(self, name, value, **options):
        self.cookies.append((name, value, options))

    def delete(self, name, path="/", domain=None):
        self.cookies.append((name, "", {"path": path, "domain": domain, "max_age": 0, "expires": 0}))

    def apply_to(self, response):
        for name, value, opts in self.cookies:
            if value == "" and opts.get("max_age") == 0:
                response.delete_cookie(name, path=opts.get("path", "/"), domain=opts.get("domain"))
            else:
                response.set_cookie(
                    name,
                    value,
                    path=opts.get("path", "/"),
                    domain=opts.get("domain"),
                    max_age=opts.get("max_age"),
                    expires=opts.get("expires"),
                    secure=opts.get("secure", False),
                    httponly=opts.get("httponly", True),
                    samesite=opts.get("samesite", "Lax")
                )
