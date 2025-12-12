from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Contact, SpamReport

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone_number', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'phone_number', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'password1', 'password2'),
        }),
    )

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'owner')
    list_filter = ('owner',)
    search_fields = ('name', 'phone_number', 'email')
    ordering = ('name',)

@admin.register(SpamReport)
class SpamReportAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'reporter', 'reported_at')
    list_filter = ('reporter', 'reported_at')
    search_fields = ('phone_number', 'reporter__username', 'reporter__phone_number')
    ordering = ('-reported_at',)
