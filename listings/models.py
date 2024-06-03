# listings/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from accounts.models import Skill,SkillMapping
import requests
from django.conf import settings

class ListingManager(models.Manager):
    def for_user(self, user):
        if user.role == 'freelancer':
            return self.filter(freelancer=user)
        elif user.role == 'client':
            return self.filter(user=user)
        return self.none()


class Listing(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('in_progress', 'In Progress'),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    description = models.TextField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    taken_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='taken_listings')
    skills = models.ManyToManyField(Skill, blank=True)

    objects = ListingManager()

    def save(self, *args, **kwargs):
        super(Listing, self).save(*args, **kwargs)
        data = {
            'title': self.title,
            'description': self.description,
            'price': str(self.price),
            'skills': [mapping.first_project_skill_id for mapping in SkillMapping.objects.filter(second_project_skill__in=self.skills.all())],
            'client': self.user_id,
            'status': self.status
        }

        print("Data being sent:", data)  # Log the data being sent to troubleshoot

        response = requests.post(settings.FIRST_PROJECT_ORDER_API_URL, json=data)  # Note: Use json= here
        if response.status_code == 201:
            try:
                response_data = response.json()
                print("Data received:", response_data)
            except ValueError:
                print("Failed to decode JSON from response:", response.text)
        else:
            print("Failed to sync order with the first project:", response.status_code, response.text)

    def __str__(self):
        return self.title

