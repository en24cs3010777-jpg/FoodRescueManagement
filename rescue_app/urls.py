"""
URL Configuration for rescue_app.
"""

from django.urls import path
from rescue_app import views

urlpatterns = [
    # Public & Authentication
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard & Mode Switcher
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('switch-mode/<str:mode>/', views.switch_mode_view, name='switch_mode'),

    # Food Management
    path('add-food/', views.add_food_view, name='add_food'),
    path('view-food/', views.view_food_view, name='view_food'),
    path('food/<str:food_id>/', views.food_detail_view, name='food_detail'),
    path('food/<str:food_id>/claim/', views.claim_food_view, name='claim_food'),
    path('food/<str:food_id>/collect/', views.mark_collected_view, name='mark_collected'),
    path('food/<str:food_id>/cancel/', views.cancel_food_view, name='cancel_food'),

    # Provider & Seeker Dashboards
    path('my-listings/', views.my_listings_view, name='my_listings'),
    path('my-claims/', views.my_claims_view, name='my_claims'),

    # Account Management
    path('account-settings/', views.account_settings_view, name='account_settings'),

    # Database Diagnostic Tool
    path('db-status/', views.db_status_view, name='db_status'),
]
