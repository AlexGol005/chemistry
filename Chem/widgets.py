{% load static %}
<!-- 1. Контейнер, где появится сам редактор -->
<div id="jsme_container_{{ widget.attrs.id }}" style="border: 1px solid #444; margin-bottom: 10px;"></div>

<!-- 2. Поле, куда Django запишет результат (сделаем его видимым для контроля) -->
<input type="text" name="{{ widget.name }}" id="{{ widget.attrs.id }}" 
       value="{{ widget.value|default:'' }}" 
       style="width: 100%; background: #f0f0f0; font-family: monospace;" readonly>

<!-- 3. Подключение скрипта из вашей папки static/jsme/ -->
<script type="text/javascript" src="{% static 'jsme/jsme.nocache.js' %}"></script>

<script type="text/javascript">
    // Эта функция запустится сама, когда JSME загрузится
    function jsmeOnLoad() {
        var inputId = "{{ widget.attrs.id }}";
        var inputField = document.getElementById(inputId);
        
        // Создаем редактор (ID контейнера, Ширина, Высота)
        // Опция "oldLook" делает интерфейс классическим, "paste" разрешает вставку
        var jsmeApplet = new JSApplet.JSME("jsme_container_" + inputId, "100%", "400px", {
            "options": "oldLook,paste"
        });

        // Если в базе уже есть SMILES, рисуем молекулу при открытии страницы
        if (inputField.value) {
            jsmeApplet.readGenericMolecularInput(inputField.value);
        }

        // ГЛАВНОЕ: При каждом изменении рисунка обновляем текст в поле Django
        jsmeApplet.setCallBack("AfterStructureModified", function(jsme) {
            var smiles = jsme.smiles();
            inputField.value = smiles;
        });
    }
</script>
