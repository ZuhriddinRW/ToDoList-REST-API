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