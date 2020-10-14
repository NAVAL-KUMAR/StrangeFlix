from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=300)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    path = models.CharField(max_length=60)
    imName = models.CharField(max_length=60)
    datetime = models.DateTimeField(auto_now=True, blank=False, null=False) #todo: auto_now=True
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

class Comment(models.Model):
    text = models.TextField(max_length=300)
    datetime = models.DateTimeField(auto_now=True, blank=False, null=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

class Like(models.Model):
    like = models.IntegerField(default=0)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

class Favourite(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

class Comment(models.Model):
    datetime = models.DateTimeField(auto_now=True, blank=False, null=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)



