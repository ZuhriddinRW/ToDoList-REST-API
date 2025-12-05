import random
from django.contrib.auth import get_user_model
from django.core import cache
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from .make_token import get_tokens_for_user
from .models import TodoItem, OTPVerification
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from datetime import timedelta


class TodoItemViewSet ( ModelViewSet ) :
    serializer_class = TodoItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) :
        return TodoItem.objects.filter ( user=self.request.user )

    def perform_create(self, serializer) :
        serializer.save ( user=self.request.user )

    @swagger_auto_schema (
        method='get',
        responses={200 : TodoItemSerializer ( many=True )}
    )
    @action ( detail=False, methods=['GET'] )
    def completed(self, request, *args, **kwargs) :
        todos = self.get_queryset ().filter ( is_completed=True )
        serializer = self.get_serializer ( todos, many=True )
        return Response ( serializer.data )

    @swagger_auto_schema (
        method='get',
        responses={200 : TodoItemSerializer ( many=True )}
    )
    @action ( detail=False, methods=['GET'] )
    def pending(self, request, *args, **kwargs) :
        todos = self.get_queryset ().filter ( is_completed=False )
        serializer = self.get_serializer ( todos, many=True )
        return Response ( serializer.data )

    @swagger_auto_schema (
        method='post',
        responses={200 : "Completed items were deleted"}
    )
    @action ( detail=False, methods=['POST'] )
    def clear_completed(self, request, *args, **kwargs) :
        deleted_count = self.get_queryset ().filter ( is_completed=True ).delete ()[0]
        return Response ( {
            "message" : f"{deleted_count} completed tasks were deleted"
        } )


class SendOTPView ( generics.GenericAPIView ) :
    permission_classes = [AllowAny]
    serializer_class = PhoneNumberSerializer

    def post(self, request, *args, **kwargs) :
        serializer = self.get_serializer ( data=request.data )
        serializer.is_valid ( raise_exception=True )

        phone_number = serializer.validated_data['phone_number']

        otp_code = str ( random.randint ( 100000, 999999 ) )

        OTPVerification.objects.create (
            phone_number=phone_number,
            otp_code=otp_code
        )

        print ( f"\n{'=' * 50}" )
        print ( f"Phone Number: {phone_number}" )
        print ( f"OTP code: {otp_code}" )
        print ( f"{'=' * 50}\n" )

        return Response ( {
            'success' : True,
            'message' : 'OTP code was sent!',
            'phone_number' : phone_number,
        }, status=status.HTTP_200_OK )


class VerifyOTPView ( generics.GenericAPIView ) :
    permission_classes = [AllowAny]
    serializer_class = OTPVerifySerializer

    def post(self, request, *args, **kwargs) :
        serializer = self.get_serializer ( data=request.data )
        serializer.is_valid ( raise_exception=True )

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

        time_threshold = timezone.now () - timedelta ( minutes=5 )

        try :
            otp_obj = OTPVerification.objects.filter (
                phone_number=phone_number,
                otp_code=otp_code,
                is_verified=False,
                created_at__gte=time_threshold
            ).latest ( 'created_at' )

            otp_obj.is_verified = True
            otp_obj.save ()

            User = get_user_model ()

            user, created = User.objects.get_or_create (
                phone_number=phone_number,
                defaults={'phone_number' : phone_number}
            )
            user.is_phone_verified = True
            user.save ()

            refresh = RefreshToken.for_user ( user )

            return Response ( {
                'success' : True,
                'message' : 'Phone number confirmed!',
                'user' : {
                    'id' : user.id,
                    'phone_number' : user.phone_number,
                    'username' : user.username,
                },
                'tokens' : {
                    'refresh' : str ( refresh ),
                    'access' : str ( refresh.access_token ),
                }
            }, status=status.HTTP_200_OK )

        except OTPVerification.DoesNotExist :
            return Response ( {
                'success' : False,
                'error' : 'Wrong or expired OTP'
            }, status=status.HTTP_400_BAD_REQUEST )


class LoginUser ( APIView ) :
    permission_classes = [AllowAny]

    @swagger_auto_schema ( request_body=LoginSerializer )
    def post(self, request) :
        serializer = LoginSerializer ( data=request.data )
        serializer.is_valid ( raise_exception=True )
        user = serializer.validated_data.get ( "user" )

        token = get_tokens_for_user ( user )

        return Response ( data=token, status=status.HTTP_200_OK )

class UserRegister(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            phone = serializer.validated_data['phone_number']
            serializer.save(is_active=True)
            return Response({'status':True,'massage': "Registerdan otildi"},status.HTTP_200_OK)
        else:
            return Response({'status':False,'massage':serializer.errors},status=status.HTTP_400_BAD_REQUEST)