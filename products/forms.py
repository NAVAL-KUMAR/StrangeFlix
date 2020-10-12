from django import forms


#this function is not in use currently
#this is already implemented by sonu in account folder
class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    password = forms.CharField(label='Password', max_length=20)


#this function is not in use currently
#this is already implemented by sonu in account folder
class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    password = forms.CharField(label='Password', max_length=20)
    email = forms.CharField(label='Email', max_length=20)

class CommentForm(forms.Form):
    text = forms.CharField(label='Add Comment :', max_length=300)
    
class NewVideoForm(forms.Form):
    title = forms.CharField(label='Title', max_length=20)
    description = forms.CharField(label='Description', max_length=300)
    file = forms.FileField(label='Add Video')
    fileI = forms.FileField(label='Add Image Thumbnail')
