# listings/views.py
from rest_framework import generics, permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .models import Listing
from .permissions import IsClientUser
from .serializers import ListingSerializer, OpenListingSerializer
from django.shortcuts import get_object_or_404
import datetime
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from accounts.models import Skill
from .models import Listing
from .serializers import OpenListingSerializer


class OpenListingsListView(generics.ListAPIView):
    queryset = Listing.objects.filter(status='open')
    serializer_class = OpenListingSerializer


class CreateListingView(generics.CreateAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsClientUser]  # Assuming you have an IsClientUser permission class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ListingDetailView(generics.RetrieveAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]  # Allow any user to view listings


class UpdateListingView(generics.UpdateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        listing = serializer.instance
        if listing.user != self.request.user:
            raise permissions.PermissionDenied("You can't edit a listing you didn't create.")
        serializer.save()


class TakeListingView(generics.UpdateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can take a listing
    lookup_field = 'slug'

    def perform_update(self, serializer):
        listing = serializer.instance
        if listing.status != 'open' or listing.freelancer is not None:
            raise permissions.PermissionDenied("This listing is not available for taking.")
        serializer.save(freelancer=self.request.user, status='in_progress', taken_at=timezone.now())


class TakenListingsListView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can view taken listings

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'is_freelancer') and user.is_freelancer:
            return Listing.objects.filter(freelancer=user)
        else:
            raise permissions.PermissionDenied("You do not have permission to view this.")

#################################

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_matched_listings(request):
    user = request.user
    user_skills = user.freelancer_profile.skills.all() if hasattr(user, 'freelancer_profile') else Skill.objects.none()

    # Annotate listings with the count of matched skills
    listings = Listing.objects.filter(status='open').annotate(
        matched_skills_count=Count(
            'skills',
            filter=Q(skills__in=user_skills)
        )
    ).order_by('-matched_skills_count')[:10]  # Get the top 10 matched listings

    serializer = OpenListingSerializer(listings, many=True)
    return Response(serializer.data)


