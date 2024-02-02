from django.contrib import admin

from .models import CustomUser, FreelancerProfile, Skill, ClientProfile

class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'portfolio', 'average_rating']
    filter_horizontal = ('skills',)

admin.site.register(CustomUser)
admin.site.register(FreelancerProfile)
admin.site.register(Skill)
admin.site.register(ClientProfile)
