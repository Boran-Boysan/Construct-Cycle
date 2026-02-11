
# Django'nun yönetimsel görevler için komut satırı aracı.

import os # İşletim sistemi kütüphanesi
import sys # Pythonun kendisi ile konuşma kütüphanesi

def main(): # Amacı yönetim görevlerini çalıştırması.

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'construct_cycle_project.settings') # construct_cycle_project dosyasının ismi değişilirse değiştirilmesi lazım.

    try:
        from django.core.management import execute_from_command_line

    except ImportError as exc:

        raise ImportError(
            "Django import edilemedi. Django'nun kurulu olduğundan ve "
            "PYTHONPATH environment değişkeninizde mevcut olduğundan emin misiniz? "
            "Sanal ortamı (virtual environment) aktifleştirmeyi unuttunuz mu?"
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

"""
Bu dosya Django projesinin komut satırı üzerinden yönetilmesini sağlar.
os.environ ile hangi Django ayar dosyasının (settings.py) kullanılacağı belirlenir.
execute_from_command_line, terminalden gelen komutları Django'ya iletir.
sys.argv, runserver, migrate gibi komutları Python üzerinden Django'ya aktarır.
Tüm `python manage.py ...` komutları bu dosya aracılığıyla çalıştırılır.
"""
