import re
from webob import Request, Response
from webob import exc


class Router(object):
    """A WSGI compatible router """
    METHOD_GET = 'GET'
    METHOD_POST = 'POST'
    METHOD_PUT = 'PUT'
    METHOD_DELETE = 'DELETE'
    METHODS = [METHOD_GET, METHOD_POST, METHOD_PUT, METHOD_DELETE]

    CONTENT_TYPE_HEADER = 'Content-Type'
    CONTENT_TYPE_JSON = 'application/json'
    CONTENT_TYPE_HTML = 'text/html'

    _ROUTE_TEMPLATE_REGEX = re.compile(r'\{(\w+)(?::([^}]+))?\}')

    def __init__(self):
        self.routes = []

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
        return regex

    def __call__(self, environ, start_response):
        """
        Makes object of the Router class callables as specified by the WSGI
        spceification

        Args:
            environ: (dict): The WSGI environment dict
            start_response: (callable): The WSGI response callable
        """
        req = Request(environ)
        for regex, method, app, vars in self.routes:
            match = regex.match(req.path_info)
            if match and req.method == method:
                req.urlvars = match.groupdict()

                if hasattr(req, 'extras'):
                    req.extras.update(vars)
                else:
                    req.extras = vars

                return app(environ, start_response)

        error = exc.HTTPNotFound()
        return error(environ, start_response)

    def use(self, template, method, app, **vars):
        """
        Use WSGI application to handle a route

        Args:
            template: (str): A route template
            method: (str): An HTTP method, one of 'GET', 'POST', 'PUT',
                'DELETE'
            app: (callable): A WSGI application
            **vars: (dict): Keyword arguments that will be passed to the app
        """
        if method not in Router.METHODS:
            raise ValueError('Method {} not supported'.format(method))
        regex = re.compile(self._parse_route(template))
        self.routes.append((regex, method, app, vars))

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
