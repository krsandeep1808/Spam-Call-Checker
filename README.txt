Spam Detection and Contact Management API
=======================================

A Django REST API that allows users to manage contacts, search for people by name or phone number, and report spam numbers. The API is designed to be consumed by a mobile application.

Features
--------
1. User Management
   - Registration with phone number and optional email
   - Token-based authentication
   - Phone number validation

2. Contact Management
   - Add, view, edit, and delete contacts
   - Automatic contact import (simulated)
   - Unique phone numbers per user's contact list

3. Spam Detection
   - Report numbers as spam
   - View spam likelihood for any number
   - Global spam database

4. Search Functionality
   - Search by name (partial matches supported)
   - Search by phone number
   - View detailed person information
   - Conditional email display based on contact relationships

Setup Instructions
-----------------
1. Install Python 3.8 or higher
2. Install required packages:
   pip install django djangorestframework django-cors-headers Faker

3. Run migrations:
   python manage.py migrate

4. Create a superuser:
   python manage.py createsuperuser

5. Populate the database with sample data:
   python manage.py populate_data --users 50 --contacts 200 --spam_reports 30

6. Start the development server:
   python manage.py runserver

The API will be available at http://localhost:8000/api/

API Endpoints
------------
1. Authentication
   POST /api/register/ - Register a new user
   POST /api/login/ - Login and get authentication token

2. Contacts
   GET /api/contacts/ - List all contacts
   POST /api/contacts/ - Add a new contact
   GET /api/contacts/{id}/ - Get contact details
   PUT /api/contacts/{id}/ - Update contact
   DELETE /api/contacts/{id}/ - Delete contact

3. Spam Reports
   POST /api/report-spam/ - Report a number as spam

4. Search
   GET /api/search/name/?name={query} - Search by name
   GET /api/search/phone/?phone={number} - Search by phone number
   GET /api/person/{phone_number}/ - Get detailed person information

Authentication
-------------
All endpoints except registration and login require token authentication.
Include the token in the request header:
Authorization: Token your_token_here

Example API Usage
----------------
1. Register a new user:
   POST /api/register/
   {
       "username": "testuser",
       "password": "your_password",
       "first_name": "Test",
       "last_name": "User",
       "phone_number": "+1234567890",
       "email": "test@example.com"
   }

2. Login to get token:
   POST /api/login/
   {
       "username": "testuser",
       "password": "your_password"
   }

3. Search for a person:
   GET /api/search/name/?name=John
   Authorization: Token your_token_here

Admin Interface
--------------
Access the admin interface at http://localhost:8000/admin/
Use the superuser credentials to log in and manage users, contacts, and spam reports.

Security Notes
-------------
- All endpoints except registration and login require authentication
- Email addresses are only shown if the searching user is in the target user's contact list
- Phone numbers are validated using a regex pattern
- CORS is configured to allow only specific origins
- Token-based authentication is used for API security

Development
-----------
The project uses:
- Django 5.1.7
- Django REST Framework
- SQLite database (for development)
- Token authentication
- CORS headers for API access

For production deployment:
1. Change DEBUG to False in settings.py
2. Use a production-grade database (e.g., PostgreSQL)
3. Configure proper CORS settings
4. Use HTTPS
5. Set up proper static file serving
6. Configure proper security settings 