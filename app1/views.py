from django.shortcuts import render, redirect
import requests
import logging
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
# from django.contrib.auth import login, authenticate
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from .models import CustomUser, Post, Comment
from .serializers import CustomUserSerializer, CustomUserCreateSerializer, PostSerializer, CommentSerializer
from django.contrib.auth.forms import UserCreationForm
from rest_framework.permissions import AllowAny
from django.contrib import messages
from .forms import PostForm
from django.http import JsonResponse
import json
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

# Create your views here.

def index(request):
    return render(request, 'index.html')

def login(request):
    return render(request, 'login.html')


# def register(request):
#     if request.method == 'POST':
#         # Get form data
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         age = request.POST.get('age')
#         dob = request.POST.get('dob')
#         location = request.POST.get('location')
#         image = request.FILES.get('image')  # Handle image uploads
        
#         # Prepare the data to send to the API
#         data = {
#             'username': username,
#             'email': email,
#             'password': password,
#             'age': age,
#             'dob': dob,
#             'location': location,
#         }

#         # If there's an image, handle it
#         if image:
#             files = {'image': image}
#         else:
#             files = {}

#         token = request.session.get('auth_token') 

#         # Send POST request to the API
#         api_url = f"http://127.0.0.1:8000/customuser/"  # Set your API URL in settings
#         response = requests.post(api_url, data=data, files=files)

#         if response.status_code == 201:
#             # If the user is successfully created, log them in
#             user_data = response.json()
#             user = CustomUser.objects.get(id=user_data['id'])  # Assuming user ID is returned
#             login(request, user)
# #
#             # Redirect to home page
#             return redirect('login')

#         # Handle errors returned from the API
#         else:
#             error = response.json().get('detail', 'Something went wrong.')
#             return render(request, 'register.html', {'error': error})

#     return render(request, 'register.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        age = request.POST.get('age')
        dob = request.POST.get('dob')
        location = request.POST.get('location')
        image = request.FILES.get('image')

        data = {
            'username': username,
            'email': email,
            'password': password,
            'age': age,
            'dob': dob,
            'location': location,
        }

        if image:
            files = {'image': image}
        else:
            files = {}

        token = request.session.get('auth_token') 
        api_url = f"http://127.0.0.1:8000/customuser/"
        response = requests.post(api_url, data=data, files=files)

        if response.status_code == 201:
            return redirect('login')
        else:
            error = response.json().get('detail', 'Something went wrong.')
            return render(request, 'register.html', {'error': error})

    return render(request, 'register.html')



@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    Handle user login via API, authenticate and return JWT token if successful.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        auth_login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({'access_token': access_token}, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



def landing(request):
    return render(request, 'landing.html')


def createblog(request):

    return render(request, 'createblog.html')

# @api_view(['POST'])
# def create_blog(request):
#     if not request.user.is_authenticated:
#         return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

#     # Deserialize the data from the request
#     serializer = PostSerializer(data=request.data, context={'request': request})
    
#     if serializer.is_valid():
#         # Save the post (the user is set in the serializer's create method)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def list_blogs(request):
#     posts = Post.objects.all().order_by('-created_at')  # Fetch all blogs, ordered by creation date
#     serializer = PostSerializer(posts, many=True, context={'request': request})
#     return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def list_blogs(request):
    if request.method == 'GET':
        posts = Post.objects.all().order_by('-created_at')  # Fetch all blogs, ordered by creation date
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        # Deserialize the data from the request
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Save the post (the user is set in the serializer's create method)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# def blog_detail(request, blog_id):
#     blog = Post.objects.get(id=blog_id)
#     return render(request, 'blog_detail.html', {'blog': blog})

def blog_detail(request, blog_id):
    post = get_object_or_404(Post, id=blog_id)
    context = {
        'blog': post
    }
    return render(request, 'blog_detail.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def add_comment(request, blog_id):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    post = get_object_or_404(Post, id=blog_id)

    # Ensure comment content is passed
    cmtcontent = request.data.get('cmtcontent')
    if not cmtcontent:
        return Response({'error': 'Comment content is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new comment
    comment_data = {
        'user': request.user.id,
        'post': post.id,
        'cmtcontent': cmtcontent,
    }

    serializer = CommentSerializer(data=comment_data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# add comments on landing page

# Fetch all blogs
@require_http_methods(["GET"])
def get_blogs(request):
    blogs = Post.objects.all().values('id', 'title', 'content', 'created_at', 'user__username', 'image')
    return JsonResponse(list(blogs), safe=False)

# Fetch comments for a specific blog
# @require_http_methods(["GET"])
# def get_blog_comments(request, blog_id):
#     try:
#         comments = Comment.objects.filter(post_id=blog_id).values('id', 'cmtcontent', 'user__username', 'created_at')
#         return JsonResponse(list(comments), safe=False)
#     except ObjectDoesNotExist:
#         return JsonResponse({'error': 'Blog not found'}, status=404)

@require_http_methods(["GET"])
def get_blog_comments(request, blog_id):
    try:
        comments = Comment.objects.filter(post_id=blog_id).values('id', 'cmtcontent', 'user__username', 'created_at')
        return JsonResponse(list(comments), safe=False)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Blog not found'}, status=404)

# Add a new comment
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_comment(request):
    try:
        data = json.loads(request.body)
        blog_id = data.get('post')
        content = data.get('cmtcontent')

        if not content:
            return JsonResponse({'error': 'Comment content is required'}, status=400)

        blog = Post.objects.get(id=blog_id)
        comment = Comment.objects.create(post=blog, cmtcontent=content, user=request.user)
        return JsonResponse({'id': comment.id, 'cmtcontent': comment.cmtcontent, 'user': request.user.username, 'created_at': comment.created_at})
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Blog not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)


# def user_blogs(request):
#     # Ensure the user is authenticated
#     if request.user.is_authenticated:
#         # Fetch the blogs created by the logged-in user
#         user_blogs = Post.objects.filter(user=request.user)
#         return render(request, 'user_blogs.html', {'blogs': user_blogs})
#     else:
#         # Redirect to login page if user is not authenticated
#         return redirect('login') 

def user_blogs(request):
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        # Fetch the blogs created by the logged-in user
        user_blogs = Post.objects.filter(user=request.user)

        # Set up pagination
        paginator = Paginator(user_blogs, 5)  # Show 5 posts per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'user_blogs.html', {'page_obj': page_obj})

    else:
        # Redirect to login page if user is not authenticated
        return redirect('login')
    
@login_required
def delete_blog(request, blog_id):
    # Fetch the blog
    blog = get_object_or_404(Post, id=blog_id)

    # Ensure the logged-in user is the owner of the blog
    if blog.user == request.user:
        blog.delete()
        return redirect('user_blogs')  # Redirect to the list of user's blogs after deletion
    else:
        return redirect('user_blogs')


def logout_view(request):
    logout(request)  # Log the user out
    return redirect('login')  # Redirect to login page after logout




# @api_view(['GET', 'POST'])
# def custom_user_list(request):
#     """
#     List all users (requires login) or create a new user (no login required).
#     """
#     if request.method == 'GET':
#         # Require login for listing users
#         if not request.user.is_authenticated:
#             return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

#         users = CustomUser.objects.all()
#         serializer = CustomUserSerializer(users, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         # Allow user registration without login
#         serializer = CustomUserCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # This allows unauthenticated access to POST (registration)
def custom_user_list(request):
    """
    List all users (requires login) or create a new user (no login required).
    """
    if request.method == 'GET':
        # Require login for listing users
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Allow user registration without login
        serializer = CustomUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def custom_user_detail(request, pk):
    """
    Retrieve, update, or delete a specific user by ID.
    """
    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def custom_user_me(request):
    """
    Retrieve the authenticated user's profile.
    """
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)

