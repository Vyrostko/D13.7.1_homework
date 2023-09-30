from django.forms import ModelForm
from .models import *

class AdsForm(ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'text', 'adCategory', 'image', 'video', 'file']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']