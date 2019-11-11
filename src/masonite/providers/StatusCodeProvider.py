"""A StatusProvider Service Provider."""

from ..response import Response
from ..provider import ServiceProvider
from ..helpers import config


class ServerErrorExceptionHook:

    def load(self, app):
        from config import application
        if application.DEBUG:
            return

        request = app.make('Request')

        request.status(500)
        if app.make('ViewClass').exists('errors/500'):
            rendered_view = app.make('View')('errors/500')
        else:
            rendered_view = app.make('View')(
                config('application.templates.statuscode', '/masonite/snippets/statuscode'), {'code': '500 Internal Server Error'})

        request.app().make(Response).view(rendered_view)


class StatusCodeProvider(ServiceProvider):

    def register(self):
        self.app.bind('ServiceErrorExceptionHook', ServerErrorExceptionHook())

    def boot(self):
        request = self.app.make('Request')
        response = self.app.make(Response)
        if request.is_status(200):
            return

        if request.get_status() in (500, 405, 404):
            if request.header('Content-Type') == 'application/json':
                # Returns json response when we want the client to receive a json response
                json_response = {'error': {'status': request.get_status()}}
                response.view(json_response, status=request.get_status())
            else:
                # Returns html response when json is not explicitly specified
                if self.app.make('ViewClass').exists('errors/{}'.format(request.get_status())):
                    rendered_view = self.app.make('View')(
                        'errors/{}'.format(request.get_status()))
                else:
                    rendered_view = self.app.make('View')(config('application.templates.statuscode', '/masonite/snippets/statuscode'), {
                        'code': request.get_status_code()
                    })

                response.view(rendered_view, status=request.get_status())
