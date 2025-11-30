from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings


class UserManager ( BaseUserManager ) :
    def create_user(self, username, email=None, password=None, **extra_fields) :
        if not username :
            raise ValueError ( 'Username is required!' )

        email = self.normalize_email ( email ) if email else None
        user = self.model ( username=username, email=email, **extra_fields )
        user.set_password ( password )
        user.save ( using=self._db )
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields) :
        extra_fields.setdefault ( 'is_staff', True )
        extra_fields.setdefault ( 'is_superuser', True )
        extra_fields.setdefault ( 'is_active', True )

        if extra_fields.get ( 'is_staff' ) is not True :
            raise ValueError ( "Superuser's property is_staff must be True" )
        if extra_fields.get ( 'is_superuser' ) is not True :
            raise ValueError ( "Superuser's property is_superuser must be True" )

        return self.create_user ( username, email, password, **extra_fields )


class User ( AbstractBaseUser ) :
    username = models.CharField ( max_length=150, unique=True )
    email = models.EmailField ( blank=True, null=True )
    first_name = models.CharField ( max_length=150, blank=True )
    last_name = models.CharField ( max_length=150, blank=True )
    phone_number = models.CharField ( max_length=15, blank=True, null=True )

    is_active = models.BooleanField ( default=True )
    is_staff = models.BooleanField ( default=False )
    is_superuser = models.BooleanField ( default=True )

    objects = UserManager ()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self) :
        return self.username

    def has_perm(self, perm, obj=None) :
        return self.is_superuser

    def has_module_perms(self, app_label) :
        return self.is_superuser or self.is_staff


class TodoItem ( models.Model ) :
    user = models.ForeignKey (
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='todos',
        verbose_name='User'
    )
    title = models.CharField (
        max_length=200,
        verbose_name='Title'
    )
    description = models.TextField (
        blank=True,
        null=True,
        verbose_name='Description'
    )
    is_completed = models.BooleanField (
        default=False,
        verbose_name='Completed'
    )
    due_date = models.DateField (
        blank=True,
        null=True,
        verbose_name='Due Date'
    )
    created_at = models.DateTimeField (
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_at = models.DateTimeField (
        auto_now=True,
        verbose_name='Updated at'
    )

    class Meta :
        ordering = ['-created_at']
        verbose_name = 'Todo element'
        verbose_name_plural = 'Todo elements'

    def __str__(self) :
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.title}"
