from django.urls import path
from app1.views import index, custom_user_list, custom_user_detail, custom_user_me, register,login, api_login, landing, logout_view, createblog, list_blogs, blog_detail, add_comment, get_blogs, get_blog_comments, user_blogs, delete_blog
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('', index, name='home'),
    path('login/', login, name='login'),
    # path('login/', login_view, name='login'),
    path('api/login/', api_login, name='api-login'),
    path('register/', register, name='register'),
    path('landing/', landing, name='landing'),
    path('createblog/', createblog, name='createblog'),
    # path('api/posts/', create_blog, name='create_blog'),
    path('api/posts/', list_blogs, name='list_blogs'),
    path('blog/<int:blog_id>/', blog_detail, name='blog_detail'),
    path('api/blog/<int:blog_id>/add_comment/', add_comment, name='add_comment_api'),
    # add comment in lamding page
    path('api/posts/', get_blogs, name='get_blogs'),
    path('api/posts/<int:blog_id>/comments/', get_blog_comments, name='get_blog_comments'),
    path('api/comments/', add_comment, name='add_comment'),
    path('user-blogs/', user_blogs, name='user_blogs'),
    path('blog/<int:blog_id>/delete/', delete_blog, name='delete_blog'), 
    path('logout/', logout_view, name='logout'),
    path('customuser/', custom_user_list, name='custom_user_list'),  # List all users or create a new user
    path('custom_user_detail/<int:pk>/', custom_user_detail, name='custom_user_detail'),  # Retrieve, update, or delete a specific user
    path('custom_user_me/me/', custom_user_me, name='custom_user_me'), # Retrieve the authenticated user's profile
    # JWT Authentication routes
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # To get the access and refresh tokens
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # To refresh the access token using the refresh token
]