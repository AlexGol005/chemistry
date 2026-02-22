from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs)
        field_id = attrs['id']
        container_id = f"jsme_container_{name}"
        
        # Генерируем JS-код
        jsme_script = f"""
        <div id="{container_id}" style="width:450px; height:300px; border:1px solid #79aec8; background:#fff; margin-bottom:10px;"></div>
        
        <script type="text/javascript" src="/static/js/jsme.nocache.js"></script>
        
        <script type="text/javascript">
            function tryInitJSME_{name}() {{
                // JSME создает глобальные объекты JSApplet или JME
                if (typeof JSApplet !== 'undefined') {{
                    var applet = new JSApplet.JSApplet("{container_id}", "450px", "300px", {{
                        "options": "oldlook,nozoom"
                    }});
                    
                    var input = document.getElementById("{field_id}");
                    if (input.value) {{
                        applet.readGenericMolecularInput(input.value);
                    }}

                    applet.setCallBack("AfterStructureModified", function() {{
                        input.value = applet.smiles();
                    }});
                    console.log("JSME Initialized for {name}");
                }} else {{
                    // Если еще не загрузилось, пробуем через 300мс
                    setTimeout(tryInitJSME_{name}, 300);
                }}
            }}
            
            // Запуск
            tryInitJSME_{name}();
        </script>
        <style>
            #{field_id} {{ display: block; height: 35px; border: 1px dashed #ccc; width: 450px; font-size: 11px; }}
        </style>
        """
        return mark_safe(html + jsme_script)
