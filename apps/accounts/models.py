from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class Profile(models.Model):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    STAFF = 'STAFF'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (STAFF, 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STAFF)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"