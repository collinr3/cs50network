from django import forms


class PostForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Write something!'
        })
    )


