from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Post, Group
from .forms import NewPostForm

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
        form = NewPostForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = NewPostForm()
    return render(request, 'new.html', {'form': form})
