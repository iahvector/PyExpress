import re
from webob import Request, Response
from webob import exc


class Router(object):
    """A WSGI compatible router """

    SUPPORTED_HTTP_METHODS = [
        'CONNECT',
        'DELETE',
        'HEAD',
        'GET',
        'OPTIONS',
        'PATCH',
        'POST',
        'PUT',
        'TRACE',
    ]

    _ROUTE_TEMPLATE_REGEX = re.compile(r'\{(\w+)(?::([^}]+))?\}')

    def __init__(self):
        self.routes = []
        self.middleware = []

    def __getattribute__(self, name):
        # This? or `object.__getattribute__(self, name)`?
        attr = super(Router, self)._getattr__(name)
        if not attr:
            namecaps = name.upper()
            if namecaps == 'ALL' or namecaps in Router.SUPPORTED_HTTP_METHODS:
                def add_method_route(self, method, path, handler, **kwargs):
                    self._add_method_route(self, namecaps, path, handler,
                                           **kwargs)
                attr = add_method_route
        return attr

    def _parse_route(self, template):
        """
        Takes a route template and parses it into regex

        Args:
            template: (str): A route template
        """
        regex = ''
        last_pos = 0
        for match in Router._ROUTE_TEMPLATE_REGEX.finditer(template):
            regex += re.escape(template[last_pos:match.start()])
            var_name = match.group(1)
            expr = match.group(2) or '[^/]+'
            expr = '(?P<{}>{})'.format(var_name, expr)
            regex += expr
            last_pos = match.end()
        regex += re.escape(template[last_pos:])
        regex = '^{}$'.format(regex)
        return re.compile(regex)

    def __call__(self, environ, start_response):
        """
        Makes object of the Router class callables as specified by the WSGI
        spceification

        Args:
            environ: (dict): The WSGI environment dict
            start_response: (callable): The WSGI response callable
        """
        req = Request(environ)
        for regex, method, app, kwargs in self.routes:
            match = regex.match(req.path_info)
            if match and req.method == method:
                req.urlvars = match.groupdict()

                if hasattr(req, 'extras'):
                    req.extras.update(kwargs)
                else:
                    req.extras = kwargs

                return app(environ, start_response)

        error = exc.HTTPNotFound()
        return error(environ, start_response)

    def use(self, template, app, **kwargs):
        """
        Use WSGI application to handle a route

        Args:
            template: (str): A route template
            app: (callable): A WSGI application
            **kwargs: (dict): Keyword arguments that will be passed to the app
        """
        regex = self._parse_route(template)
        self.middleware.append((regex, app, kwargs))

    def _add_method_route(self, method, path, handler, **kwargs):
        """
        Args:
            method: (str): An HTTP method, one of 'CONNECT', 'DELETE', 'HEAD',
                'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE'
        """
        pass
        # TODO Handle method call

    @staticmethod
    def app(func):
        """Decorates functions as WSGI apps"""
        def app_wrapper(environ, start_response):
            req = Request(environ)
            try:
                resp = func(req, **req.urlvars)
            except exc.HTTPException as e:
                resp = e
            if isinstance(resp, str):
                resp = Response(body=resp)
            return resp(environ, start_response)
        return app_wrapper
