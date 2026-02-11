from django.db import models
from django.conf import settings
import uuid

class Report(models.Model):
    TARGET_TYPE_CHOICES = [('product', 'Urun'), ('user', 'Kullanici'), ('review', 'Yorum')]
    REASON_CHOICES = [('scam', 'Dolandiricilik'), ('fake', 'Sahte'), ('spam', 'Spam'), ('other', 'Diger')]
    STATUS_CHOICES = [('pending', 'Beklemede'), ('resolved', 'Cozuldu'), ('dismissed', 'Reddedildi')]

    report_number = models.CharField(max_length=50, unique=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    target_id = models.PositiveIntegerField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports'

    def save(self, *args, **kwargs):
        if not self.report_number:
            self.report_number = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class UserWarning(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='warnings')
    reason = models.TextField()
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='issued_warnings')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_warnings'

class UserBan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bans')
    reason = models.TextField()
    banned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='issued_bans')
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_bans'
