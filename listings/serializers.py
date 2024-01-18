from rest_framework import serializers
from .models import Listing
from accounts.models import Skill, CustomUser

class ListingSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    user = serializers.SerializerMethodField()
    freelancer = serializers.SerializerMethodField()
    owner_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = '__all__'

    def get_owner_profile_picture(self, obj):
        if obj.user.role == 'client' and hasattr(obj.user, 'client_profile'):
            return obj.user.client_profile.profile_image.url if obj.user.client_profile.profile_image else None
        elif obj.user.role == 'freelancer' and hasattr(obj.user, 'freelancer_profile'):
            return obj.user.freelancer_profile.profile_image.url if obj.user.freelancer_profile.profile_image else None
        return None

    def get_user(self, obj):
        return obj.user.username if obj.user else None

    def get_freelancer(self, obj):
        # Directly access the username of the freelancer CustomUser object
        return obj.freelancer.username if obj.freelancer else None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class OpenListingSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'created_at', 'slug', 'skills']


class TakeListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['freelancer', 'status']

    def update(self, instance, validated_data):
        instance.freelancer = validated_data.get('freelancer', instance.freelancer)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance