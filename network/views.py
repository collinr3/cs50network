import json
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import F
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User, Post, Follower, Feedback

#@login_required(login_url='/login')
def index(request):
    posts = Post.objects.all().order_by('-id')[:3]
    opinion = 'U'
    post_list = []
    for post in posts:
        post_list.append((post, opinion))
    try:
        if User.objects.get(id=request.user.id):
            view_intro = False
    except User.DoesNotExist:
        view_intro = True
    content = {
        'intro': view_intro,
        'post_list': post_list,
    }
    return render(request, "network/index.html", content)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("posts"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url='/login')
def get_posts(request):
    user_id = request.GET.get('uid', '')
    if request.method == 'POST':
        post = Post(
            author=request.user,
            text=request.POST.get('text', ''),
            created=datetime.now()
        )
        post.save()

    follower_count = None
    following_count = None
    person = None
    follow_option = None

    if user_id:
        person = User.objects.get(id=user_id)
        print(f'User {user_id} person: {person}')
        posts = Post.objects.filter(author=user_id).order_by('-created')
        follower_count = _followers(person)
        following_count = _following(person)
        if person == request.user:
            follow_option = None
        else:
            follow_option = _get_follow_option(person, request.user)

    else:
        posts = Post.objects.all().order_by('-created')

    full_post_list = _get_post_list(posts, request.user)

    page = request.GET.get('page', 1)
    paginator = Paginator(full_post_list, 3)
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)

    content = {
        'person': person,
        'post_list': post_list,
        'followers': follower_count,
        'following': following_count,
        'follow_option': follow_option
    }
    return render(request, "network/index.html", content)


@login_required(login_url='/login')
def get_following(request):
    #user_id = request.GET.get('uid', '')
    user_id = request.user.id
    #(user_id)
    authors = Follower.objects.filter(follower=user_id)
    #print(f'following {authors}')
    posts = Post.objects.filter(author__in=authors.values_list('following_id', flat=True)).order_by('-created')
    #print(posts)
    full_post_list = _get_post_list(posts, request.user)

    page = request.GET.get('page', 1)
    paginator = Paginator(full_post_list, 3)
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)

    follower_count = _followers(request.user)
    following_count = _following(request.user)

    content = {
        'post_list': post_list,
        'followers': follower_count,
        'following': following_count
    }
    #print(content)
    return render(request, "network/index.html", content)


@login_required(login_url='/login')
def like(request):
    user = request.user
    post_id = request.GET.get('id', '')
    #print(type(post_id))
    detail = Post.objects.get(id=post_id)
    if detail.author != user:
        try:
            feedback = Feedback.objects.get(post=detail.id, reader=user)
            #print(f'Already feedback of this type, so Toggle {like}')
            if feedback.opinion == 'L':
                feedback.opinion = 'U'
                detail.like_count = F('like_count') - 1
            else:
                feedback.opinion = 'L'
                detail.like_count = F('like_count') + 1
            feedback.save()
            detail.save()
        except Feedback.DoesNotExist:
            # Add the like to the post
            feedback = Feedback(post=detail, reader=user, opinion='L')
            feedback.save()
            detail.like_count = F('like_count') + 1
            detail.save()
        opinion = feedback.opinion
    else:
        opinion = 'U'
    detail.refresh_from_db()
    #print(f'dc {detail.like_count}')
    posts = [detail]
    post_list = _get_post_list(posts, user)

    follower_count = _followers(detail.author)
    following_count = _following(user)

    content = {
        'post_id': detail.id,
        'opinion': opinion,
        'followers': follower_count,
        'following': following_count,
        'likes': detail.like_count,
    }
    #print(content)
    #return render(request, "network/index.html", content)
    return JsonResponse(content)

@login_required(login_url='/login')
def follow(request):
    user = request.user
    username = request.GET.get('uname', '')
    author = User.objects.get(username=username)
    if request.method == 'POST' and user != author:
        # Check current follow status.
        follow_option = _get_follow_option(author, user)
        if follow_option == 'Follow':
            follower = Follower(
                follower=user,
                following=author,
            )
            follower.save()
        else:
            try:
                Follower.objects.get(following=author, follower=user).delete()
            except Follower.DoesNotExist:
                # No follower match found, so nothing to delete.
                #TODO Consider raising a 404 exception here, if I can decide what to do with it in the  UI.
                pass
    else:
        pass
    url = f'/posts?uid={author.id}'
    response = redirect(url)
    return response


@login_required(login_url='/login')
def update(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        post_id = body['id']
        post = Post.objects.get(id=post_id)
        post.text = body['text']
        post.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

def _followers(author):
    follower_count = Follower.objects.filter(following=author).count()
    #print(f'Followers {follower_count}')
    return follower_count

def _following(user):
    following_count = Follower.objects.filter(follower=user).count()
    return following_count

def _get_post_list(posts, user):
    # Annotate posts with Like/Unlike option
    post_list = []
    for post in posts:
        try:
            like = Feedback.objects.get(post=post.id, reader=user, opinion='L')
            #print(f'Already feedback of this type')
            opinion = like.opinion
        except Feedback.DoesNotExist:
            opinion = 'U'
        post_list.append((post, opinion))
    #print(post_list)
    return post_list


def _get_follow_option(person, user):
    try:
        Follower.objects.get(following=person, follower=user)
        follow_option = 'Unfollow'
    except:
        follow_option = 'Follow'
    return follow_option


