from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete = models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateField(default = timezone.now)
    published_date = models.DateField(blank = True, null=True)

    def published(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


@receiver(post_save, sender=Post)
def post_saved(sender, instance, created, **kwargs):
    """Send WebSocket notification when a post is created or updated."""
    from .utils import notify_post_update
    action = 'create' if created else 'update'
    notify_post_update(instance, action)


@receiver(post_delete, sender=Post)
def post_deleted(sender, instance, **kwargs):
    """Send WebSocket notification when a post is deleted."""
    from .utils import notify_post_update
    notify_post_update(instance, 'delete')
