import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from .views import drowsiness_detection


class MonitoringConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user != AnonymousUser():
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start":
            # Start drowsiness detection
            webcam_index = 0  # Default webcam index
            ear_thresh = self.user.user_settings.ear_threshold
            ear_frames = self.user.user_settings.ear_frames
            yawn_thresh = self.user.user_settings.yawn_threshold

            await self.send(
                text_data=json.dumps(
                    {"action": "start", "message": "Monitoring started."}
                )
            )
            await drowsiness_detection(
                webcam_index,
                ear_thresh,
                ear_frames,
                yawn_thresh,
                self.user,
                self.channel_layer,
            )

        elif action == "stop":
            # Stop drowsiness detection
            await self.send(
                text_data=json.dumps(
                    {"action": "stop", "message": "Monitoring stopped."}
                )
            )

    async def send_message(self, event):
        await self.send(text_data=json.dumps(event))
