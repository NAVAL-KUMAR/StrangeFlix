
from django.contrib import admin
from django.urls import path,include
from products.views import HomeView, NewVideo, CommentView, VideoView, LogoutView
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls),
    #path('',views.home,name='home'),
    path('accounts/',include('accounts.urls')),
    path('accounts/',include('allauth.urls')),
    path('', HomeView.as_view()),
    path('new_video', NewVideo.as_view()),
    path('video/<int:id>', VideoView.as_view()),
    path('comment', CommentView.as_view()),
    #path('get_video/<file_name>', VideoFileView.as_view()),
    path('logout', LogoutView.as_view())

]
