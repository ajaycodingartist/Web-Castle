from rest_framework import serializers
from .models import CustomUser, Post, Comment

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'age', 
            'dob', 'location', 'image', 'is_staff', 'is_superuser'
        ]
        read_only_fields = ['is_staff', 'is_superuser']  # Prevent modification via serializer

class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'password', 
            'age', 'dob', 'location', 'image'
        ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            age=validated_data.get('age', 18),
            dob=validated_data.get('dob'),
            location=validated_data.get('location'),
            image=validated_data.get('image')
        )
        return user


class PostSerializer(serializers.ModelSerializer):
    # Automatically set the user to the currently authenticated user when creating a post
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'image', 'created_at']
        read_only_fields = ['id','created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        post = Post.objects.create(user=user, **validated_data)
        return post
    
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # Read-only field to automatically associate the user

    class Meta:
        model = Comment
        fields = ['id', 'user', 'cmtcontent', 'created_at', 'post']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user  # Get user from request context
        post = validated_data.get('post')  # Get post from validated data

        if not post:
            raise serializers.ValidationError("Post is required.")

        comment = Comment.objects.create(user=user, post=post, **validated_data)
        return comment
