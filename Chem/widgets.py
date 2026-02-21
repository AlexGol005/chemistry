from django import forms
from django.utils.safestring import mark_safe

class JSMEWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        # Оставляем поле видимым для отладки или скрываем через класс
        attrs['style'] = 'width: 100%; height: 50px; margin-top: 10px;'
        html = super().render(name, value, attrs, renderer)
        
        # Генерируем уникальный ID для контейнера редактора
        field_id = attrs.get('id')
        
        jsme_html = f"""
        <div id="jsme_container_{field_id}" style="border: 1px solid #ccc; background: #fff;"></div>
        
        <script type="text/javascript" src="https://jsme-editor.github.io"></script>
        
        <script>
            function jsmeOnLoad() {{
                // Инициализация редактора
                var jsmeApplet = new JSMe("jsme_container_{field_id}", "500px", "350px");
                
                var inputField = document.getElementById("{field_id}");
                
                // Если в базе уже есть SMILES, отрисовываем его
                if (inputField.value) {{
                    jsmeApplet.readGenericMolecularInput(inputField.value);
                }}

                // При каждом изменении в редакторе обновляем текстовое поле
                jsmeApplet.setCallBack("AfterStructureModified", function(event) {{
                    var smiles = event.src.smiles();
                    inputField.value = smiles;
                }});
            }}
        </script>
        """
        return mark_safe(jsme_html + html)
