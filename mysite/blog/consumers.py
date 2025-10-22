"""
WebSocket consumers for blog application.
Provides real-time updates for blog posts.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BlogConsumer(AsyncWebsocketConsumer):
    """
    Consumer for blog post updates.
    Clients can subscribe to receive real-time notifications when posts are created or updated.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.room_group_name = 'blog_updates'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        Currently used for ping/pong to keep connection alive.
        """
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')

        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong'
            }))

    async def blog_post_update(self, event):
        """
        Receive blog post update from room group.
        Forwards the update to the WebSocket.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'blog_update',
            'action': event['action'],
            'post': event['post']
        }))
