from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Post, Group, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


def index(request):
    posts = Post.objects.all().select_related('author', 'group').order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).select_related('author').order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


def profile(request, username: str):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user.pk).select_related('author', 'group').order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'profile.html', {'author': user, 'page': page, 'paginator': paginator})


def post_view(request, username: str, post_id: int, form=CommentForm()):
    post = get_object_or_404(User, username=username).posts.select_related('author',).get(id=post_id)
    comments = post.comments.select_related('author', ).all()
    return render(request, 'post.html', {'post': post, 'comments': comments, 'form': form})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    return render(request, 'new.html', {'form': form})


@login_required
def post_edit(request, username: str, post_id: int):
    if username == request.user.username:
        post = Post.objects.select_related('author', 'group').get(id=post_id)
        form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('post', username=username, post_id=post_id)
            return render(request, 'new.html', {'form': form, 'username': username, 'post': post})
        return render(request, 'new.html', {'form': form, 'username': username, 'post': post})
    return redirect('post', username=username, post_id=post_id)


@login_required
def add_comment(request, username: str, post_id: int):
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.post = Post.objects.select_related('author', 'group').get(id=post_id)
            form.instance.author = request.user
            form.save()
            return redirect('post', username=username, post_id=post_id)
        return redirect('post', username=username, post_id=post_id, form=form)
    return redirect('post', username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
