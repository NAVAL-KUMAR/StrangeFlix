from django.views.generic.base import View, HttpResponseRedirect, HttpResponse
from .forms import  NewVideoForm, CommentForm
from .models import Video, Comment, Like
from django.core.files.storage import FileSystemStorage
import os
from django.shortcuts import render, redirect
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
from django.http import HttpResponse,JsonResponse
from django.conf import settings
import threading
from django.core.exceptions import ObjectDoesNotExist


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
        most_recent_videos = Video.objects.order_by('-datetime')[:15]
        return render(request, self.template_name, {'menu_active_item': 'home', 'most_recent_videos': most_recent_videos})




#View to view Video

class VideoView(View):
    template_name = 'products/video.html'

    def get(self, request, id):
        #fetch video from DB by ID
        video_by_id = Video.objects.get(id=id)
        #BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        video_by_id.path = video_by_id.path
        video_by_id.views = video_by_id.views + 1
        video_by_id.save()
        context = {'video':video_by_id}

        if request.user.is_authenticated:
            print('user signed in')
            comment_form = CommentForm()
            context['form'] = comment_form



        comments = Comment.objects.filter(video__id=id).order_by('-datetime')[:5]
        print(comments)
        context['comments'] = comments
        most_recent_videos = Video.objects.order_by('-datetime')[:8]
        context['most_recent_videos'] = most_recent_videos
        try:
            go = Like.objects.get(video__id=id, user=request.user)
        except ObjectDoesNotExist:
            go = None
            video = Video.objects.get(id=id)
            liked_now = Like(like=0, user=request.user, video=video)
            liked_now.save()
            go = Like.objects.get(video__id=id, user=request.user)
        context['like_dislike'] = go
        return render(request, self.template_name, context)


def comment(request):
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text',False)
        video_id = request.POST.get('video_id',False)
        print(comment_text)
        print(video_id)
        video = Video.objects.get(id = video_id)
        new_comment = Comment(text = comment_text, user = request.user , video = video)
        new_comment.save()
        comments = Comment.objects.filter(video_id=video_id).order_by('-datetime')[:5]
        return JsonResponse({'comments': list(comments.values())})


def liked(request):
    if request.method == 'GET':
        video_id = request.GET.get('video_id', False)
        video = Video.objects.get(id = video_id)
        go = Like.objects.get(video=video,user=request.user)
        if go.like == 1:
            go.like = 0
            video.likes = video.likes - 1;
        else:
            if go.like == -1:
                video.dislikes = video.dislikes - 1;
            go.like = 1
            video.likes = video.likes + 1;
        go.save()
        video.save()
        context = {'like': go.like}
        context['total_like'] = video.likes
        context['total_dislike'] = video.dislikes
        return JsonResponse(context)


def disliked(request):
    if request.method == 'GET':
        video_id = request.GET.get('video_id', False)
        video = Video.objects.get(id=video_id)
        go = Like.objects.get(video=video, user=request.user)
        if go.like == -1:
            go.like = 0
            video.dislikes = video.dislikes - 1;
        else:
            if go.like == 1:
                video.likes = video.likes - 1;
            go.like = -1
            video.dislikes = video.dislikes + 1;
        go.save()
        video.save()
        context =   {'dislike': go.like}
        context['total_dislike'] = video.dislikes
        context['total_like'] = video.likes
        return JsonResponse(context)



def comment_list(request):
    video_id = request.POST.get('video_id', False)
    comments = Comment.objects.filter(video_id=2).order_by('-datetime')[:5]
    return JsonResponse({'comments': list(comments.values())})



#comment under video in video

# class CommentView(View):
#     template_name = 'products/comment.html'
#
#     def post(self, request):

        # pass filled out HTML-Form from View to CommentForm()
        # form = CommentForm(request.POST)
        # if form.is_valid():
        #     # create a Comment DB Entry
        #     text = form.cleaned_data['text']
        #     video_id = request.POST['video']
        #     video = Video.objects.get(id=video_id)
        #
        #     new_comment = Comment(text=text, user=request.user, video=video)
        #     new_comment.save()
        #     return HttpResponseRedirect('video/{}'.format(str(video_id)))
        # return HttpResponse('This is Register view. POST Request.')

#view to upload video

class NewVideo(View):
    template_name = 'products/new_video.html'

    def get(self, request):
        if request.user.is_authenticated == False:
            #return HttpResponse('You have to be logged in, in order to upload a video.')
            return HttpResponseRedirect('/register')

        form = NewVideoForm()
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        # pass filled out HTML-Form from View to NewVideoForm()
        form = NewVideoForm(request.POST, request.FILES)

        if form.is_valid():
            # create a new Video Entry
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            file = form.cleaned_data['file']
            fileI = form.cleaned_data['fileI']
            #random_char = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            path = 'products/static/'+file.name
            pathI = 'products/static/'+fileI.name

            fs = FileSystemStorage(location = os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            fileIname = fs.save(pathI,fileI)
            filename = fs.save(path, file)
            file_url = fs.url(filename)

            print(fs)
            print(filename)
            print(file_url)
            print(path)
            print(fileIname)

            new_video = Video(title=title,
                            description=description,
                            user=request.user,
                            path=file.name,imName=fileI.name)
            new_video.save()

            # redirect to detail view template of a Video
            return HttpResponseRedirect('video/{}'.format(new_video.id))
        else:
            return HttpResponse('Your form is not valid. Go back and try again.')
