from django import forms
from .models import  *

class Add_Photo(forms.ModelForm):
    class Meta:
        model=Photos
        fields=["UserID","image"]

    labels={
        "UserID":"UserID",
        "image":"image",
    }

    