from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from .models import Video, Comment
from django.core.files.storage import FileSystemStorage
import os
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import auth
from django.views.generic import View
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from .token_generator import generate_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.conf import settings
import threading
from django.utils import timezone
from django.core.files.storage import FileSystemStorage



def home(request):
    return render(request, 'products/home.html');


def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        bval = False
        if len(name) < 4:
            messages.add_message(request, messages.ERROR, 'your name must have lenght>4')
            bval = True
        if (password != cpassword):
            messages.add_message(request, messages.ERROR, 'password do not match!')
            bval = True
        if len(password) < 6:
            messages.add_message(request, messages.ERROR, 'passwword at least 6 length!')
            bval = True
        try:
            if User.object.get(email=email):
                messages.add_message(request, messages.ERROR, 'Email is taken!')
                bval = True
        except Exception as identifier:
            pass

        if bval:
            return render(request, 'products/signup.html')
        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.is_active = False
        user.save()
        email_subject = 'Activate Your Account'
        current_site = get_current_site(request)
        message = render_to_string('products/activate.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user),
        })
        email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [email]
        )
        EmailThread(email_message).start()
        messages.add_message(request, messages.SUCCESS, 'account created succesfully')
        return HttpResponse('We have sent you an email, please confirm your email address to complete registration')
    else:
        return render(request, 'products/signup.html')


class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.add_message(request, messages.SUCCESS, 'account activated successfully')
            return redirect('login')
        return render(request, 'products/signup.html', status=401)


class EmailThread(threading.Thread):

    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


def login(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.add_message(request, messages.ERROR, 'username or password is incorrect !')
            return render(request, 'products/login.html')
    else:
        return render(request, 'products/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')


#View for index.html
#fetching all the video object and displaying it

class HomeView(View):
    template_name = 'products/index.html'
    def get(self, request):
        most_recent_videos = Video.objects.order_by('-upload_date')
        return render(request, self.template_name, {'menu_active_item': 'home', 'most_recent_videos': most_recent_videos})




#View to view Video

class VideoView(View):
    template_name = 'products/video.html'

    def get(self, request, id):
        #fetch video from DB by ID
        video_by_id = get_object_or_404(Video,pk=id)
        
        context = {'video_by_id':video_by_id}

        comments = Comment.objects.filter(video__id=id).order_by('-datetime')[:5]
        context['comments'] = comments
        most_recent_videos = Video.objects.order_by('-upload_date')[:8]
        context['most_recent_videos'] = most_recent_videos
        return render(request, self.template_name, context)


#comment under video in video

class CommentView(View):
    template_name = 'products/comment.html'

    def post(self, request):
        # pass filled out HTML-Form from View to CommentForm()
        form = CommentForm(request.POST)
        if form.is_valid():
            # create a Comment DB Entry
            text = form.cleaned_data['text']
            video_id = request.POST['video']
            video = Video.objects.get(id=video_id)

            new_comment = Comment(text=text, user=request.user, video=video)
            new_comment.save()
            return HttpResponseRedirect('video/{}'.format(str(video_id)))
        return HttpResponse('This is Register view. POST Request.')

#view to upload video

def new_video(request):
    if request.method=='POST':
        bvl=False
        video=Video()
        video.title =request.POST.get('video_title')
        video.description =request.POST.get('video_description')
        play=request.FILES.get('video_filename')
        img=request.FILES.get('video_thumbtail')
        video.type=request.POST.get('video_type')
        url=request.POST.get('video_link')
        if request.POST.get('video_type')!='upload from system' and len(url)==0:
            bvl=True
            messages.add_message(request,messages.ERROR,'url field cannot be empty')
        if request.POST.get('video_type')=='upload from system' and play==None:
            bvl=True
            messages.add_message(request,messages.ERROR,'filename cannot be empty')
        if img==None:
            bvl=True
            messages.add_message(request,messages.ERROR,'add a valid thumbtail')
        if bvl:
            return redirect('new_video')

        video.category=request.POST.get('video_category')
        video.filename=play
        video.thumbtail=img
        video.link=request.POST.get('video_link')
        video.subtitle=request.POST.get('video_subtitle')
        if request.POST.get('video_premium'):
            video.premium=True
        else:
            video.premium=False
        video.upload_date=timezone.datetime.now()
        video.save()
        return HttpResponseRedirect('video/{}'.format(str(video.id)))

    return render(request,'products/new_video.html')
