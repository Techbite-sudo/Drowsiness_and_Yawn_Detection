# your_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class DrowsinessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        user = await self.get_user(self.scope)
        if user and user.is_authenticated:
            # Check if the user has the necessary permissions
            if user.has_perm("some_permission"):
                data = json.loads(text_data)
                # Call your drowsiness detection function here with data
                # Update the user with the results using self.send(text_data=json.dumps(results))
            else:
                # Handle unauthorized users
                await self.close()
        else:
            # Handle unauthenticated users
            await self.close()

    @database_sync_to_async
    def get_user(self, scope):
        # Get the user from the request's scope
        user = scope.get("user")
        return user or AnonymousUser()
