from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=300)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    upload_date = models.DateTimeField() 
    type=models.CharField(max_length=100)
    category=models.CharField(max_length=100)
    filename=models.FileField(upload_to='',blank=True)
    thumbtail=models.ImageField(upload_to='',blank=True)
    link=models.URLField(max_length=200,blank=True)
    subtitle=models.TextField()
    premium=models.BooleanField()

    def __str__(self):
        return self.title

class Comment(models.Model):
    text = models.TextField(max_length=300)
    datetime = models.DateTimeField(auto_now=True, blank=False, null=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def date_preety(self):
        return self.datetime.strftime('%b %e %Y')
