"""
ASGI config for siteMain project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

#import os

from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from googleAPI.consumers import DatabaseConsumer

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siteMain.settings')

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
					path('', DatabaseConsumer.as_asgi()),
			])
		)
	),
})