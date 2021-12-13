from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import NewPostForm

def index(request):
    # posts = Post.objects.order_by('-pub_date')[:10]
    posts = list(Post.objects.all().select_related('author').order_by('-pub_date')[:10])

    return render(request, 'index.html', {'posts': posts, })

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    # posts = Post.objects.filter(group=group).order_by('-pub_date')[:12]
    posts = list(Post.objects.filter(group=group).select_related('author').order_by('-pub_date')[:12])
    return render(request, 'group.html', {'group': group, 'posts': posts})

def new_post(request):
    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = NewPostForm()
    return render(request, 'new.html', {'form': form})
