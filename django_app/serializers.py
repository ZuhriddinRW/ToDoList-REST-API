from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import TodoItem, User


class UserSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = User
        fields = '__all__'


class TodoItemSerializer ( serializers.ModelSerializer ) :
    user = serializers.StringRelatedField ( read_only=True )

    class Meta :
        model = TodoItem
        fields = [
            'id',
            'user',
            'title',
            'description',
            'is_completed',
            'due_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_title(self, value) :
        if not value.strip () :
            raise serializers.ValidationError ( "Sarlavha bo'sh bo'lishi mumkin emas" )
        return value


class PhoneNumberSerializer ( serializers.Serializer ) :
    phone_number = serializers.CharField ( max_length=15, required=True )


class OTPVerifySerializer ( serializers.Serializer ) :
    phone_number = serializers.CharField ( max_length=15, required=True )
    otp_code = serializers.CharField ( max_length=6, required=True )


class LoginSerializer ( serializers.Serializer ) :
    phone_number = serializers.CharField ()
    password = serializers.CharField ( write_only=True )

    def validate(self, data) :
        phone_number = data.get ( 'phone_number' )
        password = data.get ( 'password' )

        if phone_number and password :
            user = authenticate ( phone_number=phone_number, password=password )

            if not user :
                raise serializers.ValidationError (
                    'Phone number or password is invalid'
                )

            if not user.is_active :
                raise serializers.ValidationError (
                    'User account is disabled'
                )

            data['user'] = user
            return data
        else :
            raise serializers.ValidationError (
                'Must include "phone number" and "password"'
            )