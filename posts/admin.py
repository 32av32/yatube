from django.contrib import admin
from .models import Post, Group

class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_filter = ('pub_date', )
    search_fields = ('text', )
    empty_value_display = '-пусто-'

class GroupModel(admin.ModelAdmin):
    list_display = ('pk', 'title', 'slug', 'description')
    list_editable = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title', )}
    empty_value_display = '-пусто-'

admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupModel)