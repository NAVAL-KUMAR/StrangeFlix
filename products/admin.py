from django.contrib import admin
from .models import Comment,Video,Like
# Register your models here.

admin.site.register(Video)
admin.site.register(Comment)
admin.site.register(Like)