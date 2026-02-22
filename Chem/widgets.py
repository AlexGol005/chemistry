from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    """
    Визуальный редактор молекул JSME для Django Admin.
    Работает без установки системных зависимостей.
    """
    def render(self, name, value, attrs=None, renderer=None):
        # 1. Генерируем стандартный HTML (скрытое текстовое поле)
        attrs = attrs or {}
        attrs['style'] = 'width: 100%; font-family: monospace; margin-top: 10px; background: #f8f8f8;'
        html = super().render(name, value, attrs)
        
        field_id = attrs.get('id')
        container_id = f"jsme_container_{name}"
        
        # 2. JS-код для вставки редактора
        # Используем CDN, но с проверкой протокола (//)
        jsme_script = f"""
        <div id="{container_id}" style="width:450px; height:300px; border:1px solid #79aec8; background:#fff;"></div>
        
        <script type="text/javascript" src="https://jsme-editor.github.io"></script>
        
        <script type="text/javascript">
            // Функция, которую JSME вызывает автоматически после загрузки
            function jsmeOnLoad() {{
                if (window.jsme_applet_{name}) return; // Защита от двойной инициализации

                window.jsme_applet_{name} = new JSApplet.JSApplet("{container_id}", "450px", "300px", {{
                    "options": "oldlook,nozoom"
                }});
                
                var inputField = document.getElementById("{field_id}");
                
                // Загружаем SMILES из базы в редактор при открытии
                if (inputField.value) {{
                    window.jsme_applet_{name}.readGenericMolecularInput(inputField.value);
                }}

                // При каждом изменении рисунка обновляем текстовое поле Django
                window.jsme_applet_{name}.setCallBack("AfterStructureModified", function(event) {{
                    var smiles = window.jsme_applet_{name}.smiles();
                    inputField.value = smiles;
                }});
            }}

            // Резервный механизм: если библиотека загрузилась, а функция не вызвалась
            var jsmeTimer_{name} = setInterval(function() {{
                if (typeof JSApplet !== 'undefined') {{
                    jsmeOnLoad();
                    clearInterval(jsmeTimer_{name});
                }}
            }}, 500);
        </script>
        
        <style>
            /* Стили для админки, чтобы поле выглядело аккуратно */
            #{field_id} {{ 
                display: block; 
                border: 1px dashed #ccc; 
                color: #666;
                height: 40px;
            }}
            .field-{name} .vLargeTextField {{ width: 460px !important; }}
        </style>
        """
        return mark_safe(html + jsme_script)
