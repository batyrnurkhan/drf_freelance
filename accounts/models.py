from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

# Client Profile Model
class ClientProfile(models.Model):
    PREFERRED_COMMUNICATION_CHOICES = [
        ('email', 'Email'),
        ('chat', 'Chat'),
        ('phone', 'Phone'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='client_profile')
    company_website = models.URLField(max_length=255, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    profile_image = models.ImageField(upload_to='profile_images', blank=True)
    contact_name = models.CharField(max_length=255, editable=False)
    contact_email = models.EmailField(max_length=255, editable=False)
    preferred_communication = models.CharField(max_length=10, choices=PREFERRED_COMMUNICATION_CHOICES, default='email')

    def save(self, *args, **kwargs):
        if not self.contact_name:
            self.contact_name = f"{self.user.first_name} {self.user.last_name}"
        if not self.contact_email:
            self.contact_email = self.user.email
        super(ClientProfile, self).save(*args, **kwargs)

# Freelancer Profile Model
class FreelancerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='freelancer_profile')
    portfolio = models.URLField(max_length=255, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    average_rating = models.FloatField(default=0.0)
    reviews = models.TextField(blank=True)  # Simple text field for reviews, consider a related model for more complexity
    profile_image = models.ImageField(upload_to='profile_images', blank=True)

    def update_rating(self):
        total_rating = sum(review.rating for review in self.received_reviews.all())
        self.average_rating = total_rating / self.received_reviews.count()
        self.save()

# Signal to create or update user profile
@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if instance.role == 'client':
        ClientProfile.objects.get_or_create(user=instance)
    elif instance.role == 'freelancer':
        FreelancerProfile.objects.get_or_create(user=instance)

class Review(models.Model):
    rating = models.FloatField()
    text = models.TextField()
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    freelancer = models.ForeignKey(FreelancerProfile, on_delete=models.CASCADE, related_name='received_reviews')

    def save(self, *args, **kwargs):
        super(Review, self).save(*args, **kwargs)
        self.freelancer.update_rating()  # Update freelancer's rating after a new review is saved

    def __str__(self):
        return f"Review by {self.client.username} for {self.freelancer.user.username}"