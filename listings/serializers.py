# listings/serializers.py
from rest_framework import serializers
from .models import Listing

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('user',)  # 'user' field will not be expected in the incoming data

    # 'create' should be aligned with 'class Meta'
    def create(self, validated_data):
        # Set the user to the current user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

# listings/serializers.py
class OpenListingSerializer(serializers.ModelSerializer):
    skills = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'  # Assuming 'name' is the field in the Skill model that you want to display
    )

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'created_at', 'slug', 'skills']