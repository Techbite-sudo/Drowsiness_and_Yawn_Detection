# your_project/routing.py
from os import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from your_app.consumers import DrowsinessConsumer

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    # Add your WebSocket path here
                    path("ws/detect_drowsiness/", DrowsinessConsumer.as_asgi()),
                ]
            )
        )
    }
)
