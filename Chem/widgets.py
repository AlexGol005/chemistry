from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        # Скрываем стандартное текстовое поле и добавляем контейнер для JSME
        html = super().render(name, value, attrs, renderer)
        jsme_html = f"""
        <div id="jsme_admin_container" style="margin-bottom:10px;"></div>
        <script type="text/javascript" src="https://jsme-editor.github.io"></script>
        <script>
            var jsmeApplet;
            function jsmeOnLoad() {{
                jsmeApplet = new JSMe("jsme_admin_container", "500px", "400px");
                // Если в поле уже есть SMILES (редактирование), загружаем его в редактор
                var val = document.getElementById("{attrs['id']}").value;
                if (val) {{
                    jsmeApplet.readGenericMolecularInput(val);
                }}
                
                // При каждом изменении в редакторе обновляем скрытое текстовое поле
                jsmeApplet.setCallBack("AfterStructureModified", function(event) {{
                    var smiles = event.src.smiles();
                    document.getElementById("{attrs['id']}").value = smiles;
                }});
            }}
        </script>
        """
        return mark_safe(jsme_html + html)
