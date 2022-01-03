from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.urls import reverse
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)

User = get_user_model()


class IndexView(ListView):
    model = Post
    queryset = Post.objects.all().select_related('author', 'group').prefetch_related('comments')
    template_name = 'index.html'
    paginate_by = 10
    ordering = '-pub_date'


class GroupView(ListView):
    model = Post
    template_name = 'group.html'
    paginate_by = 10
    ordering = '-pub_date'

    def get_queryset(self):
        return Post.objects.filter(group__slug=self.kwargs['slug'])\
            .select_related('author', 'group').prefetch_related('comments')

    def get_context_data(self, *, object_list=None, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs['slug'])
        context_data = super().get_context_data(object_list=object_list, **kwargs)
        context_data['group'] = group
        return context_data


class ProfileView(ListView):
    model = Post
    template_name = 'profile.html'
    paginate_by = 10
    ordering = '-pub_date'

    def get_queryset(self):
        return Post.objects.filter(author__username=self.kwargs['username']) \
            .select_related('author', 'group')

    @property
    def extra_context(self):
        return {
            'author': get_object_or_404(User, username=self.kwargs['username']),
            'following': Follow.objects.filter(user=self.request.user).filter(author__username=self.kwargs['username'])
        }


class PostView(DetailView):
    model = Post
    queryset = Post.objects.all().select_related('author', 'group').prefetch_related('comments')
    template_name = 'post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['form'] = CommentForm()
        return context_data


class NewPostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'new.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class PostEditView(LoginRequiredMixin, AccessMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'new.html'
    context_object_name = 'post'

    def get_success_url(self):
        return reverse('post',
                       kwargs={
                           'username': self.kwargs['username'],
                           'post_id': self.kwargs['post_id'],
                       })

    @property
    def extra_context(self):
        return {'username': self.kwargs['username']}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.username != self.kwargs['username']:
                return render(request, 'alert.html', {'message': 'У вас нет доступа на редактирование поста!'})
            return super().dispatch(request, *args, **kwargs)
        return redirect('login')


class PostDeleteView(DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'delete_post.html'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.kwargs['username']})

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.username != self.kwargs['username']:
                return render(request, 'alert.html', {'message': 'У вас нет доступа на удаление поста!'})
            return super().dispatch(request, *args, **kwargs)
        return redirect('login')


class AddCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comments.html'

    def form_valid(self, form):
        form.instance.post = Post.objects.select_related('author', 'group').get(id=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post',
                       kwargs={
                           'username': self.kwargs['username'],
                           'post_id': self.kwargs['post_id'],
                       })

    @property
    def extra_context(self):
        return {
            'username': get_object_or_404(User, username=self.kwargs['username']),
            'post_id': self.kwargs['post_id']
        }


class SubscriptionPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'follow.html'
    paginate_by = 10

    def get_queryset(self):
        posts = Post.objects.filter(author__following__user=self.request.user)
        return posts


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        print(f'author: {author}; user: {request.user}')
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
