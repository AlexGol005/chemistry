from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    class Media:
        # Подгружаем JSME через механизм медиа-файлов Django
        js = ('https://jsme-editor.github.io',)

    def render(self, name, value, attrs=None, renderer=None):
        # Обычное текстовое поле (будет скрыто)
        html = super().render(name, value, attrs)
        field_id = attrs['id']
        container_id = f"jsme_container_{name}"
        
        # Скрипт инициализации с проверкой готовности объекта JSME
        jsme_init = f"""
        <div id="{container_id}" style="width: 400px; height: 350px; border: 1px solid #ccc;"></div>
        <script type="text/javascript">
            function initJSME_{name}() {{
                // Ждем появления глобального объекта JSME (он создается асинхронно библиотекой)
                if (typeof JSApplet === 'undefined') {{
                    setTimeout(initJSME_{name}, 200);
                    return;
                }}
                
                var applet = new JSApplet.JSApplet("{container_id}", "400px", "350px", {{
                    "options": "oldlook,nozoom"
                }});

                var inputField = document.getElementById("{field_id}");
                
                // Загружаем данные из БД при старте
                if (inputField.value) {{
                    applet.readGenericMolecularInput(inputField.value);
                }}

                // При изменении структуры обновляем скрытое поле
                applet.setCallBack("AfterStructureModified", function(event) {{
                    inputField.value = applet.smiles();
                }});
            }}
            
            // Запуск после полной загрузки страницы
            window.addEventListener('load', initJSME_{name});
        </script>
        <style>
            #{field_id} {{ display: none; }} /* Скрываем текстовое поле, оставляя только редактор */
        </style>
        """
        return mark_safe(html + jsme_init)
