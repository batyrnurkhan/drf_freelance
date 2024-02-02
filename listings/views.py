from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied

from .models import Listing
from .serializers import ListingSerializer, OpenListingSerializer, TakeListingSerializer
from .permissions import IsClientUser
from accounts.models import CustomUser, FreelancerProfile, Skill
from accounts.serializers import FreelancerProfileSerializer
from chats.models import Chat, Message

class OpenListingsListView(generics.ListAPIView):
    serializer_class = OpenListingSerializer

    def get_queryset(self):
        queryset = Listing.objects.filter(freelancer__isnull=True, status='open')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        skills = self.request.query_params.getlist('skills')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if skills:
            queryset = queryset.filter(skills__name__in=skills).distinct()

        return queryset


class CreateListingView(generics.CreateAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated, IsClientUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ListingDetailView(generics.RetrieveAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]


from django.shortcuts import get_object_or_404

class UpdateListingView(generics.UpdateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        listing = serializer.instance

        if listing.user != self.request.user:
            raise PermissionDenied("You can't edit a listing you didn't create.")

        freelancer_username = self.request.data.get('freelancer')
        if freelancer_username:
            freelancer = CustomUser.objects.filter(username=freelancer_username, role='freelancer').first()
            if freelancer:
                listing.freelancer = freelancer
            else:
                raise serializers.ValidationError({"freelancer": "Freelancer not found or not valid."})

        skills_data = self.request.data.get('skills')
        if skills_data is not None:
            skills = [Skill.objects.get_or_create(name=skill_name)[0] for skill_name in skills_data]
            listing.skills.set(skills)

        serializer.save()


class TakeListingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        listing = get_object_or_404(Listing, slug=slug)
        if listing.status in ['closed', 'in_progress'] or listing.freelancer:
            return Response({'error': 'This listing is not available for taking'}, status=400)

        if not hasattr(request.user, 'freelancer_profile'):
            return Response({'error': 'Only freelancers can take listings'}, status=400)

        chat, created = Chat.get_or_create_with_participants(request.user, listing.user)

        # Create a message in the chat
        Message.objects.create(
            chat=chat,
            author=request.user,
            content=f"Hi {listing.user.username}, I am interested in your listing '{listing.title}'."
        )

        return Response({'message': 'Interest expressed in listing'}, status=200)

class SelectFreelancerView(generics.UpdateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def perform_update(self, serializer):
        listing = serializer.instance
        selected_freelancer_id = self.request.data.get('freelancer_id')
        if listing.interested_freelancers.filter(id=selected_freelancer_id).exists():
            freelancer_user = CustomUser.objects.get(id=selected_freelancer_id)
            freelancer_profile = FreelancerProfile.objects.get(user=freelancer_user)
            serializer.save(freelancer=freelancer_profile.user, status='in_progress')
        else:
            raise PermissionDenied("Selected freelancer did not express interest in this listing.")

class TakenListingsListView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'freelancer_profile'):
            return Listing.objects.filter(freelancer=user)
        else:
            raise PermissionDenied("You do not have permission to view this.")

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_matched_listings(request):
    user = request.user
    user_skills = user.freelancer_profile.skills.all() if hasattr(user, 'freelancer_profile') else Skill.objects.none()
    listings = Listing.objects.filter(status='open').annotate(
        matched_skills_count=Count('skills', filter=Q(skills__in=user_skills))
    ).order_by('-matched_skills_count')[:10]
    serializer = OpenListingSerializer(listings, many=True)
    return Response(serializer.data)

class MatchedFreelancersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client = request.user
        if hasattr(client, 'client_profile'):
            listings = Listing.objects.filter(user=client)

            # Collect skill names from all listings
            skill_names = set()
            for listing in listings:
                for skill in listing.skills.all():
                    skill_names.add(skill.name)

            # Find freelancers with matching skills
            matched_freelancers = FreelancerProfile.objects.filter(
                skills__name__in=skill_names
            ).distinct()

            serializer = FreelancerProfileSerializer(matched_freelancers, many=True)
            return Response(serializer.data)
        else:
            return Response({'message': 'User is not a client or has no listings'}, status=400)

class SearchListingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get('search', '').strip()
        if not query:
            return Response({'message': 'No search query provided'}, status=400)
        listings = Listing.objects.filter(title__icontains=query)
        serializer = OpenListingSerializer(listings, many=True)
        return Response(serializer.data)

class ClientInProgressListingsView(generics.ListAPIView):
    serializer_class = OpenListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Listing.objects.filter(status='in_progress', user=user)

class UserSpecificListingsView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Listing.objects.for_user(user)