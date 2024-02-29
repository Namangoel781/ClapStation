from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from .models import *
from .forms import *
import re



# SIGNUP

def custom_login(request):
    if request.method == 'POST':
        try:
            contact = request.POST['contact']
            password = request.POST['password']

        

            # Authenticate user based on contact (email or phone number)
            user = authenticate(request=request, contact=contact, password=password)

            if user is not None:
                # If user is authenticated, log them in and redirect to a specific page
                login(request, user)
                return redirect('/')  # Replace '/' with your desired URL
            else:
                # If authentication fails, handle it (e.g., show an error message)
                error_message = "Invalid credentials. Please try again."
                return render(request, 'login.html', {'error_message': error_message})

        except KeyError as e:
            # Handle the case where 'contact' or 'password' is missing in the POST data
            error_message = f"Missing key in POST data: {str(e)}"
            return render(request, 'login.html', {'error_message': error_message})

        except Exception as e:
            # Handle other unexpected exceptions
            error_message = f"An error occurred: {str(e)}"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')


def validate_email_format(email):
    # Basic email validation using regular expression
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_regex, email):
        raise ValidationError('Invalid email address.')

    # Additional checks for email format
    username, domain = email.split('@')
    if not (username.isalnum() and domain.count('.') == 1 and domain.index('.') > 0):
        raise ValidationError('Invalid email format.')

# SIGNIN

def signin(request):
    if request.method == "POST":
        try:
            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            password = request.POST.get('password')
            contact = request.POST.get('contact').lower()  # Convert email to lowercase
            user_type = request.POST.get('usertype')
            birthday_day = request.POST.get('birthday_day')
            birthday_month = request.POST.get('birthday_month')
            birthday_year = request.POST.get('birthday_year')
            gender = request.POST.get('gender')
            birthdate = f"{birthday_year}-{birthday_month}-{birthday_day}"

            # Validate the contact field for phone number or email
            if '@' in contact:
                # Email validation
                validate_email_format(contact)
            else:
                # Phone number validation
                if not (contact.isdigit() and len(contact) == 10):
                    raise ValidationError('Invalid phone number. Please enter a 10-digit number.')

            # Validate the password
            if (
                len(password) < 8 or
                not any(char.isdigit() for char in password) or
                not any(char.isupper() for char in password) or
                not any(char.islower() for char in password) or
                not any(char in r'!@#$%^&*()_+{}[]|;:,.<>?/' for char in password)
            ):
                raise ValidationError({'password': 'Invalid password. It should be at least 8 characters long '
                                      'with one uppercase letter, one lowercase letter, one digit, and one special character.'})
            
            # Create a CustomUser instance
            user = CustomUser(
                first_name=first_name,
                last_name=last_name,
                password=make_password(password),
                contact=contact,
                designation=user_type,
                date_of_birth=birthdate,
                gender=gender,
                profile='add a profile photo',
                address='add the address'
            )

            # Save the user to the database
            user.full_clean()  # Run full_clean to validate other model fields
            user.save()

            return redirect("/")

        except ValidationError as e:
            error_message = str(e)
            return render(request, "signup.html", {'error_message': error_message})

        except Exception as e:
            # Handle other unexpected exceptions
            error_message = f"An error occurred: {str(e)}"
            return render(request, "signup.html", {'error_message': error_message})

    return render(request, "signup.html")

#LOGOUT

@login_required(login_url="/login")
def custom_logout(request):
    try:
        if request.user.is_authenticated:
            logout(request)
    except Exception as e:
        # Handle unexpected exceptions during logout
        error_message = f"An error occurred during logout: {str(e)}"
        return render(request, "error_page.html", {'error_message': error_message})

    return redirect("/")



#INDEX PAGE
def starting_page(request):    
    
    try:
        events = Event.objects.all().order_by('-date')
    except Event.DoesNotExist:
        events = []
    
    try:
        post = posts.objects.all().order_by('-created_at')
        advertisement = advertisements.objects.all().order_by('-created_at')
    
    except posts.DoesNotExist:
        post = []
    except advertisements.DoesNotExist:
        advertisement = []    
    
    try:
        details = user_details.objects.latest("-created_at")
    except user_details.DoesNotExist:
        details = None

    try:
        liveVideos = LiveVideo.objects.all().order_by('-created_at')
    except LiveVideo.DoesNotExist:
        liveVideos = []

    if request.method == "POST":
        postContent = request.POST.get("post-content")
        postImg = request.FILES.get("post-image")

        try:
            # Ensure the user is authenticated before creating a post
            if request.user.is_authenticated:
                posts.objects.create(about=postContent, img=postImg, author=request.user)
                return redirect("/")
            else:
                # Handle the case where the user is not authenticated (e.g., redirect to a login page)
                return redirect("/") 
        except Exception as e:
            # Handle unexpected exceptions during post creation
            error_message = f"An unexpected error occurred while creating a post: {str(e)}"
            return render(request, 'error_page.html', {'error_message': error_message})
    
    try:
        p = Paginator(post, 4)
        page = request.GET.get('page')
        content = p.get_page(page)
        nums = "a" * content.paginator.num_pages
    except Exception as e:
        print(f"Error during pagination: {str(e)}")
        content = []
        nums = ""
    error_message = request.GET.get('error', '')
    context = {
        "post": post,
        "advertisement": advertisement,
        "detail": details,
        "nums": nums,
        "content": content,
        'liveVideos': liveVideos,
        'events': events,
        'error_message': error_message
    }

    return render(request, 'index.html', context)

# LIKE DISLIKE POST

@login_required(login_url='login')
def toggle_like_dislike(request, post_id):
    post = posts.objects.get(pk=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)

    return redirect('starting-page')

#COMMENT POST

@login_required(login_url='login')
def add_comment(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(posts, pk=post_id)
        text = request.POST.get('post-comment')

        if text:
            Comment.objects.create(post=post, user=request.user, text=text)

    return redirect('starting-page')

#RATE POST

@login_required(login_url="/login")
def submit_rating(request, post_id, rating):
    post = get_object_or_404(posts, id=post_id)
    post.rate = rating
    post.save()
    return JsonResponse({'message': 'Rating submitted successfully'})

#DELETE POST

@login_required(login_url='login')
def postdelete(request,id):
    post = posts.objects.get(pk=id)
    post.delete()
    return redirect("starting-page")

# ADD LIVE VIDEO

@login_required(login_url='login')
def add_live_video(request):
    try:
        if request.method == "POST":
            liveUrl = request.POST.get("post-url")
            liveDescription = request.POST.get("post-description")

            # Validate URL
            if not validators.url(liveUrl):
                raise ValueError("Invalid URL format. You write first http://........")

            # Validate description length
            max_description_length = 50
            if len(liveDescription) > max_description_length:
                raise ValueError(f"Description should not exceed {max_description_length} characters")

            LiveVideo.objects.create(url=liveUrl, description=liveDescription, author=request.user)
            return redirect("/")
    except ValueError as ve:
        error_message = str(ve)
        return redirect("/?error=" + error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred while adding a live video: {str(e)}"
        return redirect("/?error=" + error_message)


# DELETE LIVE VIDEO

@login_required(login_url='login')
def livevideodelete(request, id):
    live_video = LiveVideo.objects.get(pk=id)
    live_video.delete()
    return redirect("starting-page")

# EVENT

@login_required(login_url='login')
def add_event(request):
    if request.method == 'POST':
        date = request.POST.get('eventDate')
        artist_name = request.POST.get('artistName')
        event_name = request.POST.get('eventName')
        event_photo = request.FILES.get('eventPhoto')
        Event.objects.create(date=date, artist_name=artist_name, event_name=event_name, event_photo=event_photo)
        return redirect("/")
    

@login_required(login_url='login')
def groups_page(request):
    return render(request, 'groups.html')

@login_required(login_url='login')
def bands_page(request):
    return render(request, 'bands.html')

@login_required(login_url='login')
def academies_page(request):
    return render(request, 'academies.html')

@login_required(login_url='login')
def events_page(request):
    return render(request, 'events.html')

@login_required(login_url='login')
def artists_page(request):
    return render(request, 'artists.html')

@login_required(login_url='login')
def about_page(request):
    return render(request, 'about-us.html')

#CONTACT PAGE

@login_required(login_url='login')
def contact_page(request):
    if request.method == "POST":
        First_N = request.POST['First_Name']
        emailid = request.POST['Email']
        message = request.POST['Message']
        
        contact_usobj = Contact_us(First_N=First_N, emailid=emailid, message=message)
        contact_usobj.save()
        
    return render(request, 'contact-us.html')

#PROFILE

@login_required(login_url='login')
def profile_page(request):    
    if request.method == "POST":
        postContent = request.POST.get("post-content")
        postImg = request.FILES.get("post-image")

        try:
            # Ensure the user is authenticated before creating a post
            if request.user.is_authenticated:
                posts.objects.create(about=postContent, img=postImg, author=request.user)
                return redirect("/profile")
            else:
                # Handle the case where the user is not authenticated (e.g., redirect to a login page)
                return redirect("/login") 
        except Exception as e:
            # Handle unexpected exceptions during post creation
            error_message = f"An unexpected error occurred while creating a post: {str(e)}"
            return render(request, 'error_page.html', {'error_message': error_message})
    

    ID=request.user.id
    current_user=CustomUser.objects.get(id=ID)
    friends=Friendship.objects.filter(UserID=ID)
    userfriends=[]
    for x in friends:
        userfriends.append(CustomUser.objects.get(contact=x.FriendID))

    my_posts=posts.objects.filter(author=ID)
    context={
        "current_user":{
            "name":current_user.first_name+" "+current_user.last_name,
            "designation":current_user.designation,
            "address":current_user.address,
            "profile":current_user.profile
        },
        "friends":userfriends,
        "my_posts":my_posts,
        "user_photos": Photos.objects.filter(UserID=ID).order_by('-timestamp'),
        "form":Add_Photo(),
        "posts":posts.objects.filter(author=ID).order_by('-created_at'),
        "liveVideos":LiveVideo.objects.filter(author=ID).order_by('-created_at')
    }
    return render(request, 'profile.html', context)

# # Add-Photo in Profile page
# def add_Photo(request):
 
    
#     if request.method == "POST":
#         profileImg = request.FILES.get("profile-image")

        
#             # Ensure the user is authenticated before creating a post
#         if request.user.is_authenticated:
#             Profile_posts.objects.create(image=profileImg, author=request.user)
#             return redirect("/profile")
#         else:
#                 # Handle the case where the user is not authenticated (e.g., redirect to a login page)
#             return redirect("/profile") 
#     profile_post = Profile_posts.objects.all().order_by('-created_at')  
        
#     context = {
#         "profile_post": profile_post,        
#         'error_message': error_message
#     }

#     return render(request, 'profile.html', context)

def add_Photo(request):
    if request.method == 'POST':
        image = request.FILES.get('profile-image')
        if image:
            # Save the image data to the database
            profile_post = Photos.objects.create(image=image, UserID=request.user)
            return redirect('/profile')  # Redirect to a success page or the same page

    # profile_post = Profile_posts.objects.all()
    # return render(request, 'profile.html', {'profile_post': profile_post})