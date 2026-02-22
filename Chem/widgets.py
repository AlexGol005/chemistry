from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        # Стандартное поле (оставляем видимым для отладки, потом скроем)
        html = super().render(name, value, attrs)
        field_id = attrs['id']
        container_id = f"jsme_container_{name}"
        
        jsme_script = f"""
        <div id="{container_id}" style="width:400px; height:300px; border:1px solid #79aec8; margin-bottom:10px;"></div>
        
        <script type="text/javascript" src="https://jsme-editor.github.io"></script>
        
        <script type="text/javascript">
            // Функция инициализации
            function jsmeOnLoad() {{
                // JSME автоматически ищет эту функцию при загрузке
                var applet = new JSApplet.JSApplet("{container_id}", "400px", "300px", {{
                    "options": "oldlook,nozoom"
                }});
                
                var input = document.getElementById("{field_id}");
                
                // Загружаем данные из поля в редактор
                if (input.value) {{
                    applet.readGenericMolecularInput(input.value);
                }}

                // При изменении в редакторе — пишем в текстовое поле
                applet.setCallBack("AfterStructureModified", function(event) {{
                    var smiles = applet.smiles();
                    input.value = smiles;
                }});
            }}
            
            // Если автоматический вызов не сработал, пробуем запустить вручную через интервал
            var checkJSME = setInterval(function() {{
                if (typeof JSApplet !== 'undefined') {{
                    jsmeOnLoad();
                    clearInterval(checkJSME);
                }}
            }}, 500);
        </script>
        <style>
            #{field_id} {{ 
                width: 400px !important; 
                display: block; 
                margin-top: 10px; 
                font-size: 11px;
                color: #666;
            }}
            .vLargeTextField {{ width: 400px !important; }}
        </style>
        """
        return mark_safe(html + jsme_script)
