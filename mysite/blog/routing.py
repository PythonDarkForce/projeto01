"""
WebSocket URL routing for blog application.
"""

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/blog/', consumers.BlogConsumer),
]
