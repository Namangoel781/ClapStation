from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from PIL import Image
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

# signup_model

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, contact, password=None, **extra_fields):
        if not contact:
            raise ValueError('The Contact field must be set')
        user = self.model(contact=contact, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, contact, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(contact, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('Male','Male'),
        ('Female','Female'),
        ('Other','Other'),
    )
    profile=models.ImageField(upload_to="profile/image",default="profile/image/home-1.png")
    address=models.CharField(max_length=50,default="Please edit your Profile address")
    contact = models.CharField(max_length=25, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES)
    timestamp=models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'contact'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'designation', 'date_of_birth', 'gender']

    def _str_(self):
        return self.contact
    
    
# other_models

def validate_image_dimensions(value):
    max_height = 360
    max_width = 640

    with Image.open(value) as img:
        width, height = img.size

    if width > max_width or height > max_height:
        raise ValidationError(f"Image dimensions must be at most {max_width}x{max_height} pixels.")



class posts(models.Model):
    img = models.ImageField(upload_to="posts/image", default="", help_text="ClapStation upload image | height: 360px | width: 640px", validators=[validate_image_dimensions])
    about = models.CharField(max_length=250, blank=True, null=True)
    author= models.ForeignKey(CustomUser,related_name='author', on_delete=models.CASCADE, default="")
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)
    rate = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    post = models.ForeignKey(posts, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class advertisements(models.Model):
    img = models.ImageField(upload_to="advertisement/image",default="")
    created_at = models.DateTimeField(auto_now_add = True )


class upComingEvents(models.Model):
    img = models.ImageField(upload_to="upcoming/image", default="")
    created_at = models.DateTimeField(auto_now_add = True )



class user_details(models.Model):
    img = models.ImageField(upload_to="profile/image", default="")
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add = True)



class Contact_us(models.Model):
    First_N = models.CharField(max_length=50)
    emailid = models.CharField(max_length=50)
    message = models.TextField(max_length=120, default="")

    def __str__(self)->str:
        return f"{self.First_N} - {self.emailid}"
        
    
class LiveVideo(models.Model):
    url = models.URLField()
    description = models.TextField(blank=True, null=True)
    author = models.ForeignKey(CustomUser, related_name='live_videos', on_delete=models.CASCADE, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.url} - {self.description}"
    
class Event(models.Model):
    date = models.DateTimeField(auto_now_add = True)
    artist_name = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255)
    event_photo = models.ImageField(upload_to="upcoming/image", default="")

    def _str_(self):
        return f"{self.date} - {self.artist_name} - {self.event_name}"

class Friendship(models.Model):
    UserID = models.ForeignKey(CustomUser,related_name="friend_of", on_delete=models.CASCADE)
    FriendID = models.ForeignKey(CustomUser,related_name="friend", on_delete=models.CASCADE)
    DateAdded= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.UserID} - {self.FriendID}"


class Photos(models.Model):
    UserID = models.ForeignKey(CustomUser,related_name="photo_by", on_delete=models.CASCADE)
    image=models.ImageField(upload_to="userimages",default="")
    timestamp=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.UserID} - {self.image}"

class Profile_posts(models.Model):
    image= models.ImageField(upload_to="posts/image", default="", help_text="ClapStation upload image | height: 360px | width: 640px", validators=[validate_image_dimensions])
    author= models.ForeignKey(CustomUser, on_delete=models.CASCADE, default="")
    created_at = models.DateTimeField(auto_now_add=True)