from django.contrib.sitemaps import Sitemap
from django.apps import apps
from django.urls import reverse

class AutoDjangoSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        dynamic_items = []
        
        for model in apps.get_models():
            if hasattr(model, 'get_absolute_url'):
                # Пропускаем системные приложения
                if model._meta.app_label in ['admin', 'auth', 'contenttypes', 'sessions']:
                    continue
                    
                # Проверяем каждую запись отдельно
                for obj in model.objects.all():
                    try:
                        # Пробуем сгенерировать URL. Если упадет — запись пропустим!
                        obj.get_absolute_url()
                        dynamic_items.append(obj)
                    except Exception:
                        # Если reverse() выдает ошибку (как measureequipmentcomm), Django просто идет дальше
                        pass
                        
        return dynamic_items
