from django.contrib.auth import authenticate
from django.core import exceptions
from rest_framework import serializers
from django.contrib.auth.models import User
import django.contrib.auth.password_validation as validators
from rest_framework.fields import DateField
from rest_framework.validators import UniqueValidator
from .models import Profile


class CreateUserSerializer(serializers.ModelSerializer):
    birth_date = DateField()
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password2', 'birth_date')
        extra_kwargs = {'username': {'required': True},
                        'email': {'required': True, 'validators': [UniqueValidator(queryset=User.objects.all())]},
                        'password': {'write_only': True, 'required': True},
                        'password2': {'write_only': True, 'required': True},
                        'birth_date': {'required': True}}

    def validate_password(self, data):
        # check the password is strong
        password = data
        errors = dict()
        try:
            # validate the password and catch the exception
            validators.validate_password(password=password)

        # the exception raised here is different from serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super(CreateUserSerializer, self).validate(data)

    def validate(self, data):
        # check the 2 password is matching
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Password didn't match")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'],
                                        validated_data['password'])
        profile = Profile.objects.create(user=user, birth_date=validated_data['birth_date'])

        return user, profile


class ProfileSerializer(serializers.ModelSerializer):
    birth_date = DateField()

    class Meta:
        model = Profile
        fields = ['birth_date']
        extra_kwargs = {'birth_date': {'required': True}}


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)
        try:
            user = User.objects.get(email=email)
            user_auth = authenticate(username=user.username, password=password)
            print(user_auth)
            if user.check_password(password):

                return user
        except exceptions.ValidationError:
            raise serializers.ValidationError('A user with this email and password is not found.')
