from rest_framework import generics, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.generics import ListAPIView
from .models import ClientProfile, FreelancerProfile, CustomUser
from .serializers import UserRegistrationSerializer, ClientProfileSerializer, FreelancerProfileSerializer, \
    FreelancerListSerializer, ReviewSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

class UserRegistrationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# accounts/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import ClientProfile, FreelancerProfile, CustomUser
from .serializers import ClientProfileSerializer, FreelancerProfileSerializer, UserSerializer  # Import UserSerializer



class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        response_data = {}

        if user.role == 'client':
            client_profile = ClientProfile.objects.get(user=user)
            response_data = ClientProfileSerializer(client_profile).data
        elif user.role == 'freelancer':
            freelancer_profile = FreelancerProfile.objects.get(user=user)
            response_data = FreelancerProfileSerializer(freelancer_profile).data
        else:
            return Response({'error': 'User role is not defined'}, status=status.HTTP_400_BAD_REQUEST)

        # Include user basic data
        response_data.update({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        })

        return Response(response_data)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class FreelancerListView(generics.ListAPIView):
    serializer_class = FreelancerListSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(role='freelancer')

class FreelancerProfileView(generics.RetrieveAPIView):
    queryset = FreelancerProfile.objects.all()
    serializer_class = FreelancerProfileSerializer
    permission_classes = [permissions.AllowAny]  # Set appropriate permissions
    lookup_field = 'user__username'

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        username = self.kwargs.get('username')
        user = get_object_or_404(CustomUser, username=username, role='freelancer')
        obj = get_object_or_404(queryset, user=user)
        return obj


class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        freelancer_username = self.kwargs.get('username')
        freelancer = get_object_or_404(CustomUser, username=freelancer_username, role='freelancer').freelancer_profile
        client = self.request.user

        if client.role != 'client':
            raise permissions.PermissionDenied("Only clients can give reviews.")

        serializer.save(client=client, freelancer=freelancer)


class TopFreelancersView(ListAPIView):
    serializer_class = FreelancerListSerializer

    def get_queryset(self):
        # Get top 3 FreelancerProfiles by rating
        top_profiles = FreelancerProfile.objects.order_by('-average_rating')[:3]

        # Fetch the associated User objects
        top_user_ids = [profile.user_id for profile in top_profiles]
        return CustomUser.objects.filter(id__in=top_user_ids)


class UserLogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Add the token to the blacklist
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Add parser classes

    def put(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        if user.role == 'freelancer':
            profile_serializer = FreelancerProfileSerializer(user.freelancer_profile, data=data, context={'request': request})
        elif user.role == 'client':
            profile_serializer = ClientProfileSerializer(user.client_profile, data=data, context={'request': request})
        else:
            return Response({'error': 'Invalid user role'}, status=status.HTTP_400_BAD_REQUEST)

        if profile_serializer.is_valid():
            profile_serializer.save()
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': user.role,  # Возвращаем роль пользователя
                'user_id': user.id
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
