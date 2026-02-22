from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        # Получаем стандартный HTML для Textarea
        html = super().render(name, value, attrs)
        field_id = attrs['id']
        
        # Генерируем уникальный ID для контейнера редактора
        container_id = f"jsme_container_{name}"
        
        jsme_script = f"""
        <div id="{container_id}" style="border: 1px solid #ccc; margin-bottom: 10px;"></div>
        
        <!-- Загружаем JSME напрямую -->
        <script type="text/javascript" src="https://jsme-editor.github.io"></script>
        
        <script type="text/javascript">
            // Функция запуска редактора
            function startJsme() {{
                if (typeof JSME === 'undefined') {{
                    // Если библиотека еще не загружена, пробуем через 200мс
                    setTimeout(startJsme, 200);
                    return;
                }}
                
                var jsmeApplet = new JSME.JSApplet("{container_id}", "400px", "350px", {{
                    "options": "oldlook,nozoom"
                }});
                
                var hiddenField = document.getElementById("{field_id}");
                
                // Загружаем текущее значение из базы
                if (hiddenField.value) {{
                    jsmeApplet.readGenericMolecularInput(hiddenField.value);
                }}

                // Синхронизация: Редактор -> Текстовое поле
                jsmeApplet.setCallBack("AfterStructureModified", function(event) {{
                    var smiles = jsmeApplet.smiles();
                    hiddenField.value = smiles;
                }});
            }}

            // Запускаем при загрузке страницы
            if (document.readyState === "complete") {{
                startJsme();
            }} else {{
                window.addEventListener("load", startJsme);
            }}
        </script>
        <style>
            #{field_id} {{ display: block; width: 100%; margin-top: 5px; font-family: monospace; }}
        </style>
        """
        return mark_safe(html + jsme_script)
