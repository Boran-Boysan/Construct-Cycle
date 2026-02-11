"""
Email Utilities
apps/accounts/utils.py
"""
from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user, verification_code):
    """Kullanıcıya email aktivasyon kodu gönder"""
    subject = 'ConstructCycle - Email Doğrulama Kodunuz'

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #264653 0%, #2A9D8F 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .code-box {{ background: white; border: 2px solid #FF6B35; padding: 20px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #FF6B35; margin: 20px 0; border-radius: 8px; }}
            .info {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ConstructCycle</h1>
            <p>İnşaat Malzemeleri Platformu</p>
        </div>
        <div class="content">
            <h2>Merhaba {user.first_name or user.email}!</h2>
            <p>ConstructCycle'a hoş geldiniz! Email adresinizi doğrulamak için aşağıdaki kodu kullanın:</p>
            <div class="code-box">{verification_code.code}</div>
            <div class="info"><strong>Önemli:</strong> Bu kod <strong>15 dakika</strong> süreyle geçerlidir.</div>
            <p>Eğer bu hesabı siz oluşturmadıysanız, bu emaili görmezden gelebilirsiniz.</p>
        </div>
        <div class="footer"><p>&copy; 2024 ConstructCycle - Tüm hakları saklıdır</p></div>
    </body>
    </html>
    """

    plain_message = f"""ConstructCycle - Email Doğrulama
Merhaba {user.first_name or user.email}!
DOĞRULAMA KODU: {verification_code.code}
Bu kod 15 dakika süreyle geçerlidir.
© 2024 ConstructCycle"""

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email gönderim hatası: {e}")
        return False


def send_activation_success_email(user):
    """Email doğrulandıktan sonra hesap aktif maili gönder"""
    subject = 'ConstructCycle - Hesabınız Aktif Edildi!'
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:8080')

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .success-badge {{ background: #d1fae5; border: 2px solid #10b981; color: #065f46; padding: 15px 25px; text-align: center; font-size: 18px; font-weight: bold; margin: 20px 0; border-radius: 8px; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #FF6B35, #e05a2b); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Hesabınız Aktif!</h1>
            <p>Email doğrulamanız başarıyla tamamlandı</p>
        </div>
        <div class="content">
            <h2>Tebrikler {user.first_name or user.email}!</h2>
            <div class="success-badge">&#10004; Email adresiniz doğrulandı ve hesabınız aktif edildi</div>
            <p>Artık ConstructCycle'ın tüm özelliklerinden yararlanabilirsiniz:</p>
            <ul>
                <li>Binlerce inşaat malzemesine erişim</li>
                <li>Güvenli ödeme sistemi</li>
                <li>Hızlı teslimat</li>
                <li>Satıcılarla doğrudan iletişim</li>
            </ul>
            <center><a href="{frontend_url}" class="button">Alışverişe Başla</a></center>
        </div>
        <div class="footer"><p>&copy; 2024 ConstructCycle - Tüm hakları saklıdır</p></div>
    </body>
    </html>
    """

    plain_message = f"""Tebrikler {user.first_name or user.email}!
Email adresiniz doğrulandı ve hesabınız aktif edildi.
Alışverişe başlamak için: {frontend_url}
© 2024 ConstructCycle"""

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Aktivasyon email hatası: {e}")
        return False


# ✅ Geriye dönük uyumluluk - eski isimle de çağrılabilsin
send_welcome_email = send_activation_success_email