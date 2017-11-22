=========
PyExpress
=========
PyExpress is a minimal web application framework for Python 3 inpired by ExpressJS.
The code is based on this tutorial_.

Install:
--------
.. code-block:: sh

    pip install pyexpress

Documentation:
==============
The Router is WSGI application. It accespts other WSGI applications as route handlers

.. code-block:: python

    from pyexpress.router import Router
    from webob import Response, exc

    # A function to handle a route. Routes are WSGI apps. the Router.app decorator wraps
    # the function in a WSGI app
    # req is a WebOb request object
    # id and name are path variables parsed by the router
    @Router.app
    def handler(req, id, name):
        # Extras passed to the route are accessed using the dict req.extras
        available = req.extras['available']
        
        if id in available:
            res_json = {
                'id': id,
                'name': name
            }
            res_body = json.dumps(res_json)
            return Response(body=res_body, content_type=Router.CONTENT_TYPE_JSON,
                            charset='UTF-8')
        else:
            return exc.HTTPNotFound()


    # Initialize the router
    app = Router()

    # Add routes to the router
    # - {id:\d+} is a path variable named id and matches the regex \d+ which matches
    # any number
    # {name} is path variable named name and matches any thing
    # - A route has an HTTP method, one of Router.METHOD_GET, Router.METHOD_POST,
    # Router.METHOD_PUT and Router.METHOD_DELETE
    # - available is an extra variable. all variables passed after the route handler
    # can be accessed as an extras dict from the request object
    app.use('/api/v1/resource/{id:\d+}/{name}',
            Router.METHOD_GET,
            handler,
            available=[1, 2 ,3, 4, 5])


Run like any WSGI application. For example, to run using Gunicorn, assuming the previous script is saved in `example.py` use

.. code-block:: sh

    gunicorn example:app

.. _tutorial: https://webob.readthedocs.io/en/stable/do-it-yourself.html
