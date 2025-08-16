from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.contrib.auth.base_user import BaseUserManager

class UserAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, first_name=None, last_name=None, gender=None, address=None, phone_number=None):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email).lower()
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            address=address,
            phone_number=phone_number
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_employee(self, email, username, password=None, permissions=None, first_name=None, last_name=None, gender=None, address=None, phone_number=None):
        """
        Create a staff account with optional permissions.
        """
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            address=address,
            phone_number=phone_number
        )
        user.is_staff = True
        user.is_active = True
        if permissions:
            for perm_codename in permissions:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    user.user_permissions.add(permission)
                except Permission.DoesNotExist:
                    raise ValueError(f"Invalid permission: {perm_codename}")
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, first_name=None, last_name=None, gender=None, address=None, phone_number=None):
        """
        Create a SuperAdmin account with full permissions.
        """
        user = self.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            address=address,
            phone_number=phone_number
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user

class UserAccount(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
    )

    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='useraccount_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='useraccount_set',
        blank=True,
    )

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    class Meta:
        permissions = [
            ("add_user", "Can add user"),
            ("view_user", "Can view user"),
            ("change_user", "Can change user"),
            ("delete_user", "Can delete user"),
        ]