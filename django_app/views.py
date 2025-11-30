from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import TodoItem
from .serializers import TodoItemSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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