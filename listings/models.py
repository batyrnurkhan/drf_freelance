# listings/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from accounts.models import Skill
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
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='taken_listings')
    skills = models.ManyToManyField(Skill, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure the slug is unique
            original_slug = self.slug
            num = 1
            while Listing.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{num}'
                num += 1
        super(Listing, self).save(*args, **kwargs)

    def __str__(self):
        return self.description
