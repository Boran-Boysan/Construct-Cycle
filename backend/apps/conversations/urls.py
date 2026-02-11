from django.urls import path
from . import views

app_name = 'conversations'

urlpatterns = [
    # Konuşmalar
    path('', views.ConversationListView.as_view(), name='conversation-list'),
    path('start/', views.ConversationStartView.as_view(), name='conversation-start'),
    path('<int:id>/', views.ConversationDetailView.as_view(), name='conversation-detail'),

    # Mesajlar
    path('send-message/', views.MessageSendView.as_view(), name='message-send'),
    path('<int:conversation_id>/messages/', views.ConversationMessagesView.as_view(), name='conversation-messages'),
    path('<int:conversation_id>/mark-read/', views.MarkAsReadView.as_view(), name='mark-read'),

    # Okunmamış mesaj sayısı
    path('unread-count/', views.UnreadCountView.as_view(), name='unread-count'),
]