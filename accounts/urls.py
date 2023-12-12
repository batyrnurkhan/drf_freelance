from django.urls import path
from .views import UserRegistrationAPIView, UserLoginAPIView, UserProfileView, FreelancerListView, \
    FreelancerProfileView, CreateReviewView, TopFreelancersView, UserLogoutAPIView, UserProfileUpdateView

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='register'),
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('freelancers/', FreelancerListView.as_view(), name='freelancer-list'),
    path('freelancer/<str:username>/', FreelancerProfileView.as_view(), name='freelancer-profile'),
    path('freelancer/<str:username>/review/', CreateReviewView.as_view(), name='create-review'),
    path('top-freelancers/', TopFreelancersView.as_view(), name='top-freelancers'),
    path('api/logout/', UserLogoutAPIView.as_view(), name='logout'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
]