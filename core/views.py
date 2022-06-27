from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .models import Profile
from .serializers import CreateUserSerializer, UserSerializer, LoginUserSerializer, ProfileSerializer


# Create your views here.


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, profile = serializer.save()
        user_profile = UserSerializer(user, context=self.get_serializer_context()).data
        profile = ProfileSerializer(profile, context=self.get_serializer_context()).data
        user_profile['birth_date'] = profile['birth_date']
        return Response({
            "key": AuthToken.objects.create(user)[1],
            "user": user_profile
        })


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        user_id = User.objects.get(username=user)
        user_profile = UserSerializer(user, context=self.get_serializer_context()).data
        profile = Profile.objects.get(user=user_id.id)
        profile = ProfileSerializer(profile, context=self.get_serializer_context()).data
        user_profile['birth_date'] = profile['birth_date']

        # login(request, user)
        return Response({
            "key": AuthToken.objects.create(user)[1],
            "user": user_profile
        })


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
