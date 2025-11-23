

class CookiePack:
    def __init__(self):
        self.cookies = []

    def set(self, name, value, **options):
        self.cookies.append((name, value, options))

    def delete(self, name, **options):
        self.cookies.append((name, None, {"delete": True, **options}))

    def apply_to(self, response):
        for name, value, opts in self.cookies:
            if opts.get("delete"):
                response.delete_cookie(name, **opts)
            else:
                response.set_cookie(name, value, **opts)
