from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate,login
from django.db.models import Q
from django.shortcuts import get_object_or_404
from . models import Contactus,Post,Profile,Like,Comment,Follow,Notification

# Create your views here.
def index(request):
    posts = Post.objects.select_related('author').all().order_by('-create_date')

    query = request.GET.get('q','')
    if query:
        posts = Post.objects.filter(title__icontains=query)
    else:
        posts = Post.objects.all().order_by('-create_date')

    unread_notifications = 0
    profile = None
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
        unread_notifications = request.user.notifications.filter(is_read=False).count()

        for post in posts:
            post.is_liked = post.likes.filter(user=request.user).exists()

    context = {
        "posts": posts,
        "query": query,
        "profile":profile,
        'unread_notifications': unread_notifications,
    }

    if request.user.is_authenticated:
        return render(request, "index.html", context)
    else:
        return render(request, "first.html")


@login_required
def search_posts(request):
    query = request.GET.get('q')
    posts = Post.objects.all()

    if query:
        posts = posts.filter(
            Q(title__icontains=query)
        ).order_by('-create_date')

    context = {
        'posts': posts,
        'query': query,
    }
    return render(request, 'search.html', context)

def first(request):
    return render(request,"../templates/first.html")


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    my_profile, _ = Profile.objects.get_or_create(user=request.user)

    comments = post.comments.all().order_by('-created_at')


    unread_notifications = 0
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.likes.filter(user=request.user).exists()
        unread_notifications = request.user.notifications.filter(is_read=False).count()

    author_followers = Follow.objects.filter(following=post.author)
    author_following = Follow.objects.filter(follower=post.author)

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=post.author).exists()

    context = {
        "post": post,
        "my_profile": my_profile,
        "modify_date": post.modify_date,
        "user_liked": user_liked,
        "comments": comments,
        "follows": author_followers.count(),
        "following": author_following.count(),
        "is_following": is_following,
        "unread_notifications":unread_notifications
    }

    return render(request, "post_detail.html", context)


@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    posts = request.user.posts.all().order_by('-create_date')


    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).count()

    my_profile = profile  

    followers = Follow.objects.filter(following=request.user)
    following = Follow.objects.filter(follower=request.user)

    query = request.GET.get('q','')
    if query:
        posts = request.user.posts.filter(title__icontains=query).order_by('-create_date')
    else:
        posts = request.user.posts.all().order_by('-create_date')

    if request.method == 'POST':

        for post in posts:
            post.is_liked = post.likes.filter(user=request.user).exists()


        if 'remove_image' in request.POST:
            profile.image.delete(save=True)

        if request.FILES.get('image'):
            profile.image = request.FILES['image']

        if request.FILES.get('cover_img'):
            profile.cover_img = request.FILES['cover_img']

        profile.save()
        return redirect('profile')

    context = {
        "profile": profile,         
        "posts": posts,
        "my_profile": my_profile,   
        "user_profile": request.user, 
        "followers": followers,
        "following": following,
        "followers_count": followers.count(),
        "following_count": following.count(),
        "query":query,
        "unread_notifications":unread_notifications
       
    }
    return render(request, '../templates/profile.html', context)


@login_required
def user_profile(request, user_id):
    user = User.objects.filter(pk=user_id).first()
    profile, created = Profile.objects.get_or_create(user=user)
    posts = user.posts.all().order_by('-create_date')


    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).count()

    my_profile, _ = Profile.objects.get_or_create(user=request.user) 

    query = request.GET.get('q','')
    if query:
        posts = user.posts.filter(title__icontains=query).order_by('-create_date')
    else:
        posts = user.posts.all().order_by('-create_date')

    for post in posts:
        post.is_liked = post.likes.filter(user=request.user).exists()

    followers = Follow.objects.filter(following=user)
    following = Follow.objects.filter(follower=user)
    is_following = False
    if user != request.user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    context = {
        "profile": profile,        
        "posts": posts,
        "user_profile": user,      
        "my_profile": my_profile,
        "followers": followers,
        "following": following,
        "followers_count": followers.count(),
        "following_count": following.count(),
        "is_following": is_following, 
        "query":query,
        "unread_notifications":unread_notifications

    }
    return render(request, '../templates/user_profile.html', context)

@login_required
def toggle_follow(request, user_id):
    target_user = User.objects.get(id=user_id)

    if target_user == request.user:
    
        return redirect('profile')

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )

    if not created:
        follow.delete()
    
    else:
        Notification.objects.create(
            sender=request.user,
            recipient=target_user,
            notification_type='follow'
        )

    return redirect('user_profile', user_id=user_id)

@login_required
def write(request):
    if not request.user.groups.filter(name='Member').exists():
        return redirect('membership')

    if request.method == "POST":
        title = request.POST.get("title")
        subtitle = request.POST.get("subtitle")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        Post.objects.create(
            author=request.user,
            title=title,
            subtitle=subtitle,
            description=description,
            image=image,
        )

        return redirect('index')

    return render(request, '../templates/write.html')
 
@login_required
def add_comment(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
            if request.user != post.author:
                Notification.objects.create(
                    sender=request.user,
                    recipient=post.author,
                    notification_type='comment',
                    post=post
                )
    return redirect('post_detail', pk=pk)

@login_required
def notifications(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    notifications = request.user.notifications.all().order_by('-timestamp')

    request.user.notifications.filter(is_read=False).update(is_read=True)

    for note in notifications:
        note.is_read = True
        note.save()

    return render(request, '../templates/notifications.html', {
        'notifications': notifications,
        'profile': profile
    })


@login_required
def toggle_like(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
        else:
            if request.user != post.author:
                Notification.objects.create(
                    sender=request.user,
                    recipient=post.author,
                    notification_type='like',
                    post=post
                )
    return redirect(request.META.get('HTTP_REFERER', 'index'))
    

def about(request):

    query = request.GET.get('q','')
    if query:
        posts = Post.objects.filter(title__icontains=query)
    else:
        posts = Post.objects.all().order_by('-create_date')

    context={
        "query":query,
        "post":posts,
    }

    return render(request,'../templates/about.html',context)

def blog(request):
     return render(request,'../templates.blog.html')

@login_required
def payment(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user = request.user
        viewer_group = Group.objects.get(name='Viewer')
        member_group = Group.objects.get(name='Member')

        user.groups.remove(viewer_group)
        user.groups.add(member_group)

        profile.is_member = True
        profile.save()

        return redirect('index')

    context = {
        "profile": profile
    }
    return render(request, '../templates/payment.html', context)


def help(request):

    unread_notifications = 0
    if request.user.is_authenticated:
        profile, created = Profile.objects.get_or_create(user=request.user)
        unread_notifications = request.user.notifications.filter(is_read=False).count()


    query = request.GET.get('q','')
    if query:
        posts = Post.objects.filter(title__icontains=query)
    else:
        posts = Post.objects.all().order_by('-create_date')

    if request.method == "POST":
              name = request.POST.get("name")
              email = request.POST.get("email")
              message = request.POST.get("message")
              sql = Contactus(name=name,email=email,message=message)
              sql.save()
              return redirect ('index')
    context={
        "posts":posts,
        "profile":profile,
        "unread_notifications":unread_notifications
    }
       
    return render(request,'../templates/help.html',context)

@login_required
def membership(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    context = {
        "profile": profile
    }
    return render(request, '../templates/membership.html', context)


def login_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")


        if User.objects.filter(username=name).exists():
            return render(request, '../templates/login_register.html', {
                "error": "Username already taken. Please choose another one."
            })

        if User.objects.filter(email=email).exists():
            return render(request, '../templates/login_register.html', {
                "error": "Email already registered. Please log in."
            })


        user = User.objects.create_user(username=name, email=email, password=password)

        viewer_group = Group.objects.get(name='Viewer')
        user.groups.add(viewer_group)

        login(request, user) 

        return redirect('index')

    return render(request, '../templates/login_register.html')


def login_view(request):
      
      if request.method == "POST": 
        
       username = request.POST.get('email')
       password = request.POST.get('password')

       try:
            user = User.objects.get(email=username)
       except User.DoesNotExist:
            return render(request, '../templates/login_register.html')

       user = authenticate(request,username=user.username, password=password)

       
       if user is not None:
             login(request,user)
             return redirect ('index')
       else:
             return render (request,'../templates/login_register.html')
       
      return render (request,'templates/login_register.html')


def logout_view(request):
    logout(request)
    return redirect('first')