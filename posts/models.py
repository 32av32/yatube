from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Text', )
    pub_date = models.DateTimeField(verbose_name='Publish date', auto_now_add=True)
    author = models.ForeignKey(User, verbose_name='Author', on_delete=models.CASCADE, related_name='posts')
    group = models.ForeignKey('Group', blank=True, null=True, verbose_name='Group', on_delete=models.CASCADE,
                              related_name='posts')
    image = models.ImageField(verbose_name='Image', upload_to='posts/', blank=True, null=True)


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Title')
    slug = models.SlugField(verbose_name='Slug', unique=True)
    description = models.TextField(verbose_name='Description')

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('Post', verbose_name='Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, verbose_name='Author', on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name='Text', )
    created_date = models.DateTimeField(verbose_name='Created_date', auto_now_add=True)