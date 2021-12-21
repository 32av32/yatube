from django.urls import path
from . import views
from django.views.decorators.cache import cache_page
from .views import (IndexView,
                    GroupView,
                    ProfileView,
                    PostView,
                    NewPostView,
                    PostEditView,
                    AddCommentView)

urlpatterns = [
    path('', cache_page(20)(IndexView.as_view()), name='index'),
    path('group/<slug:slug>/', GroupView.as_view(), name='group'),
    path('new/', NewPostView.as_view(), name='new_post'),
    path('<str:username>/', ProfileView.as_view(), name='profile'),
    path('<str:username>/<int:post_id>/', PostView.as_view(), name='post'),
    path('<str:username>/<int:post_id>/edit/', PostEditView.as_view(), name='post_edit'),
    path('<str:username>/<int:post_id>/comment/', AddCommentView.as_view(), name='add_comment')
]