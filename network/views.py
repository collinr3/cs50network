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


def index(request):
    # determine if the user is 'AnonymousUser', or a registered user
    view_intro = False
    try:
        # If a registered user, redirect to the posts view.
        if User.objects.get(id=request.user.id):
            return HttpResponseRedirect(reverse("posts"))
    except User.DoesNotExist:
        # If the user is not registered, then we will display some intro blurb
        view_intro = True
    # Also limit posts for Index page, purely a taster for unregistered users.
    posts = Post.objects.all().order_by('-id')[:3]
    # And finally, Grey out the like icons
    opinion = 'U'
    post_list = []
    for post in posts:
        post_list.append((post, opinion))
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
    """ Returns a list of Posts, either 'all posts' or the posts relating to a supplied userid (uid)
        Also detects if an author submits a new Post, and if so, processes that.
    """

    # Evaluate whether the user has submitted a new Post and if so, save it before returning the list of Posts
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

    # There may be a userid (uid) parameter passed with the GET, so look for it.
    user_id = request.GET.get('uid', '')
    # If there is one, then limit the posts to that userid.
    if user_id:
        person = User.objects.get(id=user_id)
        posts = Post.objects.filter(author=user_id).order_by('-created')
        follower_count = _followers(person)
        following_count = _following(person)
        if person == request.user:
            follow_option = None
        else:
            follow_option = _get_follow_option(person, request.user)

    else:
        # Otherwise get all posts.
        posts = Post.objects.all().order_by('-created')

    # Now annotate the posts with the like option, based on the user.
    annotated_post_list = _annotate_post_opinions(posts, request.user)

    # Now call the Django pagination facility helper function to figure out which posts to show.
    post_list = _paginate(request, annotated_post_list)

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
    """ Returns the posts for all of the authors that the user is following.
    """
    user_id = request.user.id
    authors = Follower.objects.filter(follower=user_id)
    posts = Post.objects.filter(author__in=authors.values_list('following_id', flat=True)).order_by('-created')
    annotated_post_list = _annotate_post_opinions(posts, request.user)

    # Now call the Django pagination facility helper function to figure out which posts to show.
    post_list = _paginate(request, annotated_post_list)

    follower_count = _followers(request.user)
    following_count = _following(request.user)

    content = {
        'post_list': post_list,
        'followers': follower_count,
        'following': following_count
    }
    return render(request, "network/index.html", content)


@login_required(login_url='/login')
def like(request):
    """ Evaluate a Like/Unlike request from a User, for a specified post.
        Checks that the user is not liking their own posts.
        Toggles the like status for the Post.
        Updates the like count for the Post.
        Provides a JSON response that can be consumed by the client e.g. as part of a Fetch()
    """
    user = request.user
    post_id = request.GET.get('id', '')
    post = Post.objects.get(id=post_id)
    if post.author != user:
        try:
            # Check to see if there is a record of the user previously liking the post.
            # If there is, update that record, and update the Like count as appropriate.
            feedback = Feedback.objects.get(post=post.id, reader=user)
            if feedback.opinion == 'L':
                feedback.opinion = 'U'
                # Use a Django F() expression to perform an operation directly on the database.
                post.like_count = F('like_count') - 1
            else:
                feedback.opinion = 'L'
                # Use a Django F() expression to perform an operation directly on the database.
                post.like_count = F('like_count') + 1
            feedback.save()
            post.save()
        # If there is no previous record, create a new one and update the like count as appropriate.
        except Feedback.DoesNotExist:
            # Add the like to the post
            feedback = Feedback(post=post, reader=user, opinion='L')
            feedback.save()
            # Use a Django F() expression to perform an operation directly on the database.
            post.like_count = F('like_count') + 1
            post.save()
        opinion = feedback.opinion
    else:
        # If User attempts to Like their own post, returns the 'Unliked' opinion
        opinion = 'U'
    # Now ensure that we have the post 'as stored', by refreshing from the database.
    post.refresh_from_db()

    follower_count = _followers(post.author)
    following_count = _following(user)

    content = {
        'post_id': post.id,
        'opinion': opinion,
        'followers': follower_count,
        'following': following_count,
        'likes': post.like_count,
    }
    return JsonResponse(content)


@login_required(login_url='/login')
def follow(request):
    """ Enables a User to 'Follow' an author,
        thereby making it easy for the user to see the latest posts from
        followed authors.
        The user can also unfollow an Author
    """

    # Determine the User
    user = request.user
    # Determine the author that the request relates to.
    username = request.GET.get('uname', '')
    author = User.objects.get(username=username)

    # Only update Follow Status if a 'Post', and the author is not the user.
    if request.method == 'POST' and user != author:
        # Check current follow option for this user relating to this author..
        follow_option = _get_follow_option(author, user)
        # If the returned Follow option is 'Follow', then add the user as a follower
        if follow_option == 'Follow':
            follower = Follower(
                follower=user,
                following=author,
            )
            follower.save()
        else:
            # If the follow option is to 'Unfollow' then attempt to delete the Follower record.
            try:
                Follower.objects.get(following=author, follower=user).delete()
            except Follower.DoesNotExist:
                # In the unlikely scenario of No follower match found, then nothing to delete.
                pass
    else:
        # If the user = author, then do nothing regarding Following.
        pass
    # Finally, redirect to the posts view so that the posts for the given author are displayed.
    url = f'/posts?uid={author.id}'
    response = redirect(url)
    return response


@login_required(login_url='/login')
def update(request):
    """ Updates a post if the user is the author.
    """
    user = request.user
    if request.method == 'POST':
        body = json.loads(request.body)
        post_id = body['id']
        try:
            post = Post.objects.get(id=post_id)
            if post.author == user:
                post.text = body['text']
                post.save()
                # User is the Author and Post exists.
                return HttpResponse(status=200)
            else:
                # Post is found, User is not the Author.
                return HttpResponse(status=404)
        except Post.DoesNotExist:
            # Post is not found.
            return HttpResponse(status=404)
    else:
        # Method is not POST, theredfore is not an Authorized method.
        return HttpResponse(status=403)


# Internal Helper functions
def _followers(author):
    # Returns the number of Followers for a given Author.
    follower_count = Follower.objects.filter(following=author).count()
    return follower_count


def _following(user):
    # Returns the number of Authors that the given user is following.
    following_count = Follower.objects.filter(follower=user).count()
    return following_count


def _annotate_post_opinions(posts, user):
    # Annotate posts with Like/Unlike options
    post_list = []
    for post in posts:
        try:
            post_liked = Feedback.objects.get(post=post.id, reader=user, opinion='L')
            opinion = post_liked.opinion
        except Feedback.DoesNotExist:
            opinion = 'U'
        post_list.append((post, opinion))
    return post_list


def _get_follow_option(person, user):
    # Advises whether an Author can be Followed, or Unfollowed
    # as determined by the the existence, or not of a Follower record.
    try:
        Follower.objects.get(following=person, follower=user)
        follow_option = 'Unfollow'
    except Follower.DoesNotExist:
        follow_option = 'Follow'
    return follow_option


def _paginate(request, annotated_post_list):
    # The Django paginate feature.
    page = request.GET.get('page', 1)
    paginator = Paginator(annotated_post_list, 10)  # 10 Posts per page
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return post_list
