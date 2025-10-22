from django.shortcuts import render
from .models import Post


def posts_list(request):
    """Display all blog posts with real-time update capability."""
    posts = Post.objects.all().order_by('-created_date')
    return render(request, 'blog/posts.html', {'posts': posts})
