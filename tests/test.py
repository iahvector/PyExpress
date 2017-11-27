from unittest import TestCase
from webob.request import BaseRequest
from webob.response import Response
from PyExpress.router import Router


class TestPyExpress(TestCase):
    def setUp(self):
        self.app = Router()

    def test_simple_request(self):
        @Router.app
        def simple_request_handler(req):
            return Response(body='OK', content_type=Router.CONTENT_TYPE_HTML,
                            charset='UTF-8')

        self.app.use('/', Router.METHOD_GET, simple_request_handler)

        req = BaseRequest.blank('/')
        res = req.get_response(self.app)

        self.assertIsInstance(res, Response)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, 'OK')
        self.assertEqual(res.charset, 'UTF-8')
        self.assertEqual(res.content_type, 'text/html')

    def test_path_basic_variables(self):
        @Router.app
        def path_basic_var_handler(req, var):
            return Response(body=var, content_type=Router.CONTENT_TYPE_HTML,
                            charset='UTF-8')

        self.app.use('/{var}', Router.METHOD_GET, path_basic_var_handler)

        req = BaseRequest.blank('/value')
        res = req.get_response(self.app)

        self.assertIsInstance(res, Response)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, 'value')
        self.assertEqual(res.charset, 'UTF-8')
        self.assertEqual(res.content_type, 'text/html')

    def test_path_regex_variables(self):
        @Router.app
        def path_regex_var_handler(req, var):
            return Response(body=var, content_type=Router.CONTENT_TYPE_HTML,
                            charset='UTF-8')

        self.app.use('/{var:\w\w\w\w\w}', Router.METHOD_GET,
                     path_regex_var_handler)

        req = BaseRequest.blank('/value')
        res = req.get_response(self.app)

        self.assertIsInstance(res, Response)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, 'value')
        self.assertEqual(res.charset, 'UTF-8')
        self.assertEqual(res.content_type, 'text/html')

        req_invalid = BaseRequest.blank('/123456')
        res_invalid = req_invalid.get_response(self.app)
        self.assertIsInstance(res_invalid, Response)
        self.assertEqual(res_invalid.status, '404 Not Found')
        self.assertEqual(res_invalid.status_code, 404)
