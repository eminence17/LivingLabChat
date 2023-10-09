"""
WSGI config for LivingLabChat project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import socketio
from api.views import sio

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LivingLabChat.settings')

django_app= get_wsgi_application()

application = socketio.WSGIApp(sio, django_app)

# import eventlet
# import eventlet.wsgi
# eventlet.wsgi.server(eventlet.listen(('', 8000)), application)

# from gevent import pywsgi
# # from
# # from geventwebsocket.handler import WebSocketHandler
# pywsgi.WSGIServer(('',8000), application).serve_forever()
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
app = socketio.WSGIApp(sio)
pywsgi.WSGIServer(('', 8000), application,
                  handler_class=WebSocketHandler).serve_forever()