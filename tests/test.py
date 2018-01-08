from unittest import TestCase
from webob.request import BaseRequest
from webob.response import Response
from PyExpress import Router, CONTENT_TYPE_HTML


# TODO: TEST HTTP methods other than get
# TODO: Test Router.all()
class TestPyExpress(TestCase):
    def setUp(self):
        self.app = Router()

    def test_simple_request(self):
        @self.app.get('/')
        @Router.app
        def simple_request_handler(req):
            return Response(body='OK', content_type=CONTENT_TYPE_HTML,
                            charset='UTF-8')

        req = BaseRequest.blank('/')
        res = req.get_response(self.app)

        self.assertIsInstance(res, Response)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, b'OK')
        self.assertEqual(res.charset, 'UTF-8')
        self.assertEqual(res.content_type, 'text/html')

    def test_path_basic_variables(self):
        @self.app.get('/{var}')
        @Router.app
        def path_basic_var_handler(req, var):
            return Response(body=var, content_type=CONTENT_TYPE_HTML,
                            charset='UTF-8')

        req = BaseRequest.blank('/value')
        res = req.get_response(self.app)

        self.assertIsInstance(res, Response)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, b'value')
        self.assertEqual(res.charset, 'UTF-8')
        self.assertEqual(res.content_type, 'text/html')

    def test_path_regex_variables(self):
        @self.app.get('/{var:\w\w\w\w\w}')
        @Router.app
        def path_regex_var_handler(req, var):
            return Response(body=var, content_type=CONTENT_TYPE_HTML,
                            charset='UTF-8')

        req = BaseRequest.blank('/value')
        res = req.get_response(self.app)

        self.assertIsInstance(res, Response)
        self.assertEqual(res.status, '200 OK')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, b'value')
        self.assertEqual(res.charset, 'UTF-8')
        self.assertEqual(res.content_type, 'text/html')

        req_invalid = BaseRequest.blank('/123456')
        res_invalid = req_invalid.get_response(self.app)
        self.assertIsInstance(res_invalid, Response)
        self.assertEqual(res_invalid.status, '404 Not Found')
        self.assertEqual(res_invalid.status_code, 404)
