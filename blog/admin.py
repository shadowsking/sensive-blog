from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'text', 'author']
    raw_id_fields = ('post', 'author', )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author']
    raw_id_fields = ('author', 'tags', 'likes',)


admin.site.register(Tag)
