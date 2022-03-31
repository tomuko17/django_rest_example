# from django.shortcuts import render
from itsdangerous import Serializer
from rest_framework import generics, permissions, mixins, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment, PostLike, CommentLike
from .serializers import PostSerializer, CommentSerializer, PostLikeSerializer, UserSerializer,CommentLikeSerializer


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=kwargs['pk'], user=self.request.user)
        if post.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError(_("Cannot delete posts of other users!"))
    
    def put(self, request, *args, **kwargs):
        post = Post.objects.filter(pk=kwargs['pk'], user=self.request.user)
        if post.exists():
            return self.update(request, *args, **kwargs)
        else:
            raise ValidationError(_("Cannot edit posts of other users!"))


class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['pk'])
        serializer.save(user=self.request.user, post=post)

    def get_queryset(self):
        post = Post.objects.get(pk=self.kwargs['pk'])
        queryset = super().get_queryset().filter(post=post)
        return queryset


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        comment = Comment.objects.filter(pk=kwargs['pk'], user=self.request.user)
        if comment.exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise ValidationError(_("Cannot delete comments of other users!"))
    
    def put(self, request, *args, **kwargs):
        comment = Comment.objects.filter(pk=kwargs['pk'], user=self.request.user)
        if comment.exists():
            return self.update(request, *args, **kwargs)
        else:
            raise ValidationError(_("Cannot edit comments of other users!"))


class PostLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        return PostLike.objects.filter(post=post, user=user)
    
    def perform_create(self, serializer):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs['pk'])
        if self.get_queryset().exists():
            raise ValidationError(_('You have already liked this post.'))
        serializer.save(user=user, post=post)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError(_('You have no likes to remove for this post.'))


class CommentLikeCreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = CommentLikeSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        return CommentLike.objects.filter(comment=comment, user=user)

    def perform_create(self, serializer):
        user = self.request.user
        comment = Comment.objects.get(pk=self.kwargs['pk'])
        if self.get_queryset().exists():
            raise ValidationError(_('You have already liked this comment.'))
        serializer.save(user=user, comment=comment)

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError(_('You have no likes to remove for this comment.'))
    