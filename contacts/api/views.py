from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Case, When, IntegerField, F, Value
from django.shortcuts import get_object_or_404
from .serializers import (
    UserSerializer, ContactSerializer, SpamReportSerializer, SearchResultSerializer
)
from contacts.models import Contact, SpamReport

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })

class ContactViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing contacts
    """
    serializer_class = ContactSerializer
    
    def get_queryset(self):
        return Contact.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SpamReportCreateView(generics.CreateAPIView):
    """
    API endpoint for reporting a number as spam
    """
    serializer_class = SpamReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

@api_view(['GET'])
def search_by_name(request):
    """
    Search for a person by name in the global database
    """
    name_query = request.query_params.get('name', '')
    if not name_query:
        return Response({'error': 'Name parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get all registered users whose name matches the query
    registered_users_q = Q(first_name__icontains=name_query) | Q(last_name__icontains=name_query)
    registered_users = User.objects.filter(registered_users_q)
    
    # Get all contacts whose name matches the query
    contacts = Contact.objects.filter(name__icontains=name_query)
    
    # Combine and process results
    results = []
    processed_numbers = set()
    
    # Process registered users first (they should take precedence)
    for user in registered_users:
        # Calculate spam likelihood
        spam_count = SpamReport.objects.filter(phone_number=user.phone_number).count()
        total_users = User.objects.count()
        spam_likelihood = (spam_count / total_users) if total_users > 0 else 0
        
        results.append({
            'name': user.get_full_name(),
            'phone_number': user.phone_number,
            'spam_likelihood': spam_likelihood,
            'is_registered_user': True,
            'email': user.email if user in request.user.contacts.all() else None
        })
        processed_numbers.add(user.phone_number)
    
    # Process contacts
    for contact in contacts:
        if contact.phone_number not in processed_numbers:
            # Calculate spam likelihood
            spam_count = SpamReport.objects.filter(phone_number=contact.phone_number).count()
            total_users = User.objects.count()
            spam_likelihood = (spam_count / total_users) if total_users > 0 else 0
            
            # Check if this phone number belongs to a registered user
            try:
                user = User.objects.get(phone_number=contact.phone_number)
                is_registered = True
                email = user.email if request.user in user.contacts.all() else None
            except User.DoesNotExist:
                is_registered = False
                email = contact.email
                
            results.append({
                'name': contact.name,
                'phone_number': contact.phone_number,
                'spam_likelihood': spam_likelihood,
                'is_registered_user': is_registered,
                'email': email
            })
            processed_numbers.add(contact.phone_number)
    
    # Sort results: first show people whose names start with the search query
    # then people whose names contain but don't start with the search query
    def sort_key(result):
        name = result['name'].lower()
        query = name_query.lower()
        if name.startswith(query):
            return 0, name
        return 1, name
        
    results.sort(key=sort_key)
    
    serializer = SearchResultSerializer(results, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def search_by_phone(request):
    """
    Search for a person by phone number in the global database
    """
    phone_query = request.query_params.get('phone', '')
    if not phone_query:
        return Response({'error': 'Phone parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Try to find a registered user with this phone number
    try:
        user = User.objects.get(phone_number=phone_query)
        # Calculate spam likelihood
        spam_count = SpamReport.objects.filter(phone_number=user.phone_number).count()
        total_users = User.objects.count()
        spam_likelihood = (spam_count / total_users) if total_users > 0 else 0
        
        # Check if the searching user is in the contact list of the found user
        should_show_email = Contact.objects.filter(
            owner=user, 
            phone_number=request.user.phone_number
        ).exists()
        
        result = [{
            'name': user.get_full_name(),
            'phone_number': user.phone_number,
            'spam_likelihood': spam_likelihood,
            'is_registered_user': True,
            'email': user.email if should_show_email else None
        }]
        
        serializer = SearchResultSerializer(result, many=True)
        return Response(serializer.data)
        
    except User.DoesNotExist:
        # If no registered user is found, look for contacts with this number
        contacts = Contact.objects.filter(phone_number=phone_query)
        
        if not contacts.exists():
            # Phone number doesn't exist in our database
            return Response([], status=status.HTTP_200_OK)
        
        # Calculate spam likelihood
        spam_count = SpamReport.objects.filter(phone_number=phone_query).count()
        total_users = User.objects.count()
        spam_likelihood = (spam_count / total_users) if total_users > 0 else 0
        
        results = []
        for contact in contacts:
            results.append({
                'name': contact.name,
                'phone_number': contact.phone_number,
                'spam_likelihood': spam_likelihood,
                'is_registered_user': False,
                'email': contact.email
            })
        
        serializer = SearchResultSerializer(results, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def person_details(request, phone_number):
    """
    Get detailed information about a person
    """
    # Try to find a registered user with this phone number
    try:
        user = User.objects.get(phone_number=phone_number)
        # Calculate spam likelihood
        spam_count = SpamReport.objects.filter(phone_number=user.phone_number).count()
        total_users = User.objects.count()
        spam_likelihood = (spam_count / total_users) if total_users > 0 else 0
        
        # Check if the searching user is in the contact list of the found user
        should_show_email = Contact.objects.filter(
            owner=user, 
            phone_number=request.user.phone_number
        ).exists()
        
        result = {
            'name': user.get_full_name(),
            'phone_number': user.phone_number,
            'spam_likelihood': spam_likelihood,
            'is_registered_user': True,
            'email': user.email if should_show_email else None
        }
        
        serializer = SearchResultSerializer(result)
        return Response(serializer.data)
        
    except User.DoesNotExist:
        # Check if this phone number exists in contacts
        contact = get_object_or_404(Contact, phone_number=phone_number)
        
        # Calculate spam likelihood
        spam_count = SpamReport.objects.filter(phone_number=phone_number).count()
        total_users = User.objects.count()
        spam_likelihood = (spam_count / total_users) if total_users > 0 else 0
        
        result = {
            'name': contact.name,
            'phone_number': contact.phone_number,
            'spam_likelihood': spam_likelihood,
            'is_registered_user': False,
            'email': contact.email
        }
        
        serializer = SearchResultSerializer(result)
        return Response(serializer.data) 