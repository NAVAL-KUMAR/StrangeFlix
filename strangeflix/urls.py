
from products.views import HomeView, NewVideo, CommentView, VideoView
from django.contrib import admin
from django.urls import path
from products import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', HomeView.as_view()),
    path('new_video', NewVideo.as_view()),
    path('video/<int:id>', VideoView.as_view()),
    path('comment', CommentView.as_view()),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),

    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'),
    path('logout', views.logout, name='logout'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="products/password_reset.html"),
         name='reset_password'),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="products/password_reset_sent.html"),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="products/password_reset_form.html"),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="products/password_reset_done.html"),
         name='password_reset_complete'),

]
