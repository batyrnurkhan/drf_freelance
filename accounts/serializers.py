from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ClientProfile, FreelancerProfile, Review, Skill

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        extra_kwargs = {'email': {'required': False}}




class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user




class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = [
            'user',
            'company_website',
            'company_name',
            'profile_image',
            'contact_name',
            'contact_email',
            'preferred_communication',
            'profile_video'
        ]
        read_only_fields = ('contact_name', 'contact_email')  # These fields are auto-populated


class FreelancerProfileSerializer(serializers.ModelSerializer):
    skill_names = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    user = UserSerializer(read_only=True)
    reviews = serializers.SerializerMethodField()
    introduction_video = serializers.FileField(required=False)  # Add this line

    class Meta:
        model = FreelancerProfile
        fields = [
            'user',
            'portfolio',
            'skills',
            'skill_names',
            'profile_image',
            'average_rating',
            'reviews',
            'introduction_video',  # Include the field here
        ]
        extra_kwargs = {'skills': {'read_only': True}}

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['skills'] = [skill.name for skill in instance.skills.all()]
        return response

    def update(self, instance, validated_data):
        skill_names = validated_data.pop('skill_names', None)
        if skill_names is not None:
            skills = [Skill.objects.get_or_create(name=name)[0] for name in skill_names]
            instance.skills.set(skills)
        return super().update(instance, validated_data)

    def get_reviews(self, obj):
        reviews = obj.received_reviews.all()  # assuming a reverse relation from Review to FreelancerProfile
        return ReviewSerializer(reviews, many=True).data

    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None


class FreelancerProfileNestedSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()

    class Meta:
        model = FreelancerProfile
        fields = ['portfolio', 'skills', 'average_rating', 'reviews', 'profile_image']

    def get_skills(self, obj):
        return [skill.name for skill in obj.skills.all()]

class FreelancerListSerializer(serializers.ModelSerializer):
    freelancer_profile = FreelancerProfileNestedSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'freelancer_profile']



from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'text']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']
