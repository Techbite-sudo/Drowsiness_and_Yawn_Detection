# your_project/routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from your_app.consumers import DrowsinessConsumer

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    # Add your WebSocket path here
                    # For example:
                    # path('ws/some_path/', DrowsinessConsumer.as_asgi()),
                ]
            )
        )
    }
)
