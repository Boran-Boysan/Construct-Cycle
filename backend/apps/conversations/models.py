
from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """
    Konuşma modeli - Alıcı ve satıcı arasındaki mesajlaşma
    """

    # Ürün (hangi ürün hakkında konuşuluyor)
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name="Ürün"
    )

    # Katılımcılar
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_conversations',
        verbose_name="Alıcı"
    )

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_conversations',
        verbose_name="Satıcı"
    )

    # Durum
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    # Tarihler
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Başlangıç Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Mesaj Tarihi")

    class Meta:
        db_table = 'conversations'
        verbose_name = "Konuşma"
        verbose_name_plural = "Konuşmalar"
        ordering = ['-updated_at']

        # Aynı ürün için aynı kullanıcılar arasında tek konuşma
        unique_together = [['product', 'buyer', 'seller']]

        indexes = [
            models.Index(fields=['buyer']),
            models.Index(fields=['seller']),
            models.Index(fields=['product']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self):
        return f"{self.buyer.email} ↔ {self.seller.email} - {self.product.name}"

    @property
    def last_message(self):
        """Son mesaj"""
        return self.messages.first()

    def get_unread_count(self, user):
        """Okunmamış mesaj sayısı"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """
    Mesaj modeli - Konuşmadaki tekil mesajlar
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Konuşma"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name="Gönderen"
    )

    # Mesaj içeriği
    message_text = models.TextField(verbose_name="Mesaj")

    # Durum
    is_read = models.BooleanField(default=False, verbose_name="Okundu mu?")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Okunma Zamanı")

    # Tarih
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderim Zamanı")

    class Meta:
        db_table = 'messages'
        verbose_name = "Mesaj"
        verbose_name_plural = "Mesajlar"
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=['conversation']),
            models.Index(fields=['sender']),
            models.Index(fields=['is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.sender.email}: {self.message_text[:50]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Konuşmanın updated_at'ini güncelle
        self.conversation.save()

    def mark_as_read(self):
        """Mesajı okundu olarak işaretle"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()