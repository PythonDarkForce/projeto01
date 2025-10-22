from django.test import TestCase
from django.contrib.auth.models import User
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from blog.routing import websocket_urlpatterns
from blog.models import Post
from blog.utils import notify_post_update
import json


class PostModelTestCase(TestCase):
    """Test cases for Post model."""

    def setUp(self):
        """Create test user and post."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_post(self):
        """Test creating a blog post."""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            text='This is a test post content.'
        )
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.author, self.user)
        self.assertEqual(str(post), 'Test Post')

    def test_post_published(self):
        """Test publishing a blog post."""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            text='Content'
        )
        self.assertIsNone(post.published_date)
        post.published()
        self.assertIsNotNone(post.published_date)


class WebSocketTestCase(TestCase):
    """Test cases for WebSocket functionality."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    async def test_websocket_connect(self):
        """Test WebSocket connection."""
        application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(application, "/ws/blog/")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_websocket_ping_pong(self):
        """Test WebSocket ping/pong."""
        application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(application, "/ws/blog/")
        await communicator.connect()
        
        # Send ping
        await communicator.send_json_to({'type': 'ping'})
        
        # Receive pong
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'pong')
        
        await communicator.disconnect()


class UtilsTestCase(TestCase):
    """Test cases for utility functions."""

    def setUp(self):
        """Create test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_notify_post_update(self):
        """Test that notify_post_update doesn't raise exceptions."""
        post = Post.objects.create(
            author=self.user,
            title='Test Post',
            text='Content'
        )
        # This should not raise an exception
        try:
            notify_post_update(post, 'create')
        except Exception as e:
            self.fail(f"notify_post_update raised an exception: {e}")
