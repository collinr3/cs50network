from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms


class User(AbstractUser):
    # Add Follower IDs to User

    def __str__(self):
        return f'{self.username}'

# Posts Class
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authors')
    text = models.TextField()
    like_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def published(self):
        return self.created.strftime('%B %d %Y')

    def __str__(self):
        return f'{self.author}: {self.published()}'

class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follows')

    def __str__(self):
        return f'follower: {self.follower} following: {self.following}'

class Feedback(models.Model):
    class Meta:
        verbose_name_plural = 'Feedback'
    LIKE = 'L'
    UNLIKE = 'U'

    OPINION_CHOICES = [
        (LIKE, 'Like'),
        (UNLIKE, 'Unlike'),
    ]
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='readers')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='posts')
    opinion = models.CharField(max_length=1, choices=OPINION_CHOICES)

    def __str__(self):
        return f'reader: {self.reader} post ID: {self.post.id} opinion is {self.opinion}'

