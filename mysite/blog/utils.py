"""
Utilities for sending real-time updates via WebSocket.
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def notify_post_update(post, action='update'):
    """
    Send notification about post update to all connected WebSocket clients.
    
    Args:
        post: Post instance
        action: Type of action ('create', 'update', 'delete')
    """
    channel_layer = get_channel_layer()
    if channel_layer:
        post_data = {
            'id': post.id,
            'title': post.title,
            'author': post.author.username,
            'created_date': post.created_date.isoformat() if post.created_date else None,
            'published_date': post.published_date.isoformat() if post.published_date else None,
        }
        
        async_to_sync(channel_layer.group_send)(
            'blog_updates',
            {
                'type': 'blog_post_update',
                'action': action,
                'post': post_data
            }
        )
