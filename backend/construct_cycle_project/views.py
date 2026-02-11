from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages, admin
from django.apps import apps
from django.utils.html import strip_tags


@staff_member_required
def bulk_delete_view(request, app_label=None, model_name=None):
    """Toplu silme sayfası - Tüm modeller tek sayfada"""

    # POST işlemi - silme
    if request.method == 'POST':
        deleted_total = 0
        for key, values in request.POST.lists():
            if key.startswith('selected_') and key != 'csrfmiddlewaretoken':
                # key formatı: selected_appname_modelname
                parts = key.replace('selected_', '').rsplit('_', 1)
                if len(parts) == 2:
                    app, model = parts
                    try:
                        model_class = apps.get_model(app, model)
                        count = model_class.objects.filter(pk__in=values).delete()[0]
                        deleted_total += count
                    except:
                        pass

        if deleted_total > 0:
            messages.success(request, f'Toplam {deleted_total} kayıt başarıyla silindi.')
        else:
            messages.warning(request, 'Silmek için en az bir kayıt seçmelisiniz.')

        return redirect('admin_bulk_delete_all')

    # Tüm kayıtlı modelleri al
    all_models_data = []

    for model, model_admin in admin.site._registry.items():
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        queryset = model.objects.all()

        # Boş modelleri atla (isteğe bağlı - yoruma alabilirsin)
        # if not queryset.exists():
        #     continue

        # List display alanlarını al
        list_display = getattr(model_admin, 'list_display', ('__str__',))
        if list_display == ('__str__',):
            list_display = ['__str__']

        # Sütun başlıkları
        headers = []
        for field_name in list_display:
            if field_name == '__str__':
                headers.append(str(model._meta.verbose_name))
            elif hasattr(model_admin, field_name):
                method = getattr(model_admin, field_name)
                headers.append(getattr(method, 'short_description', field_name))
            else:
                try:
                    field = model._meta.get_field(field_name)
                    headers.append(str(field.verbose_name))
                except:
                    headers.append(field_name)

        # Satır verileri
        rows = []
        for obj in queryset:
            row_data = {'id': obj.pk, 'fields': []}
            for field_name in list_display:
                if field_name == '__str__':
                    value = str(obj)
                elif hasattr(model_admin, field_name):
                    method = getattr(model_admin, field_name)
                    try:
                        value = method(obj)
                        if isinstance(value, str) and '<' in value:
                            value = strip_tags(value)
                    except:
                        value = '-'
                elif hasattr(obj, field_name):
                    value = getattr(obj, field_name)
                    if callable(value):
                        value = value()
                else:
                    value = '-'
                row_data['fields'].append(value)
            rows.append(row_data)

        all_models_data.append({
            'app_label': app_label,
            'model_name': model_name,
            'verbose_name': model._meta.verbose_name,
            'verbose_name_plural': model._meta.verbose_name_plural,
            'headers': headers,
            'rows': rows,
            'count': queryset.count(),
            'checkbox_name': f'selected_{app_label}_{model_name}',
        })

    # App label'a göre grupla
    apps_grouped = {}
    for model_data in all_models_data:
        app = model_data['app_label']
        if app not in apps_grouped:
            apps_grouped[app] = []
        apps_grouped[app].append(model_data)

    context = {
        'title': 'Toplu Silme - Tüm Modeller',
        'apps_grouped': apps_grouped,
        'all_models_data': all_models_data,
        'has_permission': True,
        'site_header': 'ConstructCycle Yönetim Paneli',
    }

    return render(request, 'admin/bulk_delete.html', context)