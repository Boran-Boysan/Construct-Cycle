
"""
Bu dosya Django’daki 'accounts' uygulamasının yapılandırma (AppConfig) dosyasıdır.
Django bu sınıfı kullanarak uygulamayı nasıl tanıyacağını ve yöneteceğini bilir.
"""

from django.apps import AppConfig # Django’daki her uygulama için kullanılan temel yapılandırma sınıfı


class AccountsConfig(AppConfig):

    """
    Bu sınıf, 'apps.accounts' uygulamasının Django içindeki tanımını yapar.
    Django, bu ayarları admin paneli, migration’lar ve uygulama kaydı için kullanır.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Kullanıcılar ve Kimlik Doğrulama'