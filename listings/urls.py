from django.urls import path
from .views import (CreateListingView, ListingDetailView, UpdateListingView, 
                    TakeListingView, OpenListingsListView, TakenListingsListView,
                    get_matched_listings, MatchedFreelancersView, SearchListingsView, 
                    ClientInProgressListingsView, UserSpecificListingsView)  # Import UserSpecificListingsView

urlpatterns = [
    path('open/', OpenListingsListView.as_view(), name='open-listings'),
    path('user-specific/', UserSpecificListingsView.as_view(), name='user-specific-listings'),
    path('client/matched_freelancers/', MatchedFreelancersView.as_view(), name='matched_freelancers'),
    path('progress/', ClientInProgressListingsView.as_view(), name='in-progress-listings'),
    path('create/', CreateListingView.as_view(), name='create-listing'),
    path('<slug:slug>/', ListingDetailView.as_view(), name='listing-detail'),
    path('<slug:slug>/update/', UpdateListingView.as_view(), name='update-listing'),
    path('<slug:slug>/take/', TakeListingView.as_view(), name='take-listing'),
    path('taken/', TakenListingsListView.as_view(), name='taken-listings'),
    path('open/matched/', get_matched_listings, name='matched-listings'),
    path('open/search/', SearchListingsView.as_view(), name='search-listings'),
]