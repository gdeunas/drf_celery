# users/views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from users.serializers import UserProfileSerializer, UserSerializer

from .models import Payment
from .serializers import PaymentSerializer


class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Эндпоинт для просмотра и редактирования профиля пользователя.
    Принимает PUT и PATCH запросы для обновления по id.
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    filterset_fields = ("paid_course", "paid_lesson", "payment_method")

    ordering_fields = ("payment_date",)


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
