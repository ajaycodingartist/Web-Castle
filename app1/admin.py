from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Post, Comment

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'age', 'dob', 'location')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'age', 'dob', 'location', 'image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'age', 'dob', 'location', 'image', 'is_staff', 'is_superuser'),
        }),
    )
    ordering = ('username',)


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')  # Keep 'created_at' for display, not edit
    search_fields = ('title', 'content', 'user__username')  # Allows searching by title, content, or username
    list_filter = ('created_at',)  # Filter by creation date
    ordering = ('-created_at',)  # Order posts by creation date (most recent first)
    
    # Remove 'created_at' from 'fieldsets' to prevent editing this field in the admin
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'user', 'image')
        }),
        # No need to include 'created_at' here since it's non-editable
    )



class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'cmtcontent', 'created_at')
    search_fields = ('user__username', 'post__title', 'cmtcontent')
    list_filter = ('created_at',)
    ordering = ('-created_at',) 

admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(CustomUser, CustomUserAdmin)

