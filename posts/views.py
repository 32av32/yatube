from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Post, Group
from .forms import PostForm

User = get_user_model()

def index(request):
    posts = Post.objects.all().select_related('author').order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'index.html', {'page': page, 'paginator': paginator})

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).select_related('author').order_by('-pub_date')[:12]
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})

@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})

def profile(request, username: str):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user.pk).select_related('author', 'group')
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'profile.html', {'author': user, 'page': page, 'paginator': paginator})


def post_view(request, username: str, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(User, username=username)
    posts_count = Post.objects.filter(author=user.pk).count()
    return render(request, 'post.html', {'author': user, 'post': post, 'posts_count': posts_count})

@login_required
def post_edit(request, username: str, post_id: int):
    if username == request.user.username:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=Post.objects.get(id=post_id))
            if form.is_valid():
                form.save()
                return redirect('profile', username=username)
            return render(request, 'post.html', {'form': form})
        form = PostForm(instance=Post.objects.get(id=post_id))
        return render(request, 'new.html', {'form': form, 'username': username, 'post_id': post_id})
    return redirect('profile', username=username)