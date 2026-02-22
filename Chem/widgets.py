from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        # Скрываем стандартное текстовое поле и добавляем контейнер для редактора
        html = super().render(name, value, attrs)
        jsme_html = f"""
        <div id="jsme_container_{name}" style="margin-bottom:10px;"></div>
        <script type="text/javascript" src="https://jsme-editor.github.io"></script>
        <script type="text/javascript">
            function jsmeOnLoad() {{
                var jsmeApplet = new JSME.JSApplet("jsme_container_{name}", "400px", "350px", {{
                    "options": "oldlook,nozoom"
                }});
                
                // Загружаем существующий SMILES из поля в редактор
                var startValue = document.getElementById("{attrs['id']}").value;
                if (startValue) {{
                    jsmeApplet.readGenericMolecularInput(startValue);
                }}

                // При каждом изменении в редакторе обновляем скрытое текстовое поле Django
                jsmeApplet.setCallBack("AfterStructureModified", function(event) {{
                    var smiles = jsmeApplet.smiles();
                    document.getElementById("{attrs['id']}").value = smiles;
                }});
            }}
        </script>
        """
        return mark_safe(html + jsme_html)
