from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Email field must be provided")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_admin', True)
        kwargs.setdefault('is_staff', True)

        if kwargs.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if kwargs.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if kwargs.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self.create_user(email, password, **kwargs)

class User(AbstractBaseUser, PermissionsMixin):
    userId = models.CharField(max_length=50, unique=True, null=False, default=uuid.uuid4 )
    firstName = models.CharField(max_length=250, null=False)
    lastName = models.CharField(max_length=250, null=False)
    email = models.EmailField(max_length=250, unique=True, null=False)
    phone = models.CharField(max_length=20)       
    organizations = models.ManyToManyField('Organization')
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName'] 

    def save(self, *args, **kwargs):
        if not self.pk and not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
        
class Organisation(models.Model):
    orgId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=250, null=False)
    description = models.TextField(null=True)
    users = models.ManyToManyField(CustomUser, related_name='organisations')

    def __str__(self):
        return self.name
