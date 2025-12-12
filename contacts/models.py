from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom user model with additional fields for phone number and email validation
    """
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    email = models.EmailField(blank=True, null=True)
    
    # Override username field to use phone number
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'first_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number})"

class Contact(models.Model):
    """
    Represents a contact in a user's contact list
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        # A user can't have multiple contacts with the same phone number
        unique_together = ('owner', 'phone_number')
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"

class SpamReport(models.Model):
    """
    Represents a spam report for a phone number
    """
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spam_reports')
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    reported_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # A user can report a number as spam only once
        unique_together = ('reporter', 'phone_number')
    
    def __str__(self):
        return f"Spam report by {self.reporter.get_full_name()} for {self.phone_number}"
