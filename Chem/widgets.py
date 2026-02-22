from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs)
        field_id = attrs['id']
        container_id = f"jsme_container_{name}"
        
        # Путь к вашему локальному файлу в папке static/js/
        local_js_path = "/static/js/jsme.nocache.js"
        
        jsme_script = f"""
        <div id="{container_id}" style="width:450px; height:300px; border:1px solid #79aec8; background:#fff; margin-bottom:10px;"></div>
        
        <script type="text/javascript">
            // Загружаем скрипт только один раз на страницу
            if (!window.jsme_script_loaded) {{
                var script = document.createElement('script');
                script.src = "{local_js_path}";
                document.head.appendChild(script);
                window.jsme_script_loaded = true;
            }}

            function initJsme_{name}() {{
                if (typeof JSApplet === 'undefined') {{
                    setTimeout(initJsme_{name}, 300);
                    return;
                }}
                var applet = new JSApplet.JSApplet("{container_id}", "450px", "300px", {{
                    "options": "oldlook,nozoom"
                }});
                var input = document.getElementById("{field_id}");
                if (input.value) applet.readGenericMolecularInput(input.value);
                applet.setCallBack("AfterStructureModified", function() {{
                    input.value = applet.smiles();
                }});
            }}
            initJsme_{name}();
        </script>
        <style>
            #{field_id} {{ display: block; height: 30px; border: 1px dashed #ccc; width: 450px; color: #999; font-size: 10px; }}
        </style>
        """
        return mark_safe(html + jsme_script)
