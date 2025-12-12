from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()
router.register(r'contacts', views.ContactViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('report-spam/', views.SpamReportCreateView.as_view(), name='report-spam'),
    path('search/name/', views.search_by_name, name='search-by-name'),
    path('search/phone/', views.search_by_phone, name='search-by-phone'),
    path('person/<str:phone_number>/', views.person_details, name='person-details'),
] 