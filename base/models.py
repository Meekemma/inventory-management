from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin,Group



# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates, saves, and returns a User with the given email, first name, last name, and password.
        """
        if not email:
            raise ValueError('email is required')
        if not first_name:
            raise ValueError('first name is required')
        if not last_name:
            raise ValueError('last name is required')
        
        email =self.normalize_email(email).lower()

        user = self.model(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self.db)
        return user


    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email=email, first_name=first_name, last_name=last_name, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.save(using=self._db)
        return user
    

AUTH_PROVIDERS = {'email': 'email', 'google': 'google'}


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super(User, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at'] 










