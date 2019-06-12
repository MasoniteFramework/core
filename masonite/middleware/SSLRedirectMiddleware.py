"""SSL Redirect Middleware."""

from masonite.request import Request


class SSLRedirectMiddleware:
    """SSL Redirect Middleware."""

    def __init__(self, request: Request):
        """Inject Any Dependencies From The Service Container.

        Arguments:
            Request {masonite.request.Request} -- The Masonite request object
        """
        self.request = request

    def before(self):
        """Redirect user to secure URL."""
        from config import middleware
        if middleware.SSLRedirect:
            host = request.environ['HOST']
            url = 'https://{}{}'.format(host, self.request.path)
            return self.request.redirect(url)

    def after(self):
        pass
