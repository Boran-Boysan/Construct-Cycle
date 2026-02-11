from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, ConversationListSerializer,
    MessageSerializer, MessageCreateSerializer,
    ConversationStartSerializer
)


@extend_schema(tags=['💬 Konuşmalar'])
class ConversationListView(generics.ListAPIView):
    """
    Konuşma Listesi

    Kullanıcının tüm konuşmalarını listeler.
    """
    serializer_class = ConversationListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Kullanıcının alıcı veya satıcı olduğu konuşmalar
        return Conversation.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('product', 'buyer', 'seller').prefetch_related('messages')


@extend_schema(tags=['💬 Konuşmalar'])
class ConversationDetailView(generics.RetrieveAPIView):
    """
    Konuşma Detayı

    Belirli bir konuşmanın detaylarını ve mesajlarını gösterir.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user

        # Sadece kendi konuşmalarını görebilir
        return Conversation.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related('product', 'buyer', 'seller').prefetch_related('messages__sender')

    def retrieve(self, request, *args, **kwargs):
        conversation = self.get_object()

        # Okunmamış mesajları okundu olarak işaretle
        unread_messages = conversation.messages.filter(
            is_read=False
        ).exclude(sender=request.user)

        for message in unread_messages:
            message.mark_as_read()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)


@extend_schema(tags=['💬 Konuşmalar'])
class ConversationStartView(generics.CreateAPIView):
    """
    Konuşma Başlat

    Ürün hakkında satıcıyla konuşma başlatır.
    """
    serializer_class = ConversationStartSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()

        return Response(
            ConversationSerializer(conversation, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['💬 Mesajlar'])
class MessageSendView(generics.CreateAPIView):
    """
    Mesaj Gönder

    Mevcut konuşmaya mesaj gönderir.
    """
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        return Response(
            MessageSerializer(message, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(tags=['💬 Mesajlar'])
class ConversationMessagesView(generics.ListAPIView):
    """
    Konuşma Mesajları

    Belirli bir konuşmanın tüm mesajlarını listeler.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        user = self.request.user

        # Konuşmaya erişim kontrolü
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id
        )

        # Kullanıcı bu konuşmada var mı?
        if user != conversation.buyer and user != conversation.seller:
            return Message.objects.none()

        # Mesajları getir (en yeniden eskiye)
        return Message.objects.filter(
            conversation=conversation
        ).select_related('sender').order_by('-created_at')


@extend_schema(tags=['💬 Mesajlar'])
class MarkAsReadView(APIView):
    """
    Mesajları Okundu Olarak İşaretle

    Konuşmadaki tüm okunmamış mesajları okundu yapar.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, conversation_id):
        user = request.user

        # Konuşmayı al
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id
        )

        # Kullanıcı bu konuşmada var mı?
        if user != conversation.buyer and user != conversation.seller:
            return Response(
                {'error': 'Bu konuşmaya erişim yetkiniz yok'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Okunmamış mesajları okundu yap
        unread_messages = conversation.messages.filter(
            is_read=False
        ).exclude(sender=user)

        count = 0
        for message in unread_messages:
            message.mark_as_read()
            count += 1

        return Response({
            'message': f'{count} mesaj okundu olarak işaretlendi'
        })


@extend_schema(tags=['💬 Konuşmalar'])
class UnreadCountView(APIView):
    """
    Okunmamış Mesaj Sayısı

    Kullanıcının toplam okunmamış mesaj sayısını döner.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Kullanıcının konuşmaları
        conversations = Conversation.objects.filter(
            Q(buyer=user) | Q(seller=user)
        )

        # Toplam okunmamış mesaj
        total_unread = 0
        for conversation in conversations:
            total_unread += conversation.get_unread_count(user)

        return Response({
            'total_unread': total_unread
        })