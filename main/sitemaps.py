from django.contrib.sitemaps import Sitemap
from django.apps import apps

class AutoDjangoSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        dynamic_items = []
        
        # 1. Пробегаемся по всем моделям вашего проекта
        for model in apps.get_models():
            # 2. Проверяем, настроил ли программист для модели страницу (get_absolute_url)
            # Если у модели нет своего адреса, Django её просто пропустит!
            if hasattr(model, 'get_absolute_url'):
                try:
                    # 3. Забираем все записи из этой модели в карту сайта
                    # Исключаем технические модели Яндекса/Админки, если они вдруг попадутся
                    if not model._meta.app_label in ['admin', 'auth', 'contenttypes', 'sessions']:
                        dynamic_items.extend(list(model.objects.all()))
                except Exception:
                    pass
                    
        return dynamic_items
