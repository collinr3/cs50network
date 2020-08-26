# CS50: Web Programming with Python and JavaScript - Project 4 2020: Network

Project 4: implements a Twitter-like social network website for making posts and following users.

## Getting Started

### Python and Django

First, make sure you install a copy of Python. For this project, you should be using Python version 3.6 or higher.
You’ll also need to install pip.

### The Application:

Download the project distribution directory from either: -
  `https://github.com/collinr3/cs50network.git`
  
  or
  `https://github.com/me50/collinr3.git/` on branch `web50/projects/2020/x/network`

In a terminal window, navigate into your project directory.

Run `pip3 install -r requirements.txt` in your terminal window to make sure that all of the necessary Python packages (Django, for instance) are installed.

### API

Currently, there is no published API for the application.

### Running the Application

Run `python manage.py runserver` to start up your Django application.
If you navigate to the URL provided by Django, you should see the Network Home Page.

## Initial Usage

### Simple Use Case
1. On the Network landing page, note the Welcome, option to Login, if already registered, or the option to Sign Up. Note also that a small number of Posts (Max 3) may be visible if previously registered users have submitted posts.
2. Choose `Sign Up` and provide a minimum of `Username` and `Password`. Click `Register`.
3. If successfully registered, Note that the Network landing page now provides the option to `Post something` and also shows the latest posts (Max 10 per page), with a pagination option at the bottom, where more that 10 posts have been posted.
4. From the menu, click on `My Posts` , `All Posts` and `Following` and note that the option to `Post something` is available on each page.
5. Whilst on `Following` Submit a Post - note that  the display reverts to a display of `All Posts`. Note also that your new post appears at the top of the Latest Posts list. The same behaviour occurs on `My Posts` and, logically,  `All Posts`.
6. From the menu, click on `All Posts` and note that all posts from all users are displayed with the most recent posts first. Note that for posts with a large amount of text, a `More` option is displayed.
7. Click on the `username` for a post. Note that that the Profile for that username is shown. Note the `Followed by` and `Following`  numbers. Note also that the posts for that username are displayed, with the most recent first.
8. Click the `Follow` button. Note that the `Followed by` number increases by 1, and that the button now shows `Unfollow`.
9. From the menu, click on ‘Following`. Note the posts for the username you are now following, are displayed.
10. Beneath each post, note the `heart symbol` this indicates whether you have liked a post, or not. Click the symbol to `Like` or `Unlike` a post. Note that the colour changes and the number of Likes updates appropriately. Note that the entire page  does not reload when doing this.
11. From the menu, click `My Posts`. Note the `Followed by` and `Following`  numbers for you. Note that there is no option to `Follow` yourself. Note also that you cannot `Like` your own posts.
12. Note the `edit symbol` beneath each of your posts. Click the `symbol` beneath one of the posts. Note that the post is now editable, with a `Save` and `Cancel` option. This `Editor` is a React Component and it utilise the Django csrf token to validate the edit submission. The server also checks that the username that submits the edit is also the author of the post. 
13. Without `Saving` or `Cancelling` the edit, click the `edit` icon of another post. Note the alert that advises `Already editing`
14. In the editor, make a change and `Save`. Note that the edit is saved to your post, and the `Editor` is closed.
15. From the menu, click `Logout`. Note that you are now logged out and that the `Following` menu option is not visible. Note also that the Network landing page is now re-displayed with 3 of the latest posts.
16. From the menu, click `All Posts`, note that you are re-directed top the `Login` page.
17. End.

### User interface

Generally, the user interface is generated from `Django templates`, and styled with `CSS`.

`Javascript` is used to: -
* set the `like` icon colour for each post
* detect a `like` event so that the status can be updated asynchronously
* add a `More` option to posts with large amounts of text. (Note the `text length` is not limited in Network, unlike Twitter).
* detect an edit post event and invoke a React editor.
    
`JSX` is used to define the React Editor components and manage the update of a post. 

### Testing

Currently, there are no test scripts developed for the application.
The application does include test users `user1` `user2` `user3` and `admin` and also some test posts.
Note: Passwords are the same as username.
To start with a clean database, simply delete `db.sqlite3` and re-run migrations `python manage.py migrate`


## Author

* **Robert Collins** - *inspired by tuition from* - [the CS50 team at Harvard](https://cs50.harvard.edu/web/)