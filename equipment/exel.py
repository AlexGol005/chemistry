"""
Модуль проекта LabJournal, приложения equipment.
Приложение equipment это обширное приложение, включает все про лабораторное оборудование и лабораторные помещения
Данный модуль exel.py выводит представления для выгрузки данных в формате exel.
Список блоков:
блок 1 блок получения констант
блок 2 блок стили  для стилей полей документа exel
блок 3 - выгрузка данных в формате ексель (вначале блока идет общий класс base_planreport_xls, который наследуется частными классами)
блок 4 - шаблоны для массовой загрузки приборов
блок 5 - нестандартные exel выгрузки (протоколы верификации, карточка, этикетки) 
блок 6 - ТОИР 
блок 7 - график поверки и формы для паспорта лаборатории
"""


import xlwt
import pytils.translit
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse, request
from django.db.models import Max, Q, Value, CharField, Count, Sum, Exists
from django.db.models.functions import Concat, Substr 
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView, UpdateView
from xlwt import Alignment, Borders

from equipment.constants import servicedesc0
from equipment.forms import*
from equipment.models import*
from formstandart import YearForm
from functstandart import get_dateformat
from users.models import Profile, Company

URL = 'equipment'
now = date.today()



def get_affirmation(model, request):
        company = Company.objects.get(userid=request.user.profile.userid)
        affirmation = f'УТВЕРЖДАЮ \n{company.direktor_position}\n{company.name}\n____________/{company.direktor_name}/\n«__» ________20__ г.'
        return affirmation

def get_author(Company, request):
        company = Company.objects.get(userid=request.user.profile.userid)
        author = f'Разработал: \n{get_company(Company, request).manager_position} _____________ /{get_company(Company, request).manager_name}/'
        return author

# блок 1
# блок получения констант для блока 1 и блока 2

# для фильтрации кверисетов для выгрузок ексель. Так как нужно выбирать актуальные (последниие)
# поверки/аттестации из их таблиц и подставлять их в таблицы СИ и ИО, при этом не теряя остальные поля,
# поэтому просто группировка не подходит

get_id_room = Roomschange.objects.select_related('equipment').values('equipment'). \
        annotate(id_actual=Max('id')).values('id_actual')
list_ = list(get_id_room)
setroom = []
for n in list_:
    setroom.append(n.get('id_actual'))

get_id_person = Personchange.objects.select_related('equipment').values('equipment'). \
        annotate(id_actual=Max('id')).values('id_actual')
list_ = list(get_id_person)
setperson = []
for n in list_:
    setperson.append(n.get('id_actual'))

get_id_verification = Verificationequipment.objects.select_related('equipmentSM').values('equipmentSM'). \
    annotate(id_actual=Max('id')).values('id_actual')
list_ = list(get_id_verification)
setver = []
for n in list_:
    setver.append(n.get('id_actual'))

get_id_attestation = Attestationequipment.objects.select_related('equipmentSM').values('equipmentSM'). \
    annotate(id_actual=Max('id')).values('id_actual')
list_ = list(get_id_attestation)
setatt = []
for n in list_:
    setatt.append(n.get('id_actual'))


# для для фильтрации из базы данных по ID компании (userid  или pointer)
# ruser=rquest.user.profile.userid






# блок 2
# блок стили
size = 11
# al10 выравнивание по центру по горизонтали и по вертикали, обтекание wrap тип 1
alg_hc_vc_w1 = Alignment()
alg_hc_vc_w1.horz = Alignment.HORZ_CENTER
alg_hc_vc_w1.vert = Alignment.VERT_CENTER
alg_hc_vc_w1.wrap = 1

# обкновенные границы ячеек
b1 = Borders()
b1.left = 1
b1.right = 1
b1.top = 1
b1.bottom = 1


# кажется двойные границы ячеек
b2 = Borders()
b2.left = 6
b2.right = 6
b2.bottom = 6
b2.top = 6

# style_bold_borders  жирным шрифтом, с границами ячеек
style_bold_borders = xlwt.XFStyle()
style_bold_borders.font.bold = True
style_bold_borders.font.name = 'Times New Roman'
style_bold_borders.borders = b1
style_bold_borders.alignment = alg_hc_vc_w1

# style_bold_borders_blue  жирным шрифтом, с границами ячеек
style_bold_borders_blue = xlwt.XFStyle()
style_bold_borders_blue.font.bold = True
style_bold_borders_blue.font.name = 'Times New Roman'
style_bold_borders_blue.borders = b1
style_bold_borders_blue.alignment = alg_hc_vc_w1
style_bold_borders_blue.font.height = 20 * size
style_bold_borders_blue.font.colour_index = 32

# style_plain обычные ячейки, с границами ячеек
style_plain = xlwt.XFStyle()
style_plain.font.name = 'Times New Roman'
style_plain.borders = b1
style_plain.alignment = alg_hc_vc_w1
style_plain.font.height = 20 * size

# style_plain_textf обычные ячейки, с границами ячеек формат текстовый
style_plain_textf = xlwt.XFStyle()
style_plain_textf.font.name = 'Times New Roman'
style_plain_textf.borders = b1
style_plain_textf.alignment = alg_hc_vc_w1
style_plain_textf.font.height = 20 * size
style_plain_textf.num_format_str = '0'


# style_date обычные ячейки с датами, с границами ячеек
style_date = xlwt.XFStyle()
style_date.font.name = 'Times New Roman'
style_date.borders = b1
style_date.alignment = alg_hc_vc_w1
style_date.num_format_str = 'DD.MM.YYYY г'
style_date.font.height = 20 * size


al1 = Alignment()
al1.horz = Alignment.HORZ_CENTER
al1.vert = Alignment.VERT_CENTER

al2 = Alignment()
al2.horz = Alignment.HORZ_RIGHT
al2.vert = Alignment.VERT_CENTER

al20 = Alignment()
al20.horz = Alignment.HORZ_RIGHT
al20.vert = Alignment.VERT_CENTER
al20.wrap = 1

al3 = Alignment()
al3.horz = Alignment.HORZ_LEFT
al3.vert = Alignment.VERT_CENTER
al3.wrap = 1

al100 = Alignment()
al100.horz = Alignment.HORZ_CENTER
al100.vert = Alignment.VERT_CENTER
al100.rota = Alignment.ROTATION_STACKED


# обычные ячейки, с границами ячеек повернут на 90 градусов
style_plain_90 = xlwt.XFStyle()
style_plain_90.font.name = 'Times New Roman'
style_plain_90.font.height = 20 * size
style_plain_90.borders = b1
style_plain_90.alignment = al100

xlwt.easyxf('align: rotation 90')

# обычные ячейки, с толстыми границами ячеек
style_plain_bb = xlwt.XFStyle()
style_plain_bb.font.name = 'Times New Roman'
style_plain_bb.font.height = 20 * size
style_plain_bb.borders = b2
style_plain_bb.alignment = alg_hc_vc_w1

# обычные ячейки, с границами ячеек, c форматом чисел '0.00'  == style4
style_2dp = xlwt.XFStyle()
style_2dp.font.name = 'Times New Roman'
style_2dp.font.height = 20 * size
style_2dp.borders = b1
style_2dp.alignment = al1
style_2dp.num_format_str = '0.00'

# обычные ячейки, с границами ячеек, c форматом чисел '0.00000'  == style5
style_5dp = xlwt.XFStyle()
style_5dp.font.name = 'Times New Roman'
style_5dp.font.height = 20 * size
style_5dp.borders = b1
style_5dp.alignment = al1
style_5dp.num_format_str = '0.00000'

# обычные ячейки, с границами ячеек, c форматом чисел '0.0000'
style_4dp = xlwt.XFStyle()
style_4dp.font.name = 'Times New Roman'
style_4dp.font.height = 20 * size
style_4dp.borders = b1
style_4dp.alignment = al1
style_4dp.num_format_str = '0.0000'

# обычные ячейки, без границ  == style6
style_plain_nobor = xlwt.XFStyle()
style_plain_nobor.font.name = 'Times New Roman'
style_plain_nobor.font.height = 20 * size
style_plain_nobor.alignment = alg_hc_vc_w1

# обычные ячейки, без границ  жирный шрифт размер больше на 1
style_plain_nobor_bold = xlwt.XFStyle()
style_plain_nobor_bold.font.bold = True
style_plain_nobor_bold.font.name = 'Times New Roman'
style_plain_nobor_bold.font.height = 20 * (size + 1)
style_plain_nobor_bold.alignment = alg_hc_vc_w1

# обычные ячейки, без границ, сдвинуто вправо  == style7
style_plain_nobor_r = xlwt.XFStyle()
style_plain_nobor_r.font.name = 'Times New Roman'
style_plain_nobor_r.font.height = 20 * size
style_plain_nobor_r.alignment = al20

# обычные ячейки, без границ, сдвинуто влево
style_plain_nobor_l = xlwt.XFStyle()
style_plain_nobor_l.font.name = 'Times New Roman'
style_plain_nobor_l.font.height = 20 * size
style_plain_nobor_l.alignment = al3

# обычные ячейки, без границ, сдвинуто влево, c датовым форматом
style_plain_nobor_l_date = xlwt.XFStyle()
style_plain_nobor_l_date.font.name = 'Times New Roman'
style_plain_nobor_l_date.font.height = 20 * size
style_plain_nobor_l_date.alignment = al3
style_plain_nobor_l_date.num_format_str = 'DD.MM.YYYY г.'

# обычные ячейки, с границами, сдвинуто вправо  == style7
style_plain_r = xlwt.XFStyle()
style_plain_r.font.name = 'Times New Roman'
style_plain_r.font.height = 20 * size
style_plain_r.alignment.wrap = 1
style_plain_r.alignment = al20

# обычные ячейки, с границами, сдвинуто   влево
style_plain_l = xlwt.XFStyle()
style_plain_l.font.name = 'Times New Roman'
style_plain_l.font.height = 20 * size
style_plain_l.alignment.wrap = 1
style_plain_l.alignment = al3

pattern_black = xlwt.Pattern()
pattern_black.pattern = xlwt.Pattern.SOLID_PATTERN
pattern_black.pattern_fore_colour = 0

# чёрные ячейки
style_black = xlwt.XFStyle()
style_black.pattern = pattern_black



# блок 3 - выгрузка данных в формате ексель (списки приборов)
# (Набор вьюшек для выгрузки планов и отчетов по оборудованию в exel
# Так как планы и отчеты имеют сходную структуру. Они разделены на страницы для СИ, ИО, ВО,
# а также на помесячные суммы, то
# вначале идет общая базовая  функция.
# В ней объединено все общее для всех планов и отчетов. Базовая функция  выполняется в индивидуальных функциях)


def base_planreport_xls(request, exel_file_name,
                               measure_e, testing_e, helping_e,
                               measure_e_months, testing_e_months, helping_e_months,
                               u_headers_me, u_headers_te, u_headers_he,
                               str1, str2, str3, str4, str5, str6, nameME, nameTE, nameHE):
    """базовое шаблон представление для выгрузки планов и отчетов по СИ, ИО, ВО к которому обращаются частные представления"""
    company = Company.objects.get(userid=request.user.profile.userid)
    affirmation = f'УТВЕРЖДАЮ \n{company.direktor_position}\n{company.name}\n____________/{company.direktor_name}/\n«__» ________20__ г.'  
    author = f'Разработал: \n{company.manager_position} _____________ /{company.manager_name}/'
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{exel_file_name}.xls"'

   
    # добавляем книгу и страницы
    wb = xlwt.Workbook(encoding='utf-8')
    ws1 = wb.add_sheet(f'{str1}', cell_overwrite_ok=True)
    ws2 = wb.add_sheet(f'{str2}', cell_overwrite_ok=True)
    ws3 = wb.add_sheet(f'{str3}', cell_overwrite_ok=True)
    ws4 = wb.add_sheet(f'{str4}', cell_overwrite_ok=True)
    ws5 = wb.add_sheet(f'{str5}', cell_overwrite_ok=True)
    ws6 = wb.add_sheet(f'{str6}', cell_overwrite_ok=True)

    # убираем колонтитулы
    ws1.header_str = b' '
    ws1.footer_str = b' '
    ws2.header_str = b' '
    ws2.footer_str = b' '
    ws3.header_str = b' '
    ws3.footer_str = b' '
    ws4.header_str = b' '
    ws4.footer_str = b' '
    ws5.header_str = b' '
    ws5.footer_str = b' '
    ws6.header_str = b' '
    ws6.footer_str = b' '

    # ширина столбцов СИ
    ws1.col(0).width = 2500
    ws1.col(1).width = 2500
    ws1.col(2).width = 4500
    ws1.col(3).width = 4500
    ws1.col(4).width = 2500
    ws1.col(5).width = 4500
    ws1.col(6).width = 4500
    ws1.col(7).width = 4500
    ws1.col(7).width = 7500
    ws1.col(8).width = 7500
    ws1.col(9).width = 7500
    ws1.col(10).width = 7500
    ws1.col(11).width = 7500
    ws1.col(12).width = 7500
    ws1.col(13).width = 7500
    ws1.col(14).width = 7500
    ws1.col(15).width = 7500

    # ширина столбцов ИО
    ws2.col(0).width = 2500
    ws2.col(1).width = 4500
    ws2.col(2).width = 4500
    ws2.col(3).width = 4500
    ws2.col(4).width = 4500
    ws2.col(5).width = 4500
    ws2.col(6).width = 4500
    ws2.col(7).width = 4500
    ws2.col(8).width = 7500
    ws2.col(9).width = 7500
    ws2.col(10).width = 7500
    ws2.col(11).width = 7500
    ws2.col(12).width = 7500
    ws2.col(13).width = 7500
    ws2.col(14).width = 7500
    ws2.col(15).width = 7500

    # ширина столбцов ВО
    ws3.col(0).width = 2500
    ws3.col(1).width = 2500
    ws3.col(2).width = 4500
    ws3.col(3).width = 4500
    ws3.col(4).width = 2500
    ws3.col(5).width = 4500
    ws3.col(6).width = 2500
    ws3.col(7).width = 4500
    ws3.col(8).width = 7500
    ws3.col(9).width = 7500
    ws3.col(11).width = 7500
    ws3.col(12).width = 7500
    ws3.col(13).width = 7500
    ws3.col(14).width = 7500
    ws3.col(15).width = 7500

    # колонки для разбиивок по месяцам
    columns_month = [
        'Месяц',
        'Количество единиц оборудования',
        'Сумма, руб',
    ]

    # заголовки СИ (вынесены сюда для подсчёта длины строк ексель)
    columnsME = [
        'Внутренний номер',
        'Номер в госреестре',
        'Наименование',
        'Тип/Модификация',
        'Заводской номер',
    ]
    columnsME = columnsME + u_headers_me
    lennME = len(columnsME)

    # заголовки ИО (вынесены сюда для подсчёта длины строк ексель)
    columnsTE = [
        'Внутренний номер',
        'Наименование',
        'Тип/Модификация',
        'Заводской номер',
    ]
    columnsTE = columnsTE + u_headers_te
    lennTE = len(columnsTE)

    # заголовки ВО (вынесены сюда для подсчёта длины строк ексель)
    columnsHE = [
        'Внутренний номер',
        'Наименование',
        'Тип/Модификация',
        'Заводской номер',
    ]
    columnsHE = columnsHE + u_headers_he
    lennHE = len(columnsHE)

    # записываем страницу 1 - СИ
    row_num = 0
    c = [''] * (lennME - 3)
    columns = c + [
        affirmation,
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_nobor_r)
        ws1.merge(row_num, row_num, lennME - 3, lennME - 1, style_plain_nobor_r)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1900

    row_num += 2
    columns = [
        f'{nameME}'
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_nobor_bold)
        ws1.merge(row_num, row_num, 0, lennME-1, style_plain_nobor_bold)
        ws2.row(row_num).height_mismatch = True
        ws2.row(row_num).height = 800

    # заголовки СИ
    row_num += 2
    datecolumnme = []

    # запись заголовков СИ
    for col_num in range(len(columnsME)):
        ws1.write(row_num, col_num, columnsME[col_num], style_bold_borders)
        if 'Дата' in str(columnsME[col_num]) or 'дата' in str(columnsME[col_num]):
            datecolumnme.append(col_num)

    # данные СИ и их запись
    rows = measure_e
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num in datecolumnme:
                ws1.write(row_num, col_num, row[col_num], style_date)
            else:
                ws1.write(row_num, col_num, row[col_num], style_plain)

    # подпись СИ
    row_num += 2
    columns = [
        author
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_nobor_l)
        ws1.merge(row_num, row_num, 0, lennME-1, style_plain_nobor_l)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1000


    # записываем страницу 2 - ИО
    # Шапка утверждаю
    row_num = 0
    c = [''] * (lennTE - 2)
    columns = c + [
        affirmation,
    ]
    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], style_plain_nobor_r)
        ws2.merge(row_num, row_num, lennTE - 2, lennTE - 1, style_plain_nobor_r)
        ws2.row(row_num).height_mismatch = True
        ws2.row(row_num).height = 1900

    row_num += 2
    columns = [
        f'{nameTE}'
    ]
    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], style_plain_nobor_bold)
        ws2.merge(row_num, row_num, 0, lennTE-1, style_plain_nobor_bold)
        ws2.row(row_num).height_mismatch = True
        ws2.row(row_num).height = 800

    # заголовки ИО
    row_num += 2
    datecolumnte = []

    # запись заголовков ИО
    for col_num in range(len(columnsTE)):
        ws2.write(row_num, col_num, columnsTE[col_num], style_bold_borders)
        if 'Дата' in str(columnsTE[col_num]) or 'дата' in str(columnsTE[col_num]):
            datecolumnte.append(col_num)

    # данные ИО и их запись
    rows = testing_e
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num in datecolumnte:
                ws2.write(row_num, col_num, row[col_num], style_date)
            else:
                ws2.write(row_num, col_num, row[col_num], style_plain)

    # подпись ИО
    row_num += 2
    columns = [
        author
    ]
    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], style_plain_nobor_l)
        ws2.merge(row_num, row_num, 0, lennTE-1, style_plain_nobor_l)
        ws2.row(row_num).height_mismatch = True
        ws2.row(row_num).height = 1000

    # записываем страницу 3 - ВО
    row_num = 0
    c = [''] * (lennHE - 2)
    columns = c + [
        affirmation,
    ]
    for col_num in range(len(columns)):
        ws3.write(row_num, col_num, columns[col_num], style_plain_nobor_r)
        ws3.merge(row_num, row_num, lennHE - 2, lennHE - 1, style_plain_nobor_r)
        ws3.row(row_num).height_mismatch = True
        ws3.row(row_num).height = 1900

    row_num += 2
    columns = [
        f'{nameHE}'
    ]
    for col_num in range(len(columns)):
        ws3.write(row_num, col_num, columns[col_num], style_plain_nobor_bold)
        ws3.merge(row_num, row_num, 0, lennHE-1, style_plain_nobor_bold)
        ws3.row(row_num).height_mismatch = True
        ws3.row(row_num).height = 800

    # заголовки ВО
    row_num += 2
    datecolumnhe = []

    # запись заголовков ВО
    for col_num in range(len(columnsHE)):
        ws3.write(row_num, col_num, columnsHE[col_num], style_bold_borders)
        if 'Дата' in str(columnsHE[col_num]) or 'дата' in str(columnsHE[col_num]):
            datecolumnhe.append(col_num)

    # данные ВО и их запись
    rows = helping_e
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if col_num in datecolumnme:
                ws3.write(row_num, col_num, row[col_num], style_date)
            else:
                ws3.write(row_num, col_num, row[col_num], style_plain)

    # подпись ВО
    row_num += 2
    columns = [
        author
    ]
    for col_num in range(len(columns)):
        ws3.write(row_num, col_num, columns[col_num], style_plain_nobor_l)
        ws3.merge(row_num, row_num, 0, lennHE-1, style_plain_nobor_l)
        ws3.row(row_num).height_mismatch = True
        ws3.row(row_num).height = 1000

    # записываем страницу 4 - подсчёт по месяцам для СИ (ПСИ)
    # заголовки ПСИ
    row_num = 0

    # запись заголовков ПСИ
    for col_num in range(len(columns_month)):
        ws4.write(row_num, col_num, columns_month[col_num], style_bold_borders)

    # данные ПСИ и их запись
    rows = measure_e_months
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws4.write(row_num, col_num, row[col_num], style_plain)

    # записываем страницу 5 - подсчёт по месяцам для ИО (ПИО)
    # заголовки ПИО
    row_num = 0

    # запись заголовков ПИО
    for col_num in range(len(columns_month)):
        ws5.write(row_num, col_num, columns_month[col_num], style_bold_borders)

    # данные ПИО и их запись
    rows = testing_e_months
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws5.write(row_num, col_num, row[col_num], style_plain)

    # записываем страницу 6 - подсчёт по месяцам для ВО (ПВО)
    # заголовки ПВО
    row_num = 0

    # запись заголовков ПВО
    for col_num in range(len(columns_month)):
        ws6.write(row_num, col_num, columns_month[col_num], style_bold_borders)

    # данные ПВО и их запись
    rows = helping_e_months
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws6.write(row_num, col_num, row[col_num], style_plain)

    # все сохраняем
    wb.save(response)
    return response


# флаг отчёты по поверке
def export_metroyearcust_xls(request):
    """Список СИ и ИО прошедших поверку/аттестацию в указанном году, исключая ЛО купленное с поверкой/аттестацией"""
    serdate = request.GET['date']
    company = Company.objects.get(userid=request.user.profile.userid)
    exel_file_name = f'report_inner_metro {serdate}'
    str1 = 'СИ'
    str2 = 'ИО'
    str3 = 3
    str4 = 'СИ - поверено единиц в месяц'
    str5 = 'ИО - аттестовано единиц в месяц'
    str6 = 6


    u_headers_me = ['Номер свидетельства',
                    'Стоимость поверки, руб.',
                    'Дата поверки',
                    'Дата окончания свидетельства',
                    ]

    measure_e = MeasurEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__pointer=request.user.profile.userid). \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_ver__in=setver). \
        filter(equipmentSM_ver__date__year=serdate). \
        exclude(equipmentSM_ver__cust=True). \
        values_list(
        'exnumber',
        'charakters__reestr',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipmentSM_ver__certnumber',
        'equipmentSM_ver__price',
        'equipmentSM_ver__date',
        'equipmentSM_ver__datedead',
    ).order_by('equipmentSM_ver__date')

    u_headers_te = ['Номер аттестата',
                    'Стоимость аттестации, руб.',
                    'Дата аттестации',
                    'Дата окончания аттестации',
                    ]

    testing_e = TestingEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__pointer=request.user.profile.userid). \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipmentSM_att__date__year=serdate). \
        exclude(equipmentSM_att__cust=True). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipmentSM_att__certnumber',
        'equipmentSM_att__price',
        'equipmentSM_att__date',
        'equipmentSM_att__datedead'
    ).order_by('equipmentSM_att__date')

    u_headers_he = []
    helping_e = []

    measure_e_months = MeasurEquipment.objects. \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_ver__in=setver). \
        filter(equipmentSM_ver__date__year=serdate). \
        filter(equipmentSM_ver__price__isnull=False). \
        exclude(equipmentSM_ver__cust=True). \
        values('equipmentSM_ver__date__month'). \
        annotate(dcount=Count('equipmentSM_ver__date__month'), s=Sum('equipmentSM_ver__price')). \
        order_by(). \
        values_list(
        'equipmentSM_ver__date__month',
        'dcount',
        's',
    )

    testing_e_months = TestingEquipment.objects. \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipmentSM_att__date__year=serdate). \
        filter(equipmentSM_att__price__isnull=False). \
        exclude(equipmentSM_att__cust=True). \
        values('equipmentSM_att__date__month'). \
        annotate(dcount1=Count('equipmentSM_att__date__month'), s1=Sum('equipmentSM_att__price')). \
        order_by(). \
        values_list(
        'equipmentSM_att__date__month',
        'dcount1',
        's1',
    )

    helping_e_months = []
    serdate = request.GET['date']
    company = Company.objects.get(userid=request.user.profile.userid)
    nameME = f'Средства измерений - отчет по поверке в {company.name} за {serdate} год'
    nameTE = f'Испытательное оборудование - отчет по аттестации в {company.name} за {serdate} год'
    nameHE = ''

    return base_planreport_xls(request, exel_file_name,
                        measure_e, testing_e, helping_e,
                       measure_e_months, testing_e_months, helping_e_months,
                        u_headers_me, u_headers_te, u_headers_he,
                               str1, str2, str3, str4, str5, str6, nameME, nameTE, nameHE
                               )

def export_metroyearprice_xls(request):
    """представление для выгрузки - Список СИ и ИО прошедших поверку в указанном году только те где
    Список СИ и ИО прошедших поверку в указанном году только где указана стоимость"""
    serdate = request.GET['date']
    exel_file_name = f'report_all_withprice_metro {serdate}'
    str1 = 'СИ'
    str2 = 'ИО'
    str3 = 3
    str4 = 'СИ - поверено единиц в месяц'
    str5 = 'ИО - аттестовано единиц в месяц'
    str6 = 6


    u_headers_me = ['Номер свидетельства',
                    'Стоимость поверки, руб.',
                    'Дата поверки',
                    'Дата окончания свидетельства',
                    ]

    measure_e = MeasurEquipment.objects. \
        annotate(exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_ver__in=setver). \
        filter(equipmentSM_ver__date__year=serdate). \
        filter(equipmentSM_ver__price__isnull=False). \
        filter(equipment__pointer=request.user.profile.userid). \
        values_list(
        'exnumber',
        'charakters__reestr',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipmentSM_ver__certnumber',
        'equipmentSM_ver__price',
        'equipmentSM_ver__date',
        'equipmentSM_ver__datedead',
    ).order_by('equipmentSM_ver__date')

    u_headers_te = ['Номер аттестата',
                    'Стоимость аттестации, руб.',
                    'Дата аттестации',
                    'Дата окончания аттестации',
                    ]

    testing_e = TestingEquipment.objects. \
        annotate(exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__personchange__in=setperson). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipmentSM_att__date__year=serdate). \
        filter(equipmentSM_att__price__isnull=False). \
        filter(equipment__pointer=request.user.profile.userid). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipmentSM_att__certnumber',
        'equipmentSM_att__price',
        'equipmentSM_att__date',
        'equipmentSM_att__datedead'
    ).order_by('equipmentSM_att__date')

    u_headers_he = []
    helping_e = []

    measure_e_months = MeasurEquipment.objects. \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_ver__in=setver). \
        filter(equipmentSM_ver__date__year=serdate). \
        filter(equipmentSM_ver__price__isnull=False).\
        values('equipmentSM_ver__date__month').\
        filter(equipment__pointer=request.user.profile.userid). \
        annotate(dcount=Count('equipmentSM_ver__date__month'), s=Sum('equipmentSM_ver__price')).\
        order_by().\
        values_list(
        'equipmentSM_ver__date__month',
        'dcount',
        's',
    )

    testing_e_months = TestingEquipment.objects. \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipmentSM_att__date__year=serdate). \
        filter(equipmentSM_att__price__isnull=False). \
        filter(equipment__pointer=request.user.profile.userid). \
        values('equipmentSM_att__date__month'). \
        annotate(dcount1=Count('equipmentSM_att__date__month'), s1=Sum('equipmentSM_att__price')). \
        order_by(). \
        values_list(
        'equipmentSM_att__date__month',
        'dcount1',
        's1',
    )



    return base_planreport_xls(request, exel_file_name,
                        measure_e, testing_e, helping_e,
                       measure_e_months, testing_e_months, helping_e_months,
                        u_headers_me, u_headers_te, u_headers_he,
                               str1, str2, str3, str4, str5, str6, nameME, nameTE, nameHE
                               )

def export_metroyear_xls(request):
    """Список СИ и ИО прошедших поверку/аттестацию в указанном году, включая ЛО купленное с поверкой/аттестацие"""
    serdate = request.GET['date']
    company = Company.objects.get(userid=request.user.profile.userid)
    exel_file_name = f'report_all_metro {serdate}'
    str1 = 'СИ'
    str2 = 'ИО'
    str3 = 3
    str4 = 4
    str5 = 5
    str6 = 6


    u_headers_me = ['Номер свидетельства',
                    'Стоимость поверки, руб.',
                    'Дата поверки',
                    'Дата окончания свидетельства',
                    ]

    measure_e = MeasurEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_ver__in=setver). \
        filter(equipmentSM_ver__date__year=serdate). \
        filter(equipment__pointer=request.user.profile.userid).\
        values_list(
        'exnumber',
        'charakters__reestr',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipmentSM_ver__certnumber',
        'equipmentSM_ver__price',
        'equipmentSM_ver__date',
        'equipmentSM_ver__datedead',
    ).order_by('equipmentSM_ver__date')

    u_headers_te = ['Номер аттестата',
                    'Стоимость аттестации, руб.',
                    'Дата аттестации',
                    'Дата окончания аттестации',
                    ]

    testing_e = TestingEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__personchange__in=setperson). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipmentSM_att__date__year=serdate). \
        filter(equipment__pointer=request.user.profile.userid).\
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipmentSM_att__certnumber',
        'equipmentSM_att__price',
        'equipmentSM_att__date',
        'equipmentSM_att__datedead'
    ).order_by('equipmentSM_att__date')

    u_headers_he = []
    helping_e = []

    measure_e_months = []

    testing_e_months = []

    helping_e_months = []
    serdate = request.GET['date']
    nameME = f'Средства измерений - отчет по поверке в {company.name} за {serdate} год (включая купленное с поверкой)'
    nameTE = f'Испытательное оборудование - отчет по аттестации в {company.name} за {serdate} год (включая купленное с аттестацией)'
    nameHE = ''

    return base_planreport_xls(request, exel_file_name,
                        measure_e, testing_e, helping_e,
                       measure_e_months, testing_e_months, helping_e_months,
                        u_headers_me, u_headers_te, u_headers_he,
                               str1, str2, str3, str4, str5, str6, nameME, nameTE, nameHE
                               )

# флаг отчёты по закупке
def export_metronewyear_xls(request):
    """представление для выгрузки -
    Список купленного (введенного в эксплуатацию) СИ и ИО в указанном году"""
    serdate = request.GET['date']
    company = Company.objects.get(userid=request.user.profile.userid)
    exel_file_name = f'purchased_equipment_{serdate}'
    str1 = 'СИ'
    str2 = 'ИО'
    str3 = 'ВО'
    str4 = 'Количество СИ в месяц'
    str5 = 'Количество ИО в месяц'
    str6 = 'Количество ВО в месяц'


    u_headers_me = ['Стоимость',
                    ]

    measure_e = MeasurEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_ver__in=setver). \
        filter(equipment__yearintoservice=serdate). \
        filter(equipment__pointer=request.user.profile.userid). \
        values_list(
        'exnumber',
        'charakters__reestr',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipment__price',
    ).order_by('equipment__date')

    u_headers_te = ['Стоимость',
                    ]

    testing_e = TestingEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__personchange__in=setperson). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipment__yearintoservice=serdate). \
        filter(equipment__pointer=request.user.profile.userid). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipment__price',
    ).order_by('equipment__date')

    u_headers_he = ['Стоимость',]
    helping_e = HelpingEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__yearintoservice=serdate). \
        filter(equipment__pointer=request.user.profile.userid). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipment__price',
    ).order_by('equipment__date')

    measure_e_months = MeasurEquipment.objects. \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_ver__in=setver). \
        filter(equipment__yearintoservice=serdate). \
        values('equipment__date__month'). \
        annotate(dcount=Count('equipment__date__month'), s=Sum('equipment__price')). \
        order_by(). \
        values_list(
        'equipment__date__month',
        'dcount',
        's',
    )

    testing_e_months = qt1 = TestingEquipment.objects. \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipment__yearintoservice=serdate). \
        values('equipment__date__month'). \
        annotate(dcount1=Count('equipment__date__month'), s1=Sum('equipment__price')). \
        order_by(). \
        values_list(
        'equipment__date__month',
        'dcount1',
        's1',
    )

    helping_e_months = HelpingEquipment.objects. \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__yearintoservice=serdate). \
        values('equipment__date__month'). \
        annotate(dcount2=Count('equipment__date__month'), s2=Sum('equipment__price')). \
        order_by(). \
        values_list(
        'equipment__date__month',
        'dcount2',
        's2',
    )

    nameME = f'CИ введенные в эксплуатацию в {company.name} за {serdate} год'
    nameTE = f'ИО введенное в эксплуатацию  в {company.name} за {serdate} год'
    nameHE = f'ВО введенное в эксплуатацию  в {company.name} за {serdate} год'

    return base_planreport_xls(request, exel_file_name,
                        measure_e, testing_e, helping_e,
                       measure_e_months, testing_e_months, helping_e_months,
                        u_headers_me, u_headers_te, u_headers_he,
                               str1, str2, str3, str4, str5, str6, nameME, nameTE, nameHE
                               )
# флаг план по поверке
def export_planmetro_xls(request):
    """представление для выгрузки плана поверки и аттестации на указанный год"""
    serdate = request.GET['date']
    company = Company.objects.get(userid=request.user.profile.userid)
    exel_file_name = f'planmetro {serdate}'
    str1 = 'СИ'
    str2 = 'ИО'
    str3 = 3
    str4 = 'СИ-количество поверок в месяц'
    str5 = 'ИО-кол-во аттестаций в месяц'
    str6 = 6


    u_headers_me = ['Текущее свидетельство',
                    'Дата окончания свидетельства',
                    'Стоимость последней поверки, руб. (при наличии)',
                    'Месяц заказа поверки',
                    ]

    measure_e = MeasurEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
            filter(equipment__roomschange__in=setroom). \
                                filter(equipment__personchange__in=setperson). \
                                filter(equipmentSM_ver__in=setver). \
                                filter(equipmentSM_ver__dateorder__year=serdate). \
                                filter(equipment__pointer=request.user.profile.userid). \
                                values_list(
                                'exnumber',
                                'charakters__reestr',
                                'charakters__name',
                                'charakters__typename',
                                'equipment__lot',
                                'equipmentSM_ver__certnumber',
                                'equipmentSM_ver__datedead',
                                'equipmentSM_ver__price',
                                'equipmentSM_ver__dateorder__month',
                            ).order_by('equipmentSM_ver__dateorder__month')

    u_headers_te = ['Текущий аттестат',
                    'Дата окончания аттестата',
                    'Стоимость последней аттестации, руб. (при наличии)',
                    'Месяц заказа аттестации',
                    ]

    testing_e = TestingEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)).\
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__personchange__in=setperson). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipmentSM_att__dateorder__year=serdate). \
        filter(equipment__pointer=request.user.profile.userid). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipmentSM_att__certnumber',
        'equipmentSM_att__datedead',
        'equipmentSM_att__price',
        'equipmentSM_att__dateorder__month',
    ).order_by('equipmentSM_att__dateorder__month')

    u_headers_he = []
    helping_e = []
    measure_e_months = MeasurEquipment.objects.\
        filter(equipment__pointer=request.user.profile.userid). \
        filter(equipment__personchange__in=setperson).\
        filter(equipmentSM_ver__dateorder__year=serdate).\
        values('equipmentSM_ver__dateorder__month').\
        annotate(dcount=Count('equipmentSM_ver__dateorder__month'), s=Sum('equipmentSM_ver__price')). \
        order_by().\
        values_list(
        'equipmentSM_ver__dateorder__month',
        'dcount',
        's',
    )

    testing_e_months = TestingEquipment.objects.\
        filter(equipment__pointer=request.user.profile.userid). \
        filter(equipment__personchange__in=setperson).\
        filter(equipmentSM_att__dateorder__year=serdate).\
        values('equipmentSM_att__dateorder__month').\
        annotate(dcount=Count('equipmentSM_att__dateorder__month'), s=Sum('equipmentSM_att__price')). \
        order_by().\
        values_list(
        'equipmentSM_att__dateorder__month',
        'dcount',
        's',
    )
    helping_e_months = []
    nameME = f'План поверки средств измерений в {company.name} на {serdate} год'
    nameTE = f'План аттестации испытательного оборудования в {company.name} за {serdate} год'
    nameHE = f'План проверки характеристик вспомогательного оборудования в {company.name} за {serdate} год'

    return base_planreport_xls(request, exel_file_name,
                               measure_e, testing_e, helping_e,
                               measure_e_months, testing_e_months, helping_e_months,
                               u_headers_me, u_headers_te, u_headers_he,
                               str1, str2, str3, str4, str5, str6, nameME, nameTE, nameHE
                               )

# флаг план закупки по поверке
def export_plan_purchaesing_xls(request):
    """представление для выгрузки плана закупки ЛО по поверке и аттестации на указанный год"""
    serdate = request.GET['date']
    company = Company.objects.get(userid=request.user.profile.userid)
    exel_file_name = f'plan_purchaesing_{serdate}'
    str1 = 'СИ'
    str2 = 'ИО'
    str3 = 3
    str4 = 'СИ-количество в месяц'
    str5 = 'ИО-кол-во в месяц'
    str6 = 6


    u_headers_me = ['Текущее свидетельство',
                    'Стоимость оборудования',
                    'Месяц заказа замены',
                    ]

    measure_e = MeasurEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
                                filter(equipment__roomschange__in=setroom). \
                                filter(equipment__personchange__in=setperson). \
                                filter(equipmentSM_ver__dateordernew__year=serdate). \
                                filter(equipmentSM_ver__haveorder=False). \
                                filter(equipment__pointer=request.user.profile.userid). \
                                values_list(
                                'exnumber',
                                'charakters__reestr',
                                'charakters__name',
                                'charakters__typename',
                                'equipment__lot',
                                'equipmentSM_ver__certnumber',
                                'equipment__price',
                                'equipmentSM_ver__dateordernew__month',
                            ).order_by('equipmentSM_ver__dateordernew__month')

    u_headers_te = ['Текущий аттестат',
                    'Стоимость оборудования',
                    'Месяц заказа замены',
                    ]

    testing_e = TestingEquipment.objects. \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName'), exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__personchange__in=setperson). \
        filter(equipmentSM_att__dateordernew__year=serdate). \
        filter(equipmentSM_att__haveorder=False). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipmentSM_att__certnumber',
        'equipment__price',
        'equipmentSM_att__dateordernew__month',
    ).order_by('equipmentSM_att__dateordernew__month')

    u_headers_he = []
    helping_e = []
    measure_e_months = MeasurEquipment.objects.\
        filter(equipment__pointer=request.user.profile.userid). \
        filter(equipment__personchange__in=setperson).\
        filter(equipmentSM_ver__dateordernew__year=serdate). \
        filter(equipmentSM_ver__haveorder=False). \
        values('equipmentSM_ver__dateordernew__month').\
        annotate(dcount=Count('equipmentSM_ver__dateordernew__month'), s=Sum('equipment__price')). \
        order_by().\
        values_list(
        'equipmentSM_ver__dateordernew__month',
        'dcount',
        'dcount',
        's',
    )

    testing_e_months = TestingEquipment.objects.\
        filter(equipment__pointer=request.user.profile.userid). \
        filter(equipment__personchange__in=setperson).\
        filter(equipmentSM_att__dateordernew__year=serdate).\
        values('equipmentSM_att__dateordernew__month').\
        annotate(dcount=Count('equipmentSM_att__dateordernew__month'), s=Sum('equipment__price')). \
        filter(equipmentSM_att__haveorder=False). \
        order_by().\
        values_list(
        'equipmentSM_att__dateordernew__month',
        'dcount',
        's',
    )
    helping_e_months = []
    nameME = ''
    nameTE = ''
    nameHE = ''

    return base_planreport_xls(request, exel_file_name,
                               measure_e, testing_e, helping_e,
                               measure_e_months, testing_e_months, helping_e_months,
                               u_headers_me, u_headers_te, u_headers_he,
                               str1, str2, str3, str4, str5, str6, nameME, nameTE, nameHE
                               )


def export_mustver_xls(request):
    """представление для выгрузки СИ требующих поверки и ИО требующих аттестации"""
    # выборка из ексель по поиску по дате
    serdate = request.GET['date']
    company = Company.objects.get(userid=request.user.profile.userid)
    exel_file_name = f'mustveratt_{serdate}'
    str1 = 'СИ'
    str2 = 'ИО'
    str3 = 3
    str4 = 4
    str5 = 5
    str6 = 6

    queryset_get = Verificationequipment.objects.filter(haveorder=False). \
        select_related('equipmentSM').values('equipmentSM'). \
        annotate(id_actual=Max('id')).values('id_actual')  
    b = list(queryset_get)
    set = []
    for i in b:
        a = i.get('id_actual')
        set.append(a)
    queryset_get1 = Verificationequipment.objects.filter(id__in=set). \
        filter(dateorder__lte=serdate).values('equipmentSM__id')
    b = list(queryset_get1)
    set1 = []
    for i in b:
        a = i.get('equipmentSM__id')
        set1.append(a)

    queryset_get0 = Attestationequipment.objects.filter(haveorder=False). \
        select_related('equipmentSM').values('equipmentSM'). \
        annotate(id_actual=Max('id')).values('id_actual')
    b = list(queryset_get0)
    set10 = []
    for i in b:
        a = i.get('id_actual')
        set10.append(a)
    queryset_get10 = Attestationequipment.objects.filter(id__in=set10). \
        filter(dateorder__lte=serdate).values('equipmentSM__id')
    b = list(queryset_get10)
    set10 = []
    for i in b:
        a = i.get('equipmentSM__id')
        set10.append(a)

    u_headers_me = [
                    'Год выпуска',
                    'Место хранения',
                    'Место поверки (предыдущей)',
                    'Сотрудник, ответственный за подготовку к поверке/аттестации',
                    'Постоянное примечание к поверке',
                    'Выписка из последних сведений о поверке',
                    ]

    measure_e = MeasurEquipment.objects.filter(id__in=set1). \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName')).annotate(exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__pointer=request.user.profile.userid). \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__status='Э'). \
        filter(equipmentSM_ver__in=setver). \
        values_list(
        'exnumber',
        'charakters__reestr',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipment__yearmanuf',
        'equipment__roomschange__roomnumber__roomnumber',
        'equipmentSM_ver__place',
        'equipment__newperson',
        'equipment__notemetrology',
        'equipmentSM_ver__extra',
    ).order_by('-equipmentSM_ver__place')

    u_headers_te = [
                    'Год выпуска',
                    'Место хранения',
                    'Место аттестации (предыдущей)',
                    'Сотрудник, ответственный за подготовку к поверке/аттестации',
                    'Постоянное примечание к аттестации',
                    'Выписка из последнего аттестата',
                    ]

    testing_e = TestingEquipment.objects.filter(id__in=set10). \
        annotate(manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName')).annotate(exnumber=Substr('equipment__exnumber',1,5)). \
        filter(equipment__personchange__in=setperson). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__status='Э'). \
        filter(equipmentSM_att__in=setatt). \
        filter(equipment__pointer=request.user.profile.userid). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipment__yearmanuf',
        'equipment__roomschange__roomnumber__roomnumber',
        'equipmentSM_att__place',
        'equipment__newperson',
        'equipment__notemetrology',
        'equipmentSM_att__extra'
    ).order_by('-equipmentSM_att__place')

    measure_e_months = []
    helping_e = []
    helping_e_months = []
    testing_e_months = []
    u_headers_he = []
    nameME = 'СИ требуют поверки'
    nameTE = 'ИО требует аттестации'
    nameHE = ''


    return base_planreport_xls(request, exel_file_name,
                               measure_e, testing_e, helping_e,
                               measure_e_months, testing_e_months, helping_e_months,
                               u_headers_me, u_headers_te, u_headers_he,
                               str1, str2, str3, str4, str5, str6, nameME, nameTE, nameHE
                               )


def export_meteo_xls(request, pk):
    '''представление для выгрузки журнала микроклимата'''
    serdate = request.GET['date']
    company = Company.objects.get(userid=request.user.profile.userid)
    note = MeteorologicalParameters.objects.filter(roomnumber_id=pk).filter(date__year=serdate)
    try:
        roomname = note.latest('id').roomnumber
    except:
        roomname = '0'

    roomname = str(roomname)
    rn = 'in '
    for i in roomname:
        if i.isdigit():
            rn = rn + i


    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="Microclimat {rn}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    i = wb.add_sheet('Журнал микроклимата', cell_overwrite_ok=True)

    i.col(0).width = 4000
    i.col(1).width = 3000
    i.col(2).width = 3000
    i.col(3).width = 3000
    i.col(4).width = 6000
    i.col(5).width = 3000
    i.header_str = b'c. &P  '
    i.footer_str = b' '

    row_num = 1
    columns = [
        f'Журнал регистрации условий микроклимата'
    ]
    for col_num in range(len(columns)):
        i.write(row_num, col_num, columns[col_num], style_plain_nobor_bold)
        i.merge(row_num, row_num, 0, 5)

    row_num += 1
    columns = [
        f'Помещение {rn[2:]}, {serdate} год'
    ]
    for col_num in range(len(columns)):
        i.write(row_num, col_num, columns[col_num], style_plain_nobor_bold)
        i.merge(row_num, row_num, 0, 5)

    row_num += 2
    columns = [
        f'При работе в лаборатории должны соблюдаться условия:'
        f' температура воздуха: (20±5) °C;'
        f' относительная влажность воздуха: не более 80%;'
        f' атмосферное давление: (100±7) кПа.'
    ]
    for col_num in range(len(columns)):
        i.write(row_num, col_num, columns[col_num], style_plain)
        i.merge(row_num, row_num, 0, 5, style_plain)
        i.row(row_num).height_mismatch = True
        i.row(row_num).height = 600

    row_num += 1
    columns = [
        f'Возможны иные условия,'
        f' указанные в методике и/или инструкции на оборудование.'
    ]
    for col_num in range(len(columns)):
        i.write(row_num, col_num, columns[col_num], style_plain)
        i.merge(row_num, row_num, 0, 5, style_plain)
        i.row(row_num).height_mismatch = True
        i.row(row_num).height = 400

    row_num += 2
    columns = [
        'Дата',
        'Температура, °C',
        'Относительная влажность, %',
        'Давление, кПа',
        'Измерил',
        'Заключение (удовл./неудовл.)',
    ]
    for col_num in range(len(columns)):
        i.write(row_num, col_num, columns[col_num], style_plain)

    rows = note.\
        values_list(
        'date',
        'temperature',
        'humidity',
        'pressure',
        'person',
    ).order_by('date')

    for row in rows:
        row_num += 1
        for col_num in range(1):
            i.write(row_num, col_num, row[col_num], style_date)
        for col_num in range(1, 5):
            i.write(row_num, col_num, row[col_num], style_plain)
        row = list(row)
        if float(row[1]) <= 25 and float(row[1]) >= 15 and float(row[2]) <= 80 and float(row[3]) <= 107 and float(row[3]) >= 93:
            for col_num in range(5, 6):
                i.write(row_num, col_num, 'удовл.', style_plain)
        else:
            for col_num in range(5, 6):
                i.write(row_num, col_num, 'неудовл.', style_plain)

    wb.save(response)
    return response


def export_mecard_xls(request, pk):
    '''представление для выгрузки карточки на прибор (СИ) в ексель'''
    company = Company.objects.get(userid=request.user.profile.userid)
    note = MeasurEquipment.objects.get(pk=pk)
    cardname = pytils.translit.translify(note.equipment.exnumber[:5]) + ' ' +\
                pytils.translit.translify(note.charakters.name) +\
                ' ' + pytils.translit.translify(note.equipment.lot)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{cardname}.xls"'
    wb = xlwt.Workbook(encoding='utf-8')

    ws = wb.add_sheet('Основная информация', cell_overwrite_ok=True)

    ws.col(0).width = 2700
    ws.col(1).width = 2500
    ws.col(2).width = 8000
    ws.col(3).width = 3700
    ws.col(4).width = 2500
    ws.col(5).width = 4300
    ws.col(6).width = 4000
    ws.col(7).width = 4300
    ws.col(8).width = 2000
    ws.col(9).width = 2000

    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 26
        
    al1 = Alignment()
    al1.horz = Alignment.HORZ_CENTER
    al1.vert = Alignment.VERT_CENTER
        
    b1 = Borders()
    b1.left = 1
    b1.right = 1
    b1.bottom = 1
    b1.top = 1
        
    style1 = xlwt.XFStyle()
    style1.font.height = 9 * 20
    style1.font.name = 'Calibri'
    style1.alignment = al1
    style1.alignment.wrap = 1
    style1.borders = b1
        
    style2 = xlwt.XFStyle()
    style2.font.height = 9 * 20
    style2.font.name = 'Calibri'
    style2.alignment = al1
    style2.alignment.wrap = 1
    style2.borders = b1
    style2.pattern = pattern
        
        
    style3 = xlwt.XFStyle()
    style3.font.height = 15 * 20
    style3.font.bold = True
    style3.font.name = 'Calibri'
    style3.alignment = al1
    style3.alignment.wrap = 1
        
    style4 = xlwt.XFStyle()
    style4.font.height = 9 * 20
    style4.font.name = 'Calibri'
    style4.alignment = al1
    style4.alignment.wrap = 1
    style4.borders = b1
    style4.num_format_str = 'DD.MM.YYYY'
        
    style5 = xlwt.XFStyle()
    style5.font.height = 20 * 20
    style5.font.bold = True
    style5.font.name = 'Calibri'
    style5.alignment = al1
    style5.alignment.wrap = 1   


    # Image.open(company.imglogoadress_mini.path).convert("RGB").save('logo.bmp')
    # ws.insert_bitmap('logo.bmp', 0, 0)
    ws.left_margin = 0
    ws.header_str = b'1'
    ws.footer_str = b' '
    ws.start_page_number = 1

    row_num = 1
    columns = [
        'Регистрационная карточка на СИ и ИО'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style5)
        ws.merge(row_num, row_num, 0, 9)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 1
    columns = [
        'Идентификационная и уникальная информация'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 9)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        'Внутренний номер',
        'Номер в госреестре',
        'Наименование',
        'Тип/модификация',
        'Заводской номер',
        'Год выпуска',
        'Производитель',
        'Год ввода в эксплуатацию в ООО "Петроаналитика" ',
        'Новый или б/у',
        'Инвентарный номер',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style2)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1100

    row_num += 1
    columns = [
        note.equipment.exnumber[:5],
        note.charakters.reestr,
        note.charakters.name,
        f'{note.charakters.typename}',
        note.equipment.lot,
        note.equipment.yearmanuf,
        f'{note.equipment.manufacturer.country}, {note.equipment.manufacturer.companyName}',
        note.equipment.yearintoservice,
        note.equipment.new,
        note.equipment.invnumber,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1100

    row_num += 1
    columns = [
        'Расположение и комплектность'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 9)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 1
    columns = [
        'Документы, комплектные принадлежности, программное обеспечение',
        'Документы, комплектные принадлежности, программное обеспечение',
        'Документы, комплектные принадлежности, программное обеспечение',
        'Документы, комплектные принадлежности, программное обеспечение',
        'Ответственный за прибор',
        'Ответственный за прибор',
        'Расположение прибора',
        'Расположение прибора',
        'Расположение прибора',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 0, 4, style2)
        ws.merge(row_num, row_num, 5, 6, style2)
        ws.merge(row_num, row_num, 7, 9, style2)

    row_num += 1
    row_num_fix = row_num

    columns = [
        'год появления',
        'наименование документа/комплектной принадлежности/ПО',
        'наименование документа/комплектной принадлежности/ПО',
        'откуда поступил документ/ принадлежность/ПО',
        'откуда поступил документ/ принадлежность/ПО',
        'дата',
        'ответственный, ФИО',
        'дата',
        'номер комнаты',
        'номер комнаты',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 1, 2, style2)
        ws.merge(row_num, row_num, 3, 4, style2)
        ws.merge(row_num, row_num, 8, 9, style2)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    rows_1 = DocsCons.objects.filter(equipment=note.equipment). \
        values_list(
        'date',
        'docs',
        'docs',
        'source',
        'source',
    )
    rows_2 = Personchange.objects.filter(equipment=note.equipment). \
        values_list(
        'date',
        'person__profile__short_name',
    )

    rows_3 = Roomschange.objects.filter(equipment=note.equipment). \
        values_list(
        'date',
        'roomnumber__roomnumber',
    )


    for row in rows_1:
        row_num += 1
        for col_num in range(5):
            ws.write(row_num, col_num, row[col_num], style1)
            ws.merge(row_num, row_num, 1, 2, style2)
            ws.merge(row_num, row_num, 3, 4, style2)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500
    a = row_num

    row_num = row_num_fix
    for row in rows_2:
        row_num += 1
        for col_num in range(5, 7):
            ws.write(row_num, col_num, row[col_num - 5], style4)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500
    b = row_num


    row_num = row_num_fix
    for row in rows_3:
        row_num += 1
        for col_num in range(7, 9):
            ws.write(row_num, col_num, row[col_num - 7], style4)
            ws.merge(row_num, row_num, 8, 9, style4)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500
    c = row_num

    d = max(a, b, c)


    row_num += 15
    columns = [
        'Соответствие оборудования  установленным требованиям подтверждается протоколом верификации'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 0, 9, style2)

    ws1 = wb.add_sheet('Данные о ремонте и поверке', cell_overwrite_ok=True)

    ws1.col(0).width = 1500
    ws1.col(1).width = 7000
    ws1.col(2).width = 1000
    ws1.col(3).width = 2400
    ws1.col(4).width = 2000
    ws1.col(5).width = 4000
    ws1.col(6).width = 14000
    ws1.col(7).width = 4000

    # Image.open(company.imglogoadress_mini.path).convert("RGB").save('logo.bmp')
    # ws1.insert_bitmap('logo.bmp', 0, 0)
    # ws1.left_margin = 0

    ws1.header_str = b'&F c. &P  '
    ws1.footer_str = b' '
    ws1.start_page_number = 2

    row_num = 1
    columns = [
        'Особенности работы прибора',
        'Особенности работы прибора',
        note.equipment.individuality,
        note.equipment.individuality,
        note.equipment.individuality,
        note.equipment.individuality,
        note.equipment.individuality,
    ]
    for col_num in range(2):
        ws1.write(row_num, col_num, columns[col_num], style2)
        ws1.merge(row_num, row_num, 0, 1, style2)
    for col_num in range(2, len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style1)
        ws1.merge(row_num, row_num, 2, 7, style1)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 2000


    row_num += 2
    columns = [
        'Поверка',
        'Поверка',
        '',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
    ]
    for col_num in range(2):
        ws1.write(row_num, col_num, columns[col_num], style2)
        ws1.merge(row_num, row_num, 0, 1, style2)
    for col_num in range(3, len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style2)
        ws1.merge(row_num, row_num, 3, 7, style2)

    row_num += 1
    columns = [
        'Год',
        'Сведения о результатах поверки',
        '',
        'Дата',
        'Описание',
        'Описание',
        'Описание',
        'ФИО исполнителя',
    ]
    for col_num in range(2):
        ws1.write(row_num, col_num, columns[col_num], style2)
    for col_num in range(3, len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style2)
        ws1.merge(row_num, row_num, 4, 6, style2)


    rows_1 = Verificationequipment.objects.filter(equipmentSM__equipment=note.equipment). \
        annotate(ver=Concat(
        Value('Свидетельство о поверке: \n  '),
        'certnumber',
        Value('\n от '), str('date'),
         Value('\n до '), str('datedead'),
        Value('\n выдано '),
        'verificator__companyName', output_field=CharField(),),
    ). \
        annotate(ver_year=Concat(
        'date__year', 'year',
         output_field=CharField(), ),
    ). \
        values_list(
        'ver_year',
        'ver',
    )

    rows_2 = CommentsEquipment.objects.filter(forNote=note.equipment). \
        values_list(
        'date',
        'note',
        'note',
        'note',
        'author',
    )

    row_num +=1
    row_num_fix=row_num
    for row in rows_1:
        row_num += 1
        for col_num in range(0, 1):
            ws1.write(row_num, col_num, row[col_num], style4)
        for col_num in range(1, 2):
            ws1.write(row_num, col_num, row[col_num], style4)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1500

    row_num = row_num_fix
    for row in rows_2:
        row_num += 1
        for col_num in range(3, 8):
            ws1.write(row_num, col_num, row[col_num - 3], style4)
            ws1.merge(row_num, row_num, 4, 6, style1)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1500

    wb.save(response)
    return response


# флаг карточки на ИО
def export_tecard_xls(request, pk):
    '''представление для выгрузки карточки на прибор (ИО) в ексель'''
    note = TestingEquipment.objects.get(pk=pk)
    cardname = pytils.translit.translify(note.equipment.exnumber[:5]) + ' ' +\
                pytils.translit.translify(note.charakters.name) +\
                ' ' + pytils.translit.translify(note.equipment.lot)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{cardname}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Основная информация', cell_overwrite_ok=True)

    ws.col(0).width = 2700
    ws.col(1).width = 2500
    ws.col(2).width = 8000
    ws.col(3).width = 3700
    ws.col(4).width = 2500
    ws.col(5).width = 4300
    ws.col(6).width = 4000
    ws.col(7).width = 4300
    ws.col(8).width = 2000
    ws.col(9).width = 2000


    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 26
        
    al1 = Alignment()
    al1.horz = Alignment.HORZ_CENTER
    al1.vert = Alignment.VERT_CENTER
        
    b1 = Borders()
    b1.left = 1
    b1.right = 1
    b1.bottom = 1
    b1.top = 1
        
    style1 = xlwt.XFStyle()
    style1.font.height = 9 * 20
    style1.font.name = 'Calibri'
    style1.alignment = al1
    style1.alignment.wrap = 1
    style1.borders = b1
        
    style2 = xlwt.XFStyle()
    style2.font.height = 9 * 20
    style2.font.name = 'Calibri'
    style2.alignment = al1
    style2.alignment.wrap = 1
    style2.borders = b1
    style2.pattern = pattern
        
        
    style3 = xlwt.XFStyle()
    style3.font.height = 15 * 20
    style3.font.bold = True
    style3.font.name = 'Calibri'
    style3.alignment = al1
    style3.alignment.wrap = 1
        
    style4 = xlwt.XFStyle()
    style4.font.height = 9 * 20
    style4.font.name = 'Calibri'
    style4.alignment = al1
    style4.alignment.wrap = 1
    style4.borders = b1
    style4.num_format_str = 'DD.MM.YYYY'
        
    style5 = xlwt.XFStyle()
    style5.font.height = 20 * 20
    style5.font.bold = True
    style5.font.name = 'Calibri'
    style5.alignment = al1
    style5.alignment.wrap = 1 

    # Image.open(company.imglogoadress_mini.path).convert("RGB").save('logo.bmp')
    # ws.insert_bitmap('logo.bmp', 0, 0)
    ws.left_margin = 0
    ws.header_str = b'&F c. &P  '
    ws.footer_str = b' '
    ws.start_page_number = 1



 

    # for row_num in range(4):
    #     for col_num in range(8):
    #         ws.row(row_num).height_mismatch = True
    #         ws.row(row_num).height = 500

    row_num = 4
    columns = [
        'Регистрационная карточка на СИ и ИО'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style5)
        ws.merge(row_num, row_num, 0, 9)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num = 5
    columns = [
        'Идентификационная и уникальная информация'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 9)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num = 7
    columns = [
        'Внутренний номер',
        'Наименование',
        'Наименование',
        'Тип/модификация',
        'Заводской номер',
        'Год выпуска',
        'Производитель',
        'Год ввода в эксплуатацию в ООО "Петроаналитика" ',
        'Новый или б/у',
        'Инвентарный номер',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 1, 2, style2)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1100

    row_num = 8
    columns = [
        note.equipment.exnumber[:5],
        note.charakters.name,
        note.charakters.name,
        f'{note.charakters.typename}',
        note.equipment.lot,
        note.equipment.yearmanuf,
        f'{note.equipment.manufacturer.country}, {note.equipment.manufacturer.companyName}',
        note.equipment.yearintoservice,
        note.equipment.new,
        note.equipment.invnumber,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 2, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1100

    row_num = 9
    columns = [
        'Расположение и комплектность'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 9)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num = 10
    columns = [
        'Документы, комплектные принадлежности, программное обеспечение',
        'Документы, комплектные принадлежности, программное обеспечение',
        'Документы, комплектные принадлежности, программное обеспечение',
        'Документы, комплектные принадлежности, программное обеспечение',
        'Ответственный за прибор',
        'Ответственный за прибор',
        'Расположение прибора',
        'Расположение прибора',
        'Расположение прибора',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 0, 4, style2)
        ws.merge(row_num, row_num, 5, 6, style2)
        ws.merge(row_num, row_num, 7, 9, style2)

    row_num = 11
    columns = [
        'год появления',
        'наименование документа/комплектной принадлежности/ПО',
        'наименование документа/комплектной принадлежности/ПО',
        'откуда поступил документ/ принадлежность/ПО',
        'откуда поступил документ/ принадлежность/ПО',
        'дата',
        'ответственный, ФИО',
        'дата',
        'номер комнаты',
        'номер комнаты',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 1, 2, style2)
        ws.merge(row_num, row_num, 3, 4, style2)
        ws.merge(row_num, row_num, 8, 9, style2)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    rows_1 = DocsCons.objects.filter(equipment=note.equipment). \
        values_list(
        'date',
        'docs',
        'docs',
        'source',
        'source',
    )
    rows_2 = Personchange.objects.filter(equipment=note.equipment). \
        values_list(
        'date',
        'person__profile__short_name',
    )

    rows_3 = Roomschange.objects.filter(equipment=note.equipment). \
        values_list(
        'date',
        'roomnumber__roomnumber',
    )


    for row in rows_1:
        row_num += 1
        for col_num in range(5):
            ws.write(row_num, col_num, row[col_num], style1)
            ws.merge(row_num, row_num, 1, 2, style2)
            ws.merge(row_num, row_num, 3, 4, style2)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500
    a = row_num

    row_num = 11
    for row in rows_2:
        row_num += 1
        for col_num in range(5, 7):
            ws.write(row_num, col_num, row[col_num - 5], style4)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500
    b = row_num


    row_num = 11
    for row in rows_3:
        row_num += 1
        for col_num in range(7, 9):
            ws.write(row_num, col_num, row[col_num - 7], style4)
            ws.merge(row_num, row_num, 8, 9, style4)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500
    c = row_num

    d = max(a, b, c)


    row_num = 24
    columns = [
        'Соответствие оборудования  установленным требованиям подтверждается протоколом верификации'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 0, 9, style2)

    ws1 = wb.add_sheet('Данные о ремонте и аттестации', cell_overwrite_ok=True)

    ws1.col(0).width = 1500
    ws1.col(1).width = 7000
    ws1.col(2).width = 1000
    ws1.col(3).width = 2400
    ws1.col(4).width = 2000
    ws1.col(5).width = 4000
    ws1.col(6).width = 14000
    ws1.col(7).width = 4000

    # Image.open(company.imglogoadress_mini.path).convert("RGB").save('logo.bmp')
    # ws1.insert_bitmap('logo.bmp', 0, 0)
    # ws1.left_margin = 0

    ws1.header_str = b'&F c. &P  '
    ws1.footer_str = b' '
    ws1.start_page_number = 2

    row_num = 4
    columns = [
        'Особенности работы прибора',
        'Особенности работы прибора',
        note.equipment.individuality,
        note.equipment.individuality,
        note.equipment.individuality,
        note.equipment.individuality,
        note.equipment.individuality,
    ]
    for col_num in range(2):
        ws1.write(row_num, col_num, columns[col_num], style2)
        ws1.merge(row_num, row_num, 0, 1, style2)
    for col_num in range(2, len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style1)
        ws1.merge(row_num, row_num, 2, 7, style1)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 2000


    row_num = 6
    columns = [
        'Поверка',
        'Поверка',
        '',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
        'Техническое обслуживание и данные о повреждениях, неисправностях, модификациях и ремонте',
    ]
    for col_num in range(2):
        ws1.write(row_num, col_num, columns[col_num], style2)
        ws1.merge(row_num, row_num, 0, 1, style2)
    for col_num in range(3, len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style2)
        ws1.merge(row_num, row_num, 3, 7, style2)

    row_num = 7
    columns = [
        'Год',
        'Сведения о результатах аттестации',
        '',
        'Дата',
        'Описание',
        'Описание',
        'Описание',
        'ФИО исполнителя',
    ]
    for col_num in range(2):
        ws1.write(row_num, col_num, columns[col_num], style2)
    for col_num in range(3, len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style2)
        ws1.merge(row_num, row_num, 4, 6, style2)


    rows_1 = Attestationequipment.objects.filter(equipmentSM__equipment=note.equipment). \
        annotate(ver=Concat(
        Value('Аттестат: \n  '),
        'certnumber',
        Value('\n от '), str('date'),
         Value('\n до '), str('datedead'),
        Value('\n выдан '),
        'verificator__companyName', output_field=CharField(),),
    ). \
        annotate(ver_year=Concat(
        'date__year', 'year',
         output_field=CharField(), ),
    ). \
        values_list(
        'ver_year',
        'ver',
    )

    rows_2 = CommentsEquipment.objects.filter(forNote=note.equipment). \
        values_list(
        'date',
        'note',
        'note',
        'note',
        'author',
    )

    for row in rows_1:
        row_num += 1
        for col_num in range(0, 1):
            ws1.write(row_num, col_num, row[col_num], style4)
        for col_num in range(1, 2):
            ws1.write(row_num, col_num, row[col_num], style4)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1500

    row_num = 7
    for row in rows_2:
        row_num += 1
        for col_num in range(3, 8):
            ws1.write(row_num, col_num, row[col_num - 3], style4)
            ws1.merge(row_num, row_num, 4, 6, style1)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1500

    wb.save(response)
    return response


# блок 4 - шаблоны для массовой загрузки приборов
def export_listE_xls(request):
    '''представление для выгрузки списка загруженных приборов с поверками, калибровками и аттестациями'''
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="vsyoLO.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws1 = wb.add_sheet('СИ', cell_overwrite_ok=True)
    ws2 = wb.add_sheet('ИО', cell_overwrite_ok=True)
    ws3 = wb.add_sheet('ВО', cell_overwrite_ok=True)
    ws1.header_str = b' '
    ws1.footer_str = b' '
    ws2.header_str = b' '
    ws2.footer_str = b' '
    ws3.header_str = b' '
    ws3.footer_str = b' '

    size = 11

    # ширина столбцов
    ws1.col(0).width = 3000
    ws1.col(1).width = 3000
    ws1.col(2).width = 3000
    ws1.col(3).width = 3000
    ws1.col(4).width = 3000
    ws1.col(5).width = 3000
    ws1.col(6).width = 3000
    ws1.col(7).width = 3000
    ws1.col(8).width = 3000
    ws1.col(9).width = 3000
    ws1.col(10).width = 3000
    ws1.col(11).width = 3000
    ws1.col(12).width = 3000
    ws1.col(13).width = 3000
    ws1.col(14).width = 3000
    ws1.col(15).width = 3000
    ws1.col(16).width = 3000
    ws1.col(17).width = 3000
    ws1.col(18).width = 3000
    ws1.col(19).width = 3000

    ws2.col(0).width = 3000
    ws2.col(1).width = 3000
    ws2.col(2).width = 3000
    ws2.col(3).width = 3000
    ws2.col(4).width = 3000
    ws2.col(5).width = 3000
    ws2.col(6).width = 3000
    ws2.col(7).width = 3000
    ws2.col(8).width = 3000
    ws2.col(9).width = 3000
    ws2.col(10).width = 3000
    ws2.col(11).width = 3000
    ws2.col(12).width = 3000
    ws2.col(13).width = 3000
    ws2.col(14).width = 3000
    ws2.col(15).width = 3000
    ws2.col(16).width = 3000
    ws2.col(17).width = 3000
    ws2.col(18).width = 3000
    ws2.col(19).width = 3000

    ws3.col(0).width = 3000
    ws3.col(1).width = 3000
    ws3.col(2).width = 3000
    ws3.col(3).width = 3000
    ws3.col(4).width = 3000
    ws3.col(5).width = 3000
    ws3.col(6).width = 3000
    ws3.col(7).width = 3000
    ws3.col(8).width = 3000
    ws3.col(9).width = 3000
    ws3.col(10).width = 3000
    ws3.col(11).width = 3000
    ws3.col(12).width = 3000
    ws3.col(13).width = 3000
    ws3.col(14).width = 3000
    ws3.col(15).width = 3000
    ws3.col(16).width = 3000
    ws3.col(17).width = 3000
    ws3.col(18).width = 3000
    ws3.col(19).width = 3000

    row_num = 1 
    columns = [
            'Название прибора',
            'Номер в Госреестре',
            'Тип/модификация',          
            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',           
            'Дата поверки',
            'Дата окончания поверки',
            'Ссылка на сведения о поверке в Аршин',
            'Номер свидетельства о поверке',
            'Название компании поверителя',            
            'Дата калибровки',
            'Дата окончания калибровки',
            'Номер сертификата калибровки',
            'Название компании поверителя',
        ]    
        
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 1500

    rows = MeasurEquipment.objects.filter(pointer=request.user.profile.userid).values_list('charakters__name',               
        'charakters__reestr',
        'charakters__typename',                
        'equipment__lot',
        'equipment__yearmanuf',
        'equipment__manufacturer__companyName',                
        'newdate',
        'newdatedead',
        'newarshin',
        'newcertnumber',
        'newverificator',
        'calnewdate',
        'calnewdatedead',
        'calnewcertnumber',
        'calnewverificator',
    )
        
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws1.write(row_num, col_num, row[col_num], style_plain_textf)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1500


    row_num = 1 
    columns = [
            'Название прибора',
            'Тип/модификация',          
            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',          
            'Дата аттестации',
            'Дата окончания аттестации',
            'Номер аттестата',
            'Название компании поверителя',
        ]    
        
    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws2.row(row_num).height_mismatch = True
    ws2.row(row_num).height = 1500

    rows = TestingEquipment.objects.filter(pointer=request.user.profile.userid).values_list('charakters__name',        
        'charakters__typename',               
        'equipment__lot',
        'equipment__yearmanuf',
        'equipment__manufacturer__companyName',               
        'newdate',
        'newdatedead',
        'newcertnumber',
        'newverificator',
    )
        
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws2.write(row_num, col_num, row[col_num], style_plain_textf)
        ws2.row(row_num).height_mismatch = True
        ws2.row(row_num).height = 1500        

    row_num = 1 
    columns = [
            'Название прибора',
            'Тип/модификация',
            
            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',
        ]    
        
    for col_num in range(len(columns)):
        ws3.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws3.row(row_num).height_mismatch = True
    ws3.row(row_num).height = 1500

    rows = HelpingEquipment.objects.filter(pointer=request.user.profile.userid).values_list('charakters__name',          
        'charakters__typename',
                
        'equipment__lot',
        'equipment__yearmanuf',
        'equipment__manufacturer__companyName',
    )
        
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws3.write(row_num, col_num, row[col_num], style_plain_textf)
        ws3.row(row_num).height_mismatch = True
        ws3.row(row_num).height = 1500         

    wb.save(response)
    return response


def export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3):
    '''шаблонное представление для выгрузки шаблонов файлов EXEL'''
        
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{exel_file_name}.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('1', cell_overwrite_ok=True)
    ws1 = wb.add_sheet('примеры и пояснения', cell_overwrite_ok=True)
    ws.header_str = b' '
    ws.footer_str = b' '

    size = 11

    # ширина столбцов
    ws.col(0).width = 3000
    ws.col(1).width = 3000
    ws.col(2).width = 3000
    ws.col(3).width = 3000
    ws.col(4).width = 3000
    ws.col(5).width = 3000
    ws.col(6).width = 3000
    ws.col(7).width = 3000
    ws.col(8).width = 3000
    ws.col(9).width = 3000
    ws.col(10).width = 3000
    ws.col(11).width = 3000
    ws.col(12).width = 3000
    ws.col(13).width = 3000
    ws.col(14).width = 3000
    ws.col(15).width = 3000
    ws.col(16).width = 3000
    ws.col(17).width = 3000
    ws.col(18).width = 3000
    ws.col(19).width = 3000

    ws1.col(0).width = 5000
    ws1.col(1).width = 5000
    ws1.col(2).width = 5000
    ws1.col(3).width = 5000
    ws1.col(4).width = 5000
    ws1.col(5).width = 5000
    ws1.col(6).width = 10000
    ws1.col(7).width = 5000
    ws1.col(8).width = 5000
    ws1.col(9).width = 5000
    ws1.col(10).width = 5000
    ws1.col(11).width = 5000
    ws1.col(12).width = 5000
    ws1.col(13).width = 5000
    ws1.col(14).width = 5000
    ws1.col(15).width = 5000
    ws1.col(16).width = 5000
    ws1.col(17).width = 5000
    ws1.col(18).width = 5000
    ws1.col(19).width = 5000


    row_num = 0 
    columns = columns1
    len_mandatory = len_mandatory
    for col_num in range(len_mandatory):
        ws.write(row_num, col_num, columns[col_num], style_bold_borders_blue)
    for col_num in range(len_mandatory, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 3000

    for col_num in range(len_mandatory):
        ws1.write(row_num, col_num, columns[col_num], style_bold_borders_blue)
    for col_num in range(len_mandatory, len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 3000

    row_num += 1
    columns = columns2
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 4000

    if columns4:
            row_num += 1
            columns = columns4
            for col_num in range(len(columns)):
                ws1.write(row_num, col_num, columns[col_num], style_plain_l)
                ws1.merge(row_num, row_num, 0, 20, style_plain_l)
            ws1.row(row_num).height_mismatch = True
            ws1.row(row_num).height = 1000

        
    row_num += 1
    columns = columns3
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 3000

        
    wb.save(response)
    return response


#индивидуальности блок 4

def export_MeasurEquipmentCharakters_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Характеристики СИ, '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="harakteristiki_SI_shablon"
    columns1 = [
            'Название прибора',
            'Номер в Госреестре',
            'Тип/модификация',
            'МежМетрологический интервал, месяцев',
            'Работает от сети (да - "1", нет - "0")',
            'Требуется установка (да - "1", нет - "0")',
            'Возможно тестирование  (да - "1", нет - "0")',
            'Класс точности /(разряд/), погрешность и /(или/) неопределённость /(класс, разряд/)',
            'Диапазон измерений',
            'напряжение',
            'частота',
            'температура',
            'влажность',
            'давление',
            'описание мероприятий по установке',
            'Где указана комплектация оборудования',
            'Информация о прослеживаемости (к какому эталону прослеживаются измерения на СИ)',
            'примечание',
            'виды измерений, тип (группа) средств измерений по МИ 2314',
        ]
    len_mandatory = 7
    columns2 =  [
            'Как на странице поверки на сайте "Аршин", но в единственном числе (либо как указано в вашем файле приборов)',
            'Как на странице поверки на сайте "Аршин"',
            'Как на странице поверки на сайте "Аршин", либо "-"',
            'Как на странице поверки на сайте "Аршин"',
            'Для протокола верификации: если "да" - то в протоколе верификации будет показана таблица с требуемыми параметрами электросети',
            '"да" - для крупных приборов, например: весы, "нет" - для приборов типа термометров',
            '"да" - если можно проверить правильность показаний прибора, например измерив на нем ГСО (пример - вискозиметр), и "нет" - если проверка невозможна  (пример - барометр). Результаты проверки отражаются в приложении к протоколу верификации вручную, так как из JL выгружается только общая страница протокола',
            'Первоисточник - описание типа, которое можно скачать с сайта "Аршин", перейдя по ссылке в разделе "Регистрационный номер типа СИ"',
            'Первоисточник - описание типа, которое можно скачать с сайта "Аршин", перейдя по ссылке в разделе "Регистрационный номер типа СИ"',
            'По описанию типа или паспорту, руководству',
            'По описанию типа или паспорту, руководству',
            'По описанию типа или паспорту, руководству',
            'По описанию типа или паспорту, руководству',
            'По описанию типа или паспорту, руководству',
            'Будет отображено в протоколе верификации, следует заполнить для приборов, требующих установки, лучше по сведениям из паспорта или руководства по эксплуатации. Пример: "Установлен на лабораторном столе по уровню, вдали от сквозняков"',
            'Обычно это страница паспорта или упаковочный лист',
            'Не обязательный столбец, который может пригодиться позднее при выгрузке разных форм на оборудование',
            '',
            'Не обязательный столбец, который может пригодиться позднее при выгрузке разных форм на оборудование. Например: форма Росаккредитации. Код по МИ 2314',
        ]
    columns4 = [
                    'Пример для характеристик прибора по ссылке https://fgis.gost.ru/fundmetrology/cm/results/1-248359087',
                ]
    columns3 = [
            'Термометр стеклянный',
            '63332-16',
            '127C/ASTM',
            '24',
            '0',
            '0',
            '0',
            '± 0,1 ℃',
            'от -21,4 до 18,6 ℃',
            '',
            '',
            '-',
            '-',
            '-',
            '',
            'Паспорт, стр.1',
            'гэт35-2010, гэт14-2014',
            '',
            '3201601',
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)


def export_TestingEquipmentCharakters_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Характеристики ИО, '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="harakteristiki_IO_shablon"
    columns1 = [
            'Название прибора',
            'Тип/модификация',
            'МежМетрологический интервал, месяцев',
            'Работает от сети (да - "1", нет - "0")',
            'Требуется установка (да - "1", нет - "0")',
            'Возможно тестирование  (да - "1", нет - "0")',
            

            'Основные технические характеристики',
            
            
            'напряжение',
            'частота',
            'температура',
            'влажность',
            'давление',
            
            'описание мероприятий по установке',
            'Где указана комплектация оборудования',
            'примечание',
        ]
    len_mandatory = 6
    columns2 =  [
            'Название как указано в руководстве по эксплуатации на прибор',
            'Модификация и тип как указано в руководстве по эксплуатации, либо "-"',
            'Как указано в первичном аттестате',
            'Для протокола верификации: если "да" - то в протоколе верификации будет показана таблица с требуемыми параметрами электросети',
            '"да" - для крупных приборов, например: термостат, "нет" - для приборов переносных',
            '"да" - если можно проверить правильность показаний прибора, и "нет" - если проверка невозможна. Результаты проверки отражаются в приложении к протоколу верификации вручную, так как из JL выгружается только общая страница протокола',
            

            '',
            
            
            'По паспорту, руководству',
            'По паспорту, руководству',
            'По паспорту, руководству',
            'По паспорту, руководству',
            'По паспорту, руководству',
            
            'Будет отображено в протоколе верификации, следует заполнить для приборов, требующих установки, лучше по сведениям из руководства по эксплуатации. Пример: "Установлен на лабораторном столе по уровню, вдали от сквозняков"',
            'Обычно это страница руководства по эксплуатации или упаковочный лист',
            '',
        ]
    columns4 = None
    columns3 = [
            'Электропечь сопротивления камерная лабораторная',
            'СНОЛ 6/12',
            '24',
            '1',
            '1',
            '0',
            

            'Рабочий температурный режим (250 - 900) ºС. Контролируемые параметры: 375±25 ºС, 775±25 ºС, 825±25 ºС',        
            
            '220 вольт',
            '50 Гц',
            '20+-5ºС',
            'от 20 до 80 %',
            '101 +- 10 мПа',
            'Установлен в вытяжном шакафу, положение отрегулировано по уровню',
            
            'Руководство по эксплуатации, стр.1',
            '',
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)


def export_HelpingEquipmentCharakters_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Характеристики ВО, '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="harakteristiki_VO_shablon"
    columns1 = [
            'Название прибора',
            'Тип/модификация',
            'Работает от сети (да - "1", нет - "0")',
            'Требуется установка (да - "1", нет - "0")',
            'Возможно тестирование  (да - "1", нет - "0")',
            
            'напряжение',
            'частота',
            'температура',
            'влажность',
            'давление',
            'описание мероприятий по установке',
            'Где указана комплектация оборудования',
            'примечание',
        ]
    len_mandatory = 5
    columns2 =  [
            'Название как указано в руководстве по эксплуатации на прибор',
            'Тип/модификация как указано в руководстве по эксплуатации, либо "-"',
            'Для протокола верификации: если "да" - то в протоколе верификации будет показана таблица с требуемыми параметрами электросети',
            '"да" - для крупных приборов, например: термостат, "нет" - для приборов переносных',
            '"да" - если можно проверить правильность показаний прибора, и "нет" - если проверка невозможна. Результаты проверки отражаются в приложении к протоколу верификации вручную, так как из JL выгружается только общая страница протокола',
            
            'По паспорту, руководству',
            'По паспорту, руководству',
            'По паспорту, руководству',
            'По паспорту, руководству',
            'По паспорту, руководству',
            
            'Будет отображено в протоколе верификации, следует заполнить для приборов, требующих установки, лучше по сведениям из паспорта или руководства по эксплуатации. Пример: "Установлен на лабораторном столе по уровню, вдали от сквозняков"',
            'Обычно это страница паспорта или упаковочный лист',
            '',
        ]
    columns4 = None
    columns3 = [
            'Плитка электрическая',
            'П-24/20 см диаметр',
            '1',
            '0',
            '0',
            
            '220 вольт',
            '50 Гц',
            '20+-5ºС',
            'от 20 до 80 %',
            '101 +- 10 мПа',
            '',
            
            'Руководство по эксплуатации, стр.1',
            '',
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)
        

def export_MeasurEquipment_Equipment_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Единица ЛО плюс единица СИ плюс комната плюс ответственный '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="MeasurEquipment_Equipment_shablon"
    columns1 = [
            'Название прибора',
            'Номер в Госреестре',
            'Тип/модификация',
            
            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',
            'Новый или б/у (указать: "новый" или "б/у")',
            'Указать "cобственность" или "аренда"',

            'Год ввода в эксплуатацию',
            'Статус: указать "Э" - эксплуатация, "РЕ" - ремонт, "Р" - резерв, "Д" - другое',
            'Включать в график ТО при автоформировании графика на год (да - "1", нет - "0")',

            'Стоимость (укажите "0" если стоимость неизвестна)', 
            'Инвентарный номер (присваивает бухгалтерия)',
            'Право владения прибором (например, номер и дата накладной)', 
                        
            'номер в качестве эталона в ФИФ, разряд по ГПС, ЛПС, и т. п.',

            'Номер комнаты в которой расположено ЛО',

            'Ответственный за оборудование (краткое ФИО сотрудника, например: "И.И.Иванов")',

            'Страна производителя',
            'Наименование определяемых (измеряемых) характеристик (параметров) продукции',
            
        ]
    len_mandatory = 5
    columns2 =  [
            'Как на странице поверки на сайте "Аршин", но в единственном числе (либо как указано в вашем файле приборов). Найдет характеристики СИ  среди добавленных на шаге 1 характеристик по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то добавит такие характеристики СИ ',
            'Как на странице поверки на сайте "Аршин". Найдет характеристики СИ  среди добавленных на шаге 1 характеристик по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то добавит такие характеристики СИ',
            'Как на странице поверки на сайте "Аршин", либо "-". Найдет характеристики СИ  среди добавленных на шаге 1 характеристик по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то добавит такие характеристики СИ',
            
            'Указан на самом приборе и в его паспорте',
            'Указан в паспорте',
            '',
            '',
            '',

            'Год когда прибор внесли в списки',
            '',
            'Если прибор не включен в график, то когда вы будете автоматически формировать график ТОиР на год - прибор в него не попадет',

            '', 
            '',
            'Эта информация требуется для некоторых форм для аккредитации', 
                        
            '',

            'Если такой комнаты в списке нет, то она добавится автоматически в список комнат',
            
            'Должно повторять краткое ФИО сотрудника (как в графе ФИО кратко (для документов)) в списке сотрудников. Если сотрудника с таким кратким ФИО нет, то информация не будет добавлена',

                   'Где выпущен прибор, расположена компания производителя',
            'для паспорта лаборатории по форме Росаккредитации',
        ]
    columns4 = None
    columns3 = [
            'Барометр-анероид метеорологический',
            '5738-76',
            'БАММ-1',
            
            '606',
            '2025',
            'ОАО "Сафоновский завод "Гидрометприбор"',
            'новый',
            'cобственность',

            '2025',
            'Э',
            '1',

            '0', 
            '',
            'Накладная №123 от 10.01.2025', 
              '',          
            '474',

            'И.И.Иванов',
            'Россия' ,
            
            'Измерение давления в помещениях'         
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)

def export_TestingEquipment_Equipment_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Единица ЛО плюс единица ИО плюс комната плюс ответственный '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="TestingEquipment_Equipment_shablon"
    columns1 = [
            'Название прибора',
            'Тип/модификация',
            
            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',
            'Новый или б/у (указать: "новый" или "б/у")',
            'Указать "cобственность" или "аренда"',

            'Год ввода в эксплуатацию',
            'Статус: указать "Э" - эксплуатация, "РЕ" - ремонт, "Р" - резерв, "Д" - другое',
            'Включать в график ТО при автоформировании графика на год (да - "1", нет - "0")',

            'Стоимость (укажите "0" если стоимость неизвестна)', 
            'Инвентарный номер (присваивает бухгалтерия)',
            'Право владения прибором (например, номер и дата накладной)', 

            'Номер комнаты в которой расположено ЛО',

            'Ответственный за оборудование (краткое ФИО сотрудника, например: "И.И.Иванов")',

                    'Страна производителя',
            'Наименование видов испытаний и/или определяемых характеристик (параметров) продукциии',
             'Наименование испытуемых групп объектов',
            
        ]
    len_mandatory = 4
    columns2 =  [
            'Название как указано в руководстве по эксплуатации на прибор (либо как указано в вашем файле приборов). Найдет характеристики ИО  среди добавленных на шаге 1 характеристик по сочетанию (точному совпадению): название, тип. Если не найдет, то добавит такие характеристики ИО ',
            'Как указано в руководстве по эксплуатации на прибор (либо как указано в вашем файле приборов), либо "-". Найдет характеристики ИО  среди добавленных на шаге 1 характеристик по сочетанию (точному совпадению): название, тип. Если не найдет, то добавит такие характеристики ИО',
          
            'Указан на самом приборе и в его паспорте (руководстве)',
            'Указан в паспорте (руководстве)',
            '',
            '',
            '',

            'Год когда прибор внесли в списки',
            '',
            'Если прибор не включен в график, то когда вы будете автоматически формировать график ТОиР на год - прибор в него не попадет',

            '', 
            '',
            '',

            'Если такой комнаты в списке нет, то она добавится автоматически в список комнат',

            'Должно повторять краткое ФИО сотрудника (как в графе ФИО кратко (для документов)) в списке сотрудников. Если сотрудника с таким кратким ФИО нет, то информация не будет добавлена',

                        'Где выпущен прибор, расположена компания производителя',
            'для паспорта лаборатории по форме Росаккредитации',
            'для паспорта лаборатории по форме Росаккредитации',
        
    ]
    columns4 = None
    columns3 = [
            'Термостат вискозиметрический',
            'ЛОИП-25',
            
            '606',
            '2025',
            'ОАО "ЛОИП"',
            'новый',
            'cобственность',

            '2025',
            'Э',
            '1',

            '0', 
            '',
            'Накладная №123 от 10.01.2025', 
                        
            '474',

            'И.И.Иванов',
            'Россия',

            'Измерение кинематической вязкости нефтепродуктов',
            'Нефть'
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)

def export_HelpingEquipment_Equipment_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Единица ЛО плюс единица ВО плюс комната плюс ответственный '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="HelpingEquipment_Equipment_shablon"
    columns1 = [
            'Название прибора',
            'Тип/модификация',
            
            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',
            'Новый или б/у (указать: "новый" или "б/у")',
            'Указать "cобственность" или "аренда"',

            'Год ввода в эксплуатацию',
            'Статус: указать "Э" - эксплуатация, "РЕ" - ремонт, "Р" - резерв, "Д" - другое',
            'Включать в график ТО при автоформировании графика на год (да - "1", нет - "0")',

            'Стоимость (укажите "0" если стоимость неизвестна)', 
            'Инвентарный номер (присваивает бухгалтерия)',
            'Право владения прибором (например, номер и дата накладной)', 

            'Номер комнаты в которой расположено ЛО',

            'Ответственный за оборудование (краткое ФИО сотрудника, например: "И.И.Иванов")',

                         'Страна производителя',

            'Назначение'
            
        ]
    len_mandatory = 4
    columns2 =  [
            'Название как указано в руководстве по эксплуатации на прибор (либо как указано в вашем файле приборов). Найдет характеристики ВО  среди добавленных на шаге 1 характеристик по сочетанию (точному совпадению): название, тип. Если не найдет, то добавит такие характеристики ИО ',
            'Как указано в руководстве по эксплуатации на прибор (либо как указано в вашем файле приборов), либо "-". Найдет характеристики ВО  среди добавленных на шаге 1 характеристик по сочетанию (точному совпадению): название, тип. Если не найдет, то добавит такие характеристики ИО',
          
            'Указан на самом приборе и в его паспорте (руководстве)',
            'Указан в паспорте (руководстве)',
            '',
            '',
            '',

            'Год когда прибор внесли в списки',
            '',
            'Если прибор не включен в график, то когда вы будете автоматически формировать график ТОиР на год - прибор в него не попадет',

            '', 
            '',
            '',

            'Если такой комнаты в списке нет, то она добавится автоматически в список комнат',

            'Должно повторять краткое ФИО сотрудника (как в графе ФИО кратко (для документов)) в списке сотрудников. Если сотрудника с таким кратким ФИО нет, то информация не будет добавлена',
                                    'Где выпущен прибор, расположена компания производителя',
            'для паспорта лаборатории по форме Росаккредитации',

        ]
    columns4 = None
    columns3 = [
            'Плитка электрическая',
            '-',
            
            '334Р',
            '2025',
            'ООО "Гефест"',
            'новый',
            'cобственность',

            '2025',
            'Э',
            '1',

            '0', 
            '',
            'Накладная №123 от 10.01.2025', 
                        

            '474',

            'И.И.Иванов',
            'Россия',
            'Приготовление растворов солей при нагревании'
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)


def export_Verificationequipment_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Поверка СИ '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="Verification_Equipment_shablon"
    columns1 = [
            'Название прибора',
            'Номер в Госреестре',
            'Тип/модификация',

            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',
            
            'Дата поверки',
            'Дата окончания поверки',
            
            'Номер свидетельства о поверке',
            'Название компании поверителя',
            'Статус поверки: выберите "Поверен", "Признан непригодным", "Спорный"',
            'Место поверки: выберите "У поверителя", "На месте эксплуатации"',
            'Заказана следующая поверка (или новое СИ): "1" - заказана, "0" - не заказана',
            'Поверку организует Поставщик: "1" - да, "0" - нет',
            'Ссылка на сведения о поверке в Аршин',

            'Дата заказа следующей поверки',
            'Дата заказа нового оборудования (если поверять не выгодно)',
            
            'Стоимость данной поверки',
                      
            'Выписка из сведений о поверке',            
        ]
    len_mandatory = 15
    columns2 =  [
            'Как на странице поверки на сайте "Аршин", но в единственном числе (либо как указано в вашем файле приборов). Найдет характеристики СИ  среди добавленных по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то запись не будет добавлена',
            'Как на странице поверки на сайте "Аршин". Найдет характеристики СИ  среди добавленных по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то запись не будет добавлена',
            'Как на странице поверки на сайте "Аршин", либо "-". Найдет характеристики СИ  среди добавленных по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то запись не будет добавлена',

            'Указан на самом приборе и в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            'Указан в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            'Указан в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            
            'Здесь и далее: даты должны быть в формате: гггг-мм-дд или дд.мм.гггг или дд.мм.гг или дд/мм/гггг или дд/мм/гг. Формат ячейки должен быть ТЕКСТОВЫЙ. Если в Вашем исходном файле датовый формат, то преобразуйте его так: 1)  в отдельном столбце введите формулу =ТЕКСТ(A2;"ГГГ-ММ-ДД")   где А2 - это ячейка с исходной датой. Потяните за правый уголок и сделайте это для всего столбца. 2) Скопируйте полученный столбец 3) Выделите место вставки, нажмите правой клавишой и выберите "специальная вставка - вставить значения - значения"',
            'см пояснение к ячейке G2',
            
            'Номер свидетельства о поверке (как в Аршин)',
            'Название компании поверителя (как в Аршин)',
            'выберите один из вариантов',
            'выберите один из вариантов',
            'выберите один из вариантов',
            'Например, если прибор куплен с поверкой или стоимость поверки неизвестна, то укажите здесь "1", если вы указываете стоимость поверки, то здесь укажите "0"',
            'Ссылка на сведения о поверке в Аршин',

            'см пояснение к ячейке G2',
            'см пояснение к ячейке G2',
            
            '',
                      
            'Здесь можно указать, например, поправки к показаниям барометра, термометра и др.', 
        ]
    columns4 = [
                    'Пример для поверки прибора по ссылке https://fgis.gost.ru/fundmetrology/cm/results/1-248359087',
                ]
    columns3 = [
            'Термометр стеклянный',
            '63332-16',
            'ASTM/127C',

            '2112',
            '2017',
            'Ludwig Schneider GmbH & Co. KG',
            
            '16.05.2023',
            '15.05.2025',
            
            'С-СП/16-05-2023/248359087',
            'ФБУ "ТЕСТ-С.-ПЕТЕРБУРГ"',
            'Поверен',
            'У поверителя',
            '0',
            '0',
            'https://fgis.gost.ru/fundmetrology/cm/results/1-248359087',

            '15.05.2025',
            '',
            
            '2500,33',
                      
            'Поправки к показаниям: при 10 град. + 0,1; при 20 град. + 0,2;', 
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)


def export_Calibrationequipment_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Калибровка СИ '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="Calibration_Equipment_shablon"
    columns1 = [
            'Название прибора',
            'Номер в Госреестре',
            'Тип/модификация',

            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',
            
            'Дата калибровки',
            'Дата окончания калибровки',
            
            'Номер сертификата калибровки',
            'Название компании поверителя',
            'Статус калибровки: выберите "Калиброван", "Признан непригодным", "Спорный"',
            'Место калибровки: выберите "У поверителя", "На месте эксплуатации"',
            'Заказана следующая калибровки (или новое СИ): "1" - заказана, "0" - не заказана',
            'Калибровку организует Поставщик: "1" - да, "0" - нет',
            'Ссылка на скан сертификата',

            'Дата заказа следующей калибровки',
            'Дата заказа нового оборудования (если калибровать не выгодно)',
            
            'Стоимость данной калибровки',
                      
            'Выписка из сертификата калибровки',            
        ]
    len_mandatory = 14
    columns2 =  [
            'Как на странице поверки на сайте "Аршин", но в единственном числе (либо как указано в вашем файле приборов). Найдет характеристики СИ  среди добавленных по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то запись не будет добавлена',
            'Как на странице поверки на сайте "Аршин". Найдет характеристики СИ  среди добавленных по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то запись не будет добавлена',
            'Как на странице поверки на сайте "Аршин", либо "-". Найдет характеристики СИ  среди добавленных по сочетанию (точному совпадению): название, номер, тип. Если не найдет, то запись не будет добавлена',

            'Указан на самом приборе и в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            'Указан в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            'Указан в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            
            'Здесь и далее: даты должны быть в формате: гггг-мм-дд или дд.мм.гггг или дд.мм.гг или дд/мм/гггг или дд/мм/гг. Формат ячейки должен быть ТЕКСТОВЫЙ. Если в Вашем исходном файле датовый формат, то преобразуйте его так: 1)  в отдельном столбце введите формулу =ТЕКСТ(A2;"ГГГ-ММ-ДД")   где А2 - это ячейка с исходной датой. Потяните за правый уголок и сделайте это для всего столбца. 2) Скопируйте полученный столбец 3) Выделите место вставки, нажмите правой клавишой и выберите "специальная вставка - вставить значения - значения"',
            'см пояснение к ячейке G2',
            
            'Номер сертификата калибровки, как на бумажном документе',
            'Название компании поверителя, как на бумажном документе',
            'выберите один из вариантов',
            'выберите один из вариантов',
            'выберите один из вариантов',
            'Например, если прибор куплен с калибровкой или стоимость калибровки неизвестна, то укажите здесь "1", если вы указываете стоимость калибровкой, то здесь укажите "0"',
            'Ссылка скан документа в облаке, где хранятся электронные документы Вашей компании',

            'см пояснение к ячейке G2',
            'см пояснение к ячейке G2',
            
            '',
                      
            'Здесь можно указать, например, поправки к показаниям барометра, термометра и др.', 
        ]
    columns4 = None
    columns3 = [
            'Термометр стеклянный',
            '63332-16',
            'ASTM/127C',

            '2112',
            '2017',
            'Ludwig Schneider GmbH & Co. KG',
            
            '16.05.2023',
            '15.05.2025',
            
            '221/248359087',
            'ФБУ "ТЕСТ-С.-ПЕТЕРБУРГ"',
            'Калиброван',
            'У поверителя',
            '0',
            '0',
            'https://fgis.gost.ru/fundmetrology/cm/results/1-248359087',

            '15.05.2025',
            '',
            
            '2500,33',
                      
            'Поправки к показаниям: при 10 град. + 0,1; при 20 град. + 0,2;', 
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)

def export_Attestationequipment_pattern_xls(request):
    '''представление для выгрузки шаблона загрузочного файла: Аттестация ИО '''
    '''основанное на шаблонном export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)'''
    exel_file_name="Attestation_Equipment_shablon"
    columns1 = [
            'Название прибора',
            'Тип/модификация',

            'Заводской номер',
            'Год выпуска',
            'Название компании-производителя',
            
            'Дата аттестации',
            'Дата окончания аттестации',
            
            'Номер аттестата',
            'Название компании поверителя',
            'Статус аттестации: выберите "Аттестован", "Признан непригодным", "Спорный"',
            'Место аттестации: выберите "У поверителя", "На месте эксплуатации"',
            'Заказана следующая аттестация (или новое ИО): "1" - заказана, "0" - не заказана',
            'Аттестацию организует Поставщик: "1" - да, "0" - нет',
            'Ссылка на скан аттестата',

            'Дата заказа следующей аттестации',
            'Дата заказа нового оборудования (если аттестовывать не выгодно)',
            
            'Стоимость данной аттестации',
                      
            'Выписка из аттестата',            
        ]
    len_mandatory = 13
    columns2 =  [
            'Как в документах на прибор (либо как указано в вашем файле приборов). Найдет характеристики ИО  среди добавленных по сочетанию (точному совпадению): название, тип. Если не найдет, то запись не будет добавлена',
            'Как в документах на прибор (либо как указано в вашем файле приборов), либо "-". Найдет характеристики ИО  среди добавленных по сочетанию (точному совпадению): название, тип. Если не найдет, то запись не будет добавлена',

            'Указан на самом приборе и в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            'Указан в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            'Указан в его паспорте (руководстве). Найдет прибор по точному совпадению: заводской номер, год выпуска, название компании-производителя. Если не найдет, то запись не будет добавлена',
            
            'Здесь и далее: даты должны быть в формате: гггг-мм-дд или дд.мм.гггг или дд.мм.гг или дд/мм/гггг или дд/мм/гг. Формат ячейки должен быть ТЕКСТОВЫЙ. Если в Вашем исходном файле датовый формат, то преобразуйте его так: 1)  в отдельном столбце введите формулу =ТЕКСТ(A2;"ГГГ-ММ-ДД")   где А2 - это ячейка с исходной датой. Потяните за правый уголок и сделайте это для всего столбца. 2) Скопируйте полученный столбец 3) Выделите место вставки, нажмите правой клавишой и выберите "специальная вставка - вставить значения - значения"',
            'см пояснение к ячейке F2',
            
            'Номер аттестата, как на бумажном документе',
            'Название компании поверителя, как на бумажном документе',
            'выберите один из вариантов',
            'выберите один из вариантов',
            'выберите один из вариантов',
            'Например, если прибор куплен с аттестацией или стоимость аттестации неизвестна, то укажите здесь "1", если вы указываете стоимость калибровкой, то здесь укажите "0"',
            'Ссылка скан документа в облаке, где хранятся электронные документы Вашей компании',

            'см пояснение к ячейке F2',
            'см пояснение к ячейке F2',
            
            '',
                      
            'Здесь можно указать, например, ГОСТы и температуры на которые аттестован прибор', 
        ]
    columns4 = None
    columns3 = [
            'Термостат вискозиметрический',
            'ЛОИП-1',

            '456',
            '2017',
            'ООО "ЛОИП"',
            
            '16.05.2023',
            '15.05.2025',
            
            '221/248359087',
            'ФБУ "ТЕСТ-С.-ПЕТЕРБУРГ"',
            'Аттестован',
            'У поверителя',
            '0',
            '0',
            '',

            '15.05.2025',
            '',
            
            '2500,33',
                      
            'ГОСТ 33, темературы: 20, 25, 40, 50, 80, 100 градусов', 
        ]
    return export_base_pattern_xls(request, exel_file_name, columns1, len_mandatory, columns2, columns4, columns3)



def export_ServiceME_pattern_xls(request):
    '''представление для выгрузки списка характеристик СИ и загрузки к ним описания ТО'''
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="TO_SI.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws1 = wb.add_sheet('СИ', cell_overwrite_ok=True)
    ws1.header_str = b' '
    ws1.footer_str = b' '

    size = 11

    # ширина столбцов
    ws1.col(0).width = 3000
    ws1.col(1).width = 3000
    ws1.col(2).width = 3000
    ws1.col(3).width = 6000
    ws1.col(4).width = 6000
    ws1.col(5).width = 6000
    ws1.col(6).width = 6000

    row_num = 0 
    columns = [
            'Название прибора',
            'Номер в Госреестре',
            'Тип/модификация',                   
            'Объем технического обслуживания ТО 0',
            'Объем технического обслуживания ТО 1',
            'Объем технического обслуживания ТО 2',
            'Комментарий к постоянным особенностям ТО',
        ]    
        
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 1500

    rows = MeasurEquipmentCharakters.objects.filter(pointer=request.user.profile.userid).values_list('name',               
        'reestr',
        'typename',                
    )
        
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws1.write(row_num, col_num, row[col_num], style_plain_textf)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1500

    wb.save(response)
    return response

def export_ServiceTE_pattern_xls(request):
    '''представление для выгрузки списка характеристик ИО и загрузки к ним описания ТО'''
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="TO_IO.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws1 = wb.add_sheet('ИО', cell_overwrite_ok=True)
    ws1.header_str = b' '
    ws1.footer_str = b' '

    size = 11

    # ширина столбцов
    ws1.col(0).width = 3000
    ws1.col(1).width = 3000
    ws1.col(2).width = 6000
    ws1.col(3).width = 6000
    ws1.col(4).width = 6000
    ws1.col(5).width = 6000
    ws1.col(6).width = 6000


    row_num = 0 
    columns = [
            'Название прибора',
            'Тип/модификация',                   
            'Объем технического обслуживания ТО 0',
            'Объем технического обслуживания ТО 1',
            'Объем технического обслуживания ТО 2',
            'Комментарий к постоянным особенностям ТО',
        ]    
        
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 1500

    rows = TestingEquipmentCharakters.objects.filter(pointer=request.user.profile.userid).values_list('name',        
        'typename',               
    )
        
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws1.write(row_num, col_num, row[col_num], style_plain_textf)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1500        

    wb.save(response)
    return response


def export_ServiceHE_pattern_xls(request):
    '''представление для выгрузки списка характеристик ВО и загрузки к ним описания ТО'''
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="TO_VO.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws1 = wb.add_sheet('ВО', cell_overwrite_ok=True)
    ws1.header_str = b' '
    ws1.footer_str = b' '

    size = 11

    # ширина столбцов
    ws1.col(0).width = 3000
    ws1.col(1).width = 3000
    ws1.col(2).width = 6000
    ws1.col(3).width = 6000
    ws1.col(4).width = 6000
    ws1.col(5).width = 6000
    ws1.col(6).width = 6000

    row_num = 0 
    columns = [
            'Название прибора',
            'Тип/модификация',  
            'Объем технического обслуживания ТО 0',
            'Объем технического обслуживания ТО 1',
            'Объем технического обслуживания ТО 2',
            'Комментарий к постоянным особенностям ТО',
        ]    
        
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_plain_textf)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 1500

    rows = HelpingEquipmentCharakters.objects.filter(pointer=request.user.profile.userid).values_list('name',          
        'typename',                
    )    
        
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws1.write(row_num, col_num, row[col_num], style_plain_textf)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 1500
            
    wb.save(response)
    return response


# блок 5 - нестандартные exel выгрузки (этикетки, протоколы верификации, карточка) 

# стили для exel (для этикеток)
brd1 = Borders()
brd1.left = 1
brd1.right = 1
brd1.top = 1
brd1.bottom = 1

al_cb = Alignment()
al_cb.horz = Alignment.HORZ_CENTER
al_cb.vert = Alignment.VERT_BOTTOM

style1 = xlwt.XFStyle()
style1.font.bold = True
style1.font.name = 'Calibri'
style1.borders = brd1
style1.alignment = al_cb
style1.alignment.wrap = 1

style2 = xlwt.XFStyle()
style2.font.name = 'Calibri'
style2.borders = brd1
style2.alignment = al_cb

style3 = xlwt.XFStyle()
style3.font.name = 'Calibri'
style3.alignment = al_cb

style4 = xlwt.XFStyle()
style4.font.bold = True
style4.font.name = 'Calibri'
style4.alignment = al_cb

# флаг этикетки СИ
def export_verificlabel_xls(request):
    '''представление для выгрузки этикеток для указания поверки и аттестации'''
    note = []
    company = Company.objects.get(userid=request.user.profile.userid)
    ruser=request.user.profile.userid
    for n in (request.GET['n1'], request.GET['n2'],
              request.GET['n3'], request.GET['n4'],
              request.GET['n5'], request.GET['n6'],
              request.GET['n7'], request.GET['n8'],
              request.GET['n9'], request.GET['n10'],
              request.GET['n11'], request.GET['n12'],
              request.GET['n13'], request.GET['n14']):
                      
        n = n + '_' + str(company.pk)
        try:
            MeasurEquipment.objects.filter(pointer=ruser).get(equipment__exnumber=n)
            note.append(MeasurEquipment.objects.filter(pointer=ruser).get(equipment__exnumber=n))
        except:
            pass
        try:
            TestingEquipment.objects.filter(pointer=ruser).get(equipment__exnumber=n)
            note.append(TestingEquipment.objects.filter(pointer=ruser).get(equipment__exnumber=n))
        except:    
            pass


    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="verification_labels.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('1', cell_overwrite_ok=True)
    ws.header_str = b' '
    ws.footer_str = b' '

    # ширина столбцов
    ws.col(0).width = 300
    ws.col(1).width = 3400
    ws.col(2).width = 3600
    ws.col(3).width = 2000
    ws.col(4).width = 2000
    ws.col(5).width = 800
    ws.col(6).width = 3400
    ws.col(7).width = 3600
    ws.col(8).width = 2000
    ws.col(9).width = 2000
    ws.col(10).width = 300


    i = 0
    j = 0
    if len(note) % 2 != 0:
        note.append(note[0])
    while i <= len(note) - 2:
        currentnote1 = note[i]
        currentnote2 = note[i + 1]

        row_num = 0 + j
        columns = [
            '',
            f'{currentnote1.charakters.name} {currentnote1.charakters.typename}',
            f'{currentnote1.charakters.name} {currentnote1.charakters.typename}',
            f'{currentnote1.charakters.name} {currentnote1.charakters.typename}',
            f'{currentnote1.charakters.name} {currentnote1.charakters.typename}',
            '',
            f'{currentnote2.charakters.name} {currentnote2.charakters.typename}',
            f'{currentnote2.charakters.name} {currentnote2.charakters.typename}',
            f'{currentnote2.charakters.name} {currentnote2.charakters.typename}',
            f'{currentnote2.charakters.name} {currentnote2.charakters.typename}',
            '',
        ]

        for col_num in (1, 2, 3, 4, 6, 7, 8, 9):
            ws.write(row_num, col_num, columns[col_num], style2)
            ws.merge(row_num, row_num, 1, 4, style2)
            ws.merge(row_num, row_num, 6, 9, style2)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 750

        row_num = 1 + j
        columns = [
            '',
            f'Заводской №:',
            f'{currentnote1.equipment.lot}',
            f'Внут. №',
            f'{str(currentnote1.equipment.exnumber)[:5]}',
            '',
            f'Заводской №:',
            f'{currentnote2.equipment.lot}',
            f'Внут. №',
            f'{str(currentnote2.equipment.exnumber)[:5]}',
            '',
        ]

        for col_num in (1, 3, 6, 8):
            ws.write(row_num, col_num, columns[col_num], style1)
        for col_num in (2, 4, 7, 9):
            ws.write(row_num, col_num, columns[col_num], style2)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 270

        if currentnote1.equipment.kategory == 'СИ':
            a = 'поверка:'
        if currentnote1.equipment.kategory == 'ИО':
            a = 'аттестация:'
        if currentnote2.equipment.kategory == 'СИ':
            b = 'поверка:'
        if currentnote2.equipment.kategory == 'ИО':
            b = 'аттестация:'

        row_num = 2 + j
        columns = [
            '',
            f'{a}',
            f'{currentnote1.newcertnumber}',
            f'{currentnote1.newcertnumber}',
            f'{currentnote1.newcertnumber}',
            '',
            f'{b}',
            f'{currentnote2.newcertnumber}',
            f'{currentnote2.newcertnumber}',
            f'{currentnote2.newcertnumber}',
            '',
        ]

        for col_num in (1, 6):
            ws.write(row_num, col_num, columns[col_num], style1)
        for col_num in range(2, 5):
            ws.write(row_num, col_num, columns[col_num], style2)
        for col_num in range(7, 10):
            ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 2, 4, style2)
        ws.merge(row_num, row_num, 7, 9, style2)

        if currentnote1.equipment.kategory == 'СИ':
            a = 'поверен'
        if currentnote1.equipment.kategory == 'ИО':
            a = 'аттестован'
        if currentnote2.equipment.kategory == 'СИ':
            b = 'поверен'
        if currentnote2.equipment.kategory == 'ИО':
            b = 'аттестован'

        row_num = 3 + j
        columns = [
            '',
            f'{a} от {currentnote1.newdate} до {currentnote1.newdatedead}',
            f'{a} от {currentnote1.newdate} до {currentnote1.newdatedead}',
            f'{a} от {currentnote1.newdate} до {currentnote1.newdatedead}',
            f'{a} от {currentnote1.newdate} до {currentnote1.newdatedead}',
            ' ',
            f'{b} от {currentnote2.newdate} до {currentnote2.newdatedead}',
            f'{b} от {currentnote2.newdate} до {currentnote2.newdatedead}',
            f'{b} от {currentnote2.newdate} до {currentnote2.newdatedead}',
            f'{b} от {currentnote2.newdate} до {currentnote2.newdatedead}',
            ' ',
            ]
        for col_num in range(1, 5):
            ws.write(row_num, col_num, columns[col_num], style2)
        for col_num in range(6, 10):
            ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 1, 4, style1)
        ws.merge(row_num, row_num, 6, 9, style1)

        if currentnote1.equipment.kategory == 'СИ':
            a = 'поверку'
        if currentnote1.equipment.kategory == 'ИО':
            a = 'аттест-ю:'
        if currentnote2.equipment.kategory == 'СИ':
            b = 'поверку'
        if currentnote2.equipment.kategory == 'ИО':
            b = 'аттест-ю'

        responser = f'Ответственный за {a} {"              "} {company.manager_name}'
            
        row_num = 4 + j
        columns = [
            '',
            responser,
            responser,
            responser,
            responser,
            ' ',
            responser,
            responser,
            responser,
            responser,
            ' ',
        ]
        for col_num in range(1, 5):
            ws.write(row_num, col_num, columns[col_num], style2)
        for col_num in range(6, 10):
            ws.write(row_num, col_num, columns[col_num], style2)
        ws.merge(row_num, row_num, 1, 4, style1)
        ws.merge(row_num, row_num, 6, 9, style1)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 400

        row_num = 5 + j
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 370

        i += 2
        j += 6

    wb.save(response)
    return response


# флаг верифик
def export_exvercard_xls(request, pk):
    '''представление для выгрузки протокола верификации СИ в ексель'''
    note = MeasurEquipment.objects.get(pk=pk)
    company = Company.objects.get(userid=request.user.profile.userid)
    try:
        # room = Roomschange.objects.filter(equipment__exnumber=note.equipment.exnumber)
        # room = room.last().roomnumber
        room = note.equipment.newroomnumber
    except:
        room = 'не указано'
    try:
        # q = Personchange.objects.filter(equipment__exnumber=note.equipment.exnumber)
        # usere = q.last().person.profile.short_name
        usere = note.equipment.newperson
        # position = q.last().person.position
    except:
        usere = ''
    try:
        p = Profile.objects.get(name=usere)
        position = p.userposition
    except:
        position = ''
        
 
    userelat = pytils.translit.translify(usere)
    cardname = pytils.translit.translify(str(note.equipment.exnumber)[:5]) + ' ' + pytils.translit.translify(note.equipment.lot)
    response = HttpResponse(content_type='application/ms-excel')
    filename = f"{userelat}_{cardname}"
    filename = str(filename)
    filename = filename[:251]

    response['Content-Disposition'] = f'attachment; filename="{filename}.xls"'
    # response['Content-Disposition'] = f'attachment; filename="{cardname}.xls"'
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 0x0D

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Протокол верификации СИ', cell_overwrite_ok=True)

    ws.col(0).width = 2600
    ws.col(1).width = 2500
    ws.col(2).width = 7900
    ws.col(3).width = 3700
    ws.col(4).width = 2500
    ws.col(5).width = 2400
    ws.col(6).width = 3600


    # Image.open(company.imglogoadress_mini.path).convert("RGB").save('logo.bmp')
    # ws.insert_bitmap('logo.bmp', 0, 0)
    # ws.left_margin = 0
    ws.header_str = b'  '
    ws.footer_str = b'c. &P '
    ws.start_page_number = 1

    al1 = Alignment()
    al1.horz = Alignment.HORZ_CENTER
    al1.vert = Alignment.VERT_CENTER

    b1 = Borders()
    b1.left = 1
    b1.right = 1
    b1.bottom = 1
    b1.top = 1

    b5 = Borders()
    b5.left = 5
    b5.right = 5
    b5.bottom = 5
    b5.top = 5

    style1 = xlwt.XFStyle()
    style1.font.height = 9 * 20
    style1.font.name = 'Times new roman'
    style1.alignment = al1
    style1.alignment.wrap = 1
    style1.borders = b1

    style10 = xlwt.XFStyle()
    style10.font.height = 12 * 20
    style10.font.name = 'Times new roman'
    style10.alignment = al1
    style10.alignment.wrap = 1

    style110 = xlwt.XFStyle()
    style110.font.height = 12 * 20
    style110.font.name = 'Times new roman'
    style110.alignment = al1
    style110.alignment.wrap = 1
    style110.pattern = pattern

    style11 = xlwt.XFStyle()
    style11.font.height = 9 * 20
    style11.font.name = 'Times new roman'
    style11.alignment = al1
    style11.alignment.wrap = 1
    style11.borders = b1
    style11.pattern = pattern

    style111 = xlwt.XFStyle()
    style111.font.height = 12 * 20
    style111.font.name = 'Times new roman'
    style111.alignment = al1
    style111.alignment.wrap = 1
    style111.borders = b1

    style2 = xlwt.XFStyle()
    style2.font.height = 9 * 20
    style2.font.name = 'Times new roman'
    style2.alignment = al1
    style2.alignment.wrap = 1
    style2.borders = b1
    style2.pattern = pattern

    style3 = xlwt.XFStyle()
    style3.font.height = 11 * 20
    style3.font.bold = True
    style3.font.name = 'Times new roman'
    style3.alignment = al1
    style3.alignment.wrap = 1

    style4 = xlwt.XFStyle()
    style4.font.height = 9 * 20
    style4.font.name = 'Times new roman'
    style4.alignment = al1
    style4.alignment.wrap = 1
    style4.borders = b1
    style4.num_format_str = 'DD.MM.YYYY'

    style5 = xlwt.XFStyle()
    style5.font.height = 12 * 20
    style5.font.bold = True
    style5.font.name = 'Times new roman'
    style5.alignment = al1
    style5.alignment.wrap = 1

    dateverificformat = now
    dateverific = get_dateformat(now)
    row_num = 1
    columns = [
        f'Протокол верификации № {note.pk}/{str(now.year)[2:4]} от {dateverific} г. СИ вн.№ {str(note.equipment.exnumber)[:5]}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style5)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num +=1
    columns = [
        '1. Идентификационная и уникальная информация'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num +=2
    columns = [
        'Внутренний номер',
        'Номер в госреестре',
        'Наименование',
        'Тип/модификация',
        'Заводской номер',
        'Год выпуска',
        'Производитель',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1100


    row_num +=1
    columns = [
        f'СИ {str(note.equipment.exnumber)[:5]}',
        note.charakters.reestr,
        note.charakters.name,
        f'{note.charakters.typename}',
        note.equipment.lot,
        note.equipment.yearmanuf,
        f'{note.equipment.manufacturer.country}, {note.equipment.manufacturer.companyName}',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1100

    row_num += 2
    columns = [
        'Диапазон измерений',
        'Диапазон измерений',
        'Диапазон измерений',
        'Класс точности, погрешность и/или неопределённость',
        'Класс точности, погрешность и/или неопределённость',
        'Класс точности, погрешность и/или неопределённость',
        'Класс точности, погрешность и/или неопределённость',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 3, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700

    row_num += 1
    columns = [
        note.charakters.measurydiapason,
        note.charakters.measurydiapason,
        note.charakters.measurydiapason,
        note.charakters.accuracity,
        note.charakters.accuracity,
        note.charakters.accuracity,
        note.charakters.accuracity,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 3, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1500

    row_num +=2
    columns = [
        '2. Верификация комплектности и установки оборудования'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num +=1
    columns = [
        '2.1 Соответствие комплектности'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num +=1
    columns = [
        'Наименование',
        'Наименование',
        'Наименование',
        'Оценка',
        'Примечание',
        'Примечание',
        'Примечание',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 4, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.complectlist != '':
        a = note.charakters.complectlist
        st = style1
    else:
        a = 'упаковочный лист'
        st = style11


    row_num += 1
    columns = [
        'Комплектация',
        'Комплектация',
        'Комплектация',
        'cоответствует',
        a,
        a,
        a,
    ]
    for col_num in range(4):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
    for col_num in range(4, len(columns)):
        ws.write(row_num, col_num, columns[col_num], st)
        ws.merge(row_num, row_num, 4, 6, st)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    b = note.equipment.exnumber

    try:
        c = DocsCons.objects.filter(equipment__exnumber=b)
        d = c.filter(docs__icontains='аспорт')
        d = d[0]
        a = 'в наличии'
    except:
        a = 'отсутствует'


    row_num +=1
    columns = [
        'Паспорт',
        'Паспорт',
        'Паспорт',
        a,
        '',
        '',
        '',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 4, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    try:
        c = DocsCons.objects.filter(equipment__exnumber=b)
        d = c.filter(Q(docs__icontains='уководство')|Q(docs__icontains='нструкция')|Q(docs__icontains='ИНСТРУКЦИЯ')|Q(docs__icontains='аспорт'))
        d = d[0]
        a = 'в наличии'
        e = ''
    except:
        a = 'отсутствует'
        e = 'необходимо разработать инструкцию на оборудование (так как в списке документов к оборудованию отсутствует документ с названием "Руководство", "Инструкция" или "Паспорт)"'

    row_num += 1
    columns = [
        'Руководство по эксплуатации',
        'Руководство по эксплуатации',
        'Руководство по эксплуатации',
        a,
        e,
        e,
        e,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 4, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 1
    columns = [
        'Сведения о поверке',
        'Сведения о поверке',
        'Сведения о поверке',
        f'поверен до {note.newdatedead}',
        f'№ {note.newcertnumber}',
        f'№ {note.newcertnumber}',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 4, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500


    try:
        microclimat = MeteorologicalParameters.objects.get(roomnumber__roomnumber=room, date=dateverificformat)
        facttemperature = microclimat.temperature
        facthumid = microclimat.humidity
        factpress = microclimat.pressure
    except:
        facttemperature = 'указать'
        facthumid = 'указать'
        factpress = 'указать'

    row_num +=2
    columns = [
        f'2.2 Соответствие  требованиям к условиям эксплуатации в помещении № {room}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 1
    columns = [
        'Наименование характеристики',
        'Наименование характеристики',
        'Требования руководства по эксплуатации, паспорта или описания типа',
        'Состояние на момент верификации',
        'Состояние на момент верификации',
        'Оценка',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 1, style1)
        ws.merge(row_num, row_num, 3, 4, style1)
        ws.merge(row_num, row_num, 5, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.power == True:
        row_num += 1
        columns = [
            'Соответствие требованиям к  электропитанию'
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style1)
            ws.merge(row_num, row_num, 0, 6, style1)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500

        if note.charakters.voltage == '':
            note.charakters.voltage = '-'
            st = style11
        else:
            st = style1

        row_num += 1
        columns = [
            'Напряжение питания сети, В',
            'Напряжение питания сети, В',
            note.charakters.voltage,
            '220',
            '220',
            'соответствует',
        ]
        for col_num in range(3):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 0, 1, st)
        for col_num in range(3, len(columns)):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 3, 4, st)
            ws.merge(row_num, row_num, 5, 6, st)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500

        if note.charakters.frequency == '':
            note.charakters.frequency = '-'
            st = style11
        else:
            st = style1

        row_num += 1
        columns = [
            'Частота, Гц',
            'Частота, Гц',
            note.charakters.frequency,
            '50',
            '50',
            'соответствует',
        ]
        for col_num in range(3):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 0, 1, st)
        for col_num in range(3, len(columns)):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 3, 4, st)
            ws.merge(row_num, row_num, 5, 6, st)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500

    row_num += 1
    columns = [
        'Соответствие требованиям к  микроклимату'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.temperature == '':
        note.charakters.temperature = '-'
        st1 = style11
    else:
        st1 = style1
    if facttemperature == 'указать':
        st3 = style11
    else:
        st3 = style1


    row_num += 1
    columns = [
        'Диапазон рабочих температур, °С',
        'Диапазон рабочих температур, °С',
        note.charakters.temperature,
        facttemperature,
        facttemperature,
        'соответствует',
    ]
    for col_num in range(3):
        ws.write(row_num, col_num, columns[col_num], st1)
        ws.merge(row_num, row_num, 0, 1, st1)
    for col_num in range(3, len(columns)):
        ws.write(row_num, col_num, columns[col_num], st3)
        ws.merge(row_num, row_num, 3, 4, st3)
        ws.merge(row_num, row_num, 5, 6, st3)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.humidicity == '':
        note.charakters.humidicity = '-'
        st1 = style11
    else:
        st1 = style1
    if facthumid == 'указать':
        st3 = style11
    else:
        st3 = style1

    row_num += 1
    columns = [
        'Относительная влажность воздуха, %',
        'Относительная влажность воздуха, %',
        note.charakters.humidicity,
        facthumid,
        facthumid,
        'соответствует',
    ]
    for col_num in range(3):
        ws.write(row_num, col_num, columns[col_num], st1)
        ws.merge(row_num, row_num, 0, 1, st1)
    for col_num in range(3, len(columns)):
        ws.write(row_num, col_num, columns[col_num], st3)
        ws.merge(row_num, row_num, 3, 4, st3)
        ws.merge(row_num, row_num, 5, 6, st3)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.pressure == '':
        note.charakters.pressure = '-'
        st1 = style11
    else:
        st1 = style1

    if factpress == 'указать':
        st3 = style11
    else:
        st3 = style1

    row_num += 1
    columns = [
        'Атмосферное давление, кПа',
        'Атмосферное давление, кПа',
        note.charakters.pressure,
        factpress,
        factpress,
        'соответствует',
    ]
    for col_num in range(3):
        ws.write(row_num, col_num, columns[col_num], st1)
        ws.merge(row_num, row_num, 0, 1, st1)
    for col_num in range(3, len(columns)):
        ws.write(row_num, col_num, columns[col_num], st3)
        ws.merge(row_num, row_num, 3, 4, st3)
        ws.merge(row_num, row_num, 5, 6, st3)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '2.3 Соответствие  установки на рабочем месте требованиям документации на оборудование'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.needsetplace:
        a = ''
        b = '✓'
    if not note.charakters.needsetplace:
        a = '✓'
        b = ''


    row_num += 1
    columns = [
        a,
        'Установка не требуется'
    ]
    for col_num in range(0, 1):
        ws.write(row_num, col_num, columns[col_num], style111)
    for col_num in range(1, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700


    row_num += 1
    columns = [
        b,
        'Требуется установка'
    ]
    for col_num in range(0, 1):
        ws.write(row_num, col_num, columns[col_num], style111)
    for col_num in range(1, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700

    if note.charakters.needsetplace:
        if not note.charakters.setplace:
            st = style11
        else:
            st = style1


        row_num += 2
        columns = [
            'Описание установки'
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style3)
            ws.merge(row_num, row_num, 0, 6)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500


        row_num += 1
        columns = [
              note.charakters.setplace
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 0, 6, st)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '3. Тестирование при внедрении оборудования'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.expresstest:
        a = ''
        b = '✓'
    if not note.charakters.expresstest:
        a = '✓'
        b = ''

    row_num += 1
    columns = [
        a,
        'Тестирование невозможно'
    ]
    for col_num in range(0, 1):
        ws.write(row_num, col_num, columns[col_num], style111)
    for col_num in range(1, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700

    row_num += 1
    columns = [
        b,
        'Тестирование возможно. Результаты испытаний в приложении 1'

    ]
    for col_num in range(0, 1):
        ws.write(row_num, col_num, columns[col_num], style111)
    for col_num in range(1, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700

    row_num += 2
    columns = [
        '4. Заключение по результатам верификации'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500


    row_num += 1
    columns = [
        f'Пригодно к эксплуатации.  Требования к установке и условиям окружающей среды соответствуют документации на оборудование.\
        \n Закреплено за помещением № {room}.\n Закреплено за ответственным пользователем: {usere}.'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1500

    row_num += 2
    columns = [
        '',
        '',
        f'Верификацию провел:'
        '',
        '',
        '',
        '',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        position,
        '',
       usere,
       usere,
       usere,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
        ws.merge(row_num, row_num, 4, 6, style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        'Согласовано:'
        '',
        '',
        '',
        '',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        f'{company.headlab_position}'
        '',
        '',
        f'{company.headlab_name}',
        f'{company.headlab_name}',
        f'{company.headlab_name}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
        ws.merge(row_num, row_num, 4, 6, style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        f'{company.caretaker_position}',
        '',
        f'{company.caretaker_name}',
        f'{company.caretaker_name}',
        f'{company.caretaker_name}',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
        ws.merge(row_num, row_num, 4, 6, style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        f'{company.manager_position}',
        '',
        f'{company.manager_name}',
        f'{company.manager_name}',
        f'{company.manager_name}',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
        ws.merge(row_num, row_num, 4, 6, style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    wb.save(response)
    return response

# флаг верификация ио
def export_exvercardteste_xls(request, pk):
    '''представление для выгрузки протокола верификации ИО в ексель'''
    company = Company.objects.get(userid=request.user.profile.userid)
    note = TestingEquipment.objects.get(pk=pk)

    try:
        # room = Roomschange.objects.filter(equipment__exnumber=note.equipment.exnumber)
        # room = room.last().roomnumber
        room = note.equipment.newroomnumber
    except:
        room = 'не указано'
    try:
        # q = Personchange.objects.filter(equipment__exnumber=note.equipment.exnumber)
        # usere = q.last().person.profile.short_name
        usere = note.equipment.newperson
        # position = q.last().person.position
    except:
        usere = ''
    try:
        p = Profile.objects.get(name=usere)
        position = p.userposition
    except:
        position = ''
    userelat = pytils.translit.translify(usere)
    cardname = pytils.translit.translify(note.equipment.exnumber[:5]) + ' ' + pytils.translit.translify(note.equipment.lot)
    response = HttpResponse(content_type='application/ms-excel')
    filename = f"{userelat}_{cardname}"
    filename = str(filename)
    filename = filename[:251]

    response['Content-Disposition'] = f'attachment; filename="{filename}.xls"'
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    pattern.pattern_fore_colour = 0x0D

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Протокол верификации ИО', cell_overwrite_ok=True)

    ws.col(0).width = 2600
    ws.col(1).width = 2500
    ws.col(2).width = 7900
    ws.col(3).width = 3700
    ws.col(4).width = 2500
    ws.col(5).width = 2400
    ws.col(6).width = 3600


    # Image.open(company.imglogoadress_mini.path).convert("RGB").save('logo.bmp')
    # ws.insert_bitmap('logo.bmp', 0, 0)
    ws.left_margin = 0
    ws.header_str = b'  '
    ws.footer_str = b'c. &P '
    ws.start_page_number = 1

    al1 = Alignment()
    al1.horz = Alignment.HORZ_CENTER
    al1.vert = Alignment.VERT_CENTER

    b1 = Borders()
    b1.left = 1
    b1.right = 1
    b1.bottom = 1
    b1.top = 1

    b5 = Borders()
    b5.left = 5
    b5.right = 5
    b5.bottom = 5
    b5.top = 5

    style1 = xlwt.XFStyle()
    style1.font.height = 9 * 20
    style1.font.name = 'Times new roman'
    style1.alignment = al1
    style1.alignment.wrap = 1
    style1.borders = b1

    style10 = xlwt.XFStyle()
    style10.font.height = 12 * 20
    style10.font.name = 'Times new roman'
    style10.alignment = al1
    style10.alignment.wrap = 1

    style110 = xlwt.XFStyle()
    style110.font.height = 12 * 20
    style110.font.name = 'Times new roman'
    style110.alignment = al1
    style110.alignment.wrap = 1
    style110.pattern = pattern

    style11 = xlwt.XFStyle()
    style11.font.height = 9 * 20
    style11.font.name = 'Times new roman'
    style11.alignment = al1
    style11.alignment.wrap = 1
    style11.borders = b1
    style11.pattern = pattern

    style111 = xlwt.XFStyle()
    style111.font.height = 12 * 20
    style111.font.name = 'Times new roman'
    style111.alignment = al1
    style111.alignment.wrap = 1
    style111.borders = b1

    style2 = xlwt.XFStyle()
    style2.font.height = 9 * 20
    style2.font.name = 'Times new roman'
    style2.alignment = al1
    style2.alignment.wrap = 1
    style2.borders = b1
    style2.pattern = pattern

    style3 = xlwt.XFStyle()
    style3.font.height = 11 * 20
    style3.font.bold = True
    style3.font.name = 'Times new roman'
    style3.alignment = al1
    style3.alignment.wrap = 1

    style4 = xlwt.XFStyle()
    style4.font.height = 9 * 20
    style4.font.name = 'Times new roman'
    style4.alignment = al1
    style4.alignment.wrap = 1
    style4.borders = b1
    style4.num_format_str = 'DD.MM.YYYY'

    style5 = xlwt.XFStyle()
    style5.font.height = 12 * 20
    style5.font.bold = True
    style5.font.name = 'Times new roman'
    style5.alignment = al1
    style5.alignment.wrap = 1

    dateverificformat = now
    dateverific = get_dateformat(now)
    row_num = 4
    columns = [
        f'Протокол верификации № {note.equipment.exnumber[:5]}_01/22 от {dateverific} г. ИО вн.№ {note.equipment.exnumber[:5]}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style5)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num = 5
    columns = [
        '1. Идентификационная и уникальная информация'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num +=2
    columns = [
        'Внутренний номер',
        'Наименование',
        'Наименование',
        'Тип/модификация',
        'Заводской номер',
        'Год выпуска',
        'Производитель',
        # 'Год ввода в эксплуатацию в ООО "Петроаналитика" ',
        # 'Новый или б/у',
        # 'Инвентарный номер',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 2, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1100


    row_num +=1
    columns = [
        f'ИО {str(note.equipment.exnumber)[:5]}', 
        note.charakters.name,
        note.charakters.name,
        f'{note.charakters.typename}',
        note.equipment.lot,
        note.equipment.yearmanuf,
        f'{note.equipment.manufacturer.country}, {note.equipment.manufacturer.companyName}',
        # note.equipment.yearintoservice,
        # note.equipment.new,
        # note.equipment.invnumber,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 2, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1100

    row_num += 2
    columns = [
        'Основные технические характеристики',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700

    row_num += 1
    columns = [
        note.charakters. main_technical_characteristics,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1700

    row_num +=2
    columns = [
        '2. Верификация комплектности и установки оборудования'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num +=1
    columns = [
        '2.1 Соответствие комплектности'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num +=1
    columns = [
        'Наименование',
        'Наименование',
        'Наименование',
        'Оценка',
        'Примечание',
        'Примечание',
        'Примечание',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 4, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.complectlist != '':
        a = note.charakters.complectlist
        st = style1
    else:
        a = 'упаковочный лист'
        st = style11


    row_num += 1
    columns = [
        'Комплектация',
        'Комплектация',
        'Комплектация',
        'cоответствует',
        a,
        a,
        a,
    ]
    for col_num in range(4):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
    for col_num in range(4, len(columns)):
        ws.write(row_num, col_num, columns[col_num], st)
        ws.merge(row_num, row_num, 4, 6, st)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    b = note.equipment.exnumber

    try:
        c = DocsCons.objects.filter(equipment__exnumber=b)
        d = c.filter(docs__icontains='аспорт')
        d = d[0]
        a = 'в наличии'
    except:
        a = 'отсутствует'


    row_num +=1
    columns = [
        'Паспорт',
        'Паспорт',
        'Паспорт',
        a,
        '',
        '',
        '',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 4, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    try:
        c = DocsCons.objects.filter(equipment__exnumber=b)
        d = c.filter(Q(docs__icontains='уководство')|Q(docs__icontains='нструкция')|Q(docs__icontains='ИНСТРУКЦИЯ')|Q(docs__icontains='аспорт'))
        d = d[0]
        a = 'в наличии'
        e = ''
    except:
        a = 'отсутствует'
        e = 'необходимо разработать инструкцию на оборудование (так как в списке документов к оборудованию отсутствует документ с названием "Руководство", "Инструкция" или "Паспорт)"'

    row_num += 1
    columns = [
        'Руководство по эксплуатации',
        'Руководство по эксплуатации',
        'Руководство по эксплуатации',
        a,
        e,
        e,
        e,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 4, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 1
    columns = [
        'Сведения об аттестации',
        'Сведения об аттестации',
        'Сведения об аттестации',
        f'аттестован до {note.newdatedead}',
        f'№ {note.newcertnumber}',
        f'№ {note.newcertnumber}',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 2, style1)
        ws.merge(row_num, row_num, 4, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500


    try:
        microclimat = MeteorologicalParameters.objects.get(roomnumber__roomnumber=room, date=dateverificformat)
        facttemperature = microclimat.temperature
        facthumid = microclimat.humidity
        factpress = microclimat.pressure
    except:
        facttemperature = 'указать'
        facthumid = 'указать'
        factpress = 'указать'




    row_num +=2
    columns = [
        f'2.2 Соответствие  требованиям к условиям эксплуатации в помещении № {room}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 1
    columns = [
        'Наименование характеристики',
        'Наименование характеристики',
        'Требования руководства по эксплуатации, паспорта или описания типа',
        'Состояние на момент верификации',
        'Состояние на момент верификации',
        'Оценка',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 1, style1)
        ws.merge(row_num, row_num, 3, 4, style1)
        ws.merge(row_num, row_num, 5, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.power == True:
        row_num += 1
        columns = [
            'Соответствие требованиям к  электропитанию'
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style1)
            ws.merge(row_num, row_num, 0, 6, style1)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500

        if note.charakters.voltage == '':
            note.charakters.voltage = '-'
            st = style11
        else:
            st = style1



        row_num += 1
        columns = [
            'Напряжение питания сети, В',
            'Напряжение питания сети, В',
            note.charakters.voltage,
            '220',
            '220',
            'соответствует',
        ]
        for col_num in range(3):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 0, 1, st)
        for col_num in range(3, len(columns)):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 3, 4, st)
            ws.merge(row_num, row_num, 5, 6, st)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500

        if note.charakters.frequency == '':
            note.charakters.frequency = '-'
            st = style11
        else:
            st = style1

        row_num += 1
        columns = [
            'Частота, Гц',
            'Частота, Гц',
            note.charakters.frequency,
            '50',
            '50',
            'соответствует',
        ]
        for col_num in range(3):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 0, 1, st)
        for col_num in range(3, len(columns)):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 3, 4, st)
            ws.merge(row_num, row_num, 5, 6, st)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500

    row_num += 1
    columns = [
        'Соответствие требованиям к  микроклимату'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.temperature == '':
        note.charakters.temperature = '-'
        st1 = style11
    else:
        st1 = style1
    if facttemperature == 'указать':
        st3 = style11
    else:
        st3 = style1


    row_num += 1
    columns = [
        'Диапазон рабочих температур, °С',
        'Диапазон рабочих температур, °С',
        note.charakters.temperature,
        facttemperature,
        facttemperature,
        'соответствует',
    ]
    for col_num in range(3):
        ws.write(row_num, col_num, columns[col_num], st1)
        ws.merge(row_num, row_num, 0, 1, st1)
    for col_num in range(3, len(columns)):
        ws.write(row_num, col_num, columns[col_num], st3)
        ws.merge(row_num, row_num, 3, 4, st3)
        ws.merge(row_num, row_num, 5, 6, st3)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.humidicity == '':
        note.charakters.humidicity = '-'
        st1 = style11
    else:
        st1 = style1
    if facthumid == 'указать':
        st3 = style11
    else:
        st3 = style1

    row_num += 1
    columns = [
        'Относительная влажность воздуха, %',
        'Относительная влажность воздуха, %',
        note.charakters.humidicity,
        facthumid,
        facthumid,
        'соответствует',
    ]
    for col_num in range(3):
        ws.write(row_num, col_num, columns[col_num], st1)
        ws.merge(row_num, row_num, 0, 1, st1)
    for col_num in range(3, len(columns)):
        ws.write(row_num, col_num, columns[col_num], st3)
        ws.merge(row_num, row_num, 3, 4, st3)
        ws.merge(row_num, row_num, 5, 6, st3)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.pressure == '':
        note.charakters.pressure = '-'
        st1 = style11
    else:
        st1 = style1

    if factpress == 'указать':
        st3 = style11
    else:
        st3 = style1

    row_num += 1
    columns = [
        'Атмосферное давление, кПа',
        'Атмосферное давление, кПа',
        note.charakters.pressure,
        factpress,
        factpress,
        'соответствует',
    ]
    for col_num in range(3):
        ws.write(row_num, col_num, columns[col_num], st1)
        ws.merge(row_num, row_num, 0, 1, st1)
    for col_num in range(3, len(columns)):
        ws.write(row_num, col_num, columns[col_num], st3)
        ws.merge(row_num, row_num, 3, 4, st3)
        ws.merge(row_num, row_num, 5, 6, st3)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '2.3 Соответствие  установки на рабочем месте требованиям документации на оборудование'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.needsetplace:
        a = ''
        b = '✓'
    if not note.charakters.needsetplace:
        a = '✓'
        b = ''


    row_num += 1
    columns = [
        a,
        'Установка не требуется'
    ]
    for col_num in range(0, 1):
        ws.write(row_num, col_num, columns[col_num], style111)
    for col_num in range(1, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700


    row_num += 1
    columns = [
        b,
        'Требуется установка'
    ]
    for col_num in range(0, 1):
        ws.write(row_num, col_num, columns[col_num], style111)
    for col_num in range(1, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700

    if note.charakters.needsetplace:
        if not note.charakters.setplace:
            st = style11
        else:
            st = style1


        row_num += 2
        columns = [
            'Описание установки'
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style3)
            ws.merge(row_num, row_num, 0, 6)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500


        row_num += 1
        columns = [
              note.charakters.setplace
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], st)
            ws.merge(row_num, row_num, 0, 6, st)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 500



    row_num += 2
    columns = [
        '3. Тестирование при внедрении оборудования'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    if note.charakters.expresstest:
        a = ''
        b = '✓'
    if not note.charakters.expresstest:
        a = '✓'
        b = ''

    row_num += 1
    columns = [
        a,
        'Тестирование невозможно'
    ]
    for col_num in range(0, 1):
        ws.write(row_num, col_num, columns[col_num], style111)
    for col_num in range(1, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700

    row_num += 1
    columns = [
        b,
        'Тестирование возможно. Результаты испытаний в приложении 1'

    ]
    for col_num in range(0, 1):
        ws.write(row_num, col_num, columns[col_num], style111)
    for col_num in range(1, len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 1, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 700

    row_num += 2
    columns = [
        '4. Заключение по результатам верификации'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style3)
        ws.merge(row_num, row_num, 0, 6)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500


    row_num += 1
    columns = [
        f'Пригодно к эксплуатации.  Требования к установке и условиям окружающей среды соответствуют документации на оборудование.\
        \n Закреплено за помещением № {room}.\n Закреплено за ответственным пользователем: {usere}.'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style1)
        ws.merge(row_num, row_num, 0, 6, style1)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1500

    row_num += 2
    columns = [
        '',
        '',
        'Верификацию провел:'
        '',
        '',
        '',
        '',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        position,
        '',
       usere,
       usere,
       usere,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
        ws.merge(row_num, row_num, 4, 6, style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        'Согласовано:'
        '',
        '',
        '',
        '',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        f'{company.headlab_position}'
        '',
        '',
        f'{company.headlab_name}',
        f'{company.headlab_name}',
        f'{company.headlab_name}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
        ws.merge(row_num, row_num, 4, 6, style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        f'{company.caretaker_position}',
        '',
        f'{company.caretaker_name}',
        f'{company.caretaker_name}',
        f'{company.caretaker_name}',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
        ws.merge(row_num, row_num, 4, 6, style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    row_num += 2
    columns = [
        '',
        '',
        f'{company.manager_position}',
        '',
        f'{company.manager_name}',
        f'{company.manager_name}',
        f'{company.manager_name}',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style10)
        ws.merge(row_num, row_num, 4, 6, style10)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 500

    wb.save(response)
    return response

# блок 6 - ТОиР
# Ниже будут быгрузки ексель для переноса в LabBook
# Поэтому: для удобства стили все далаем заново. В лаббуке стили с такими же названиями вынесены в файл exelbase
# но! кроме размера шрифта - он 11!

# размер шрифта
size = 11

def get_rows_service_shedule(request, row_num, ws, MODEL, to3, equipment_type, MODEL2, MODEL3, MODEL4, MODEL5, year_search):
    """создает и пересчитывает строки графика для класса выгрузки поверки(ниже):  MODEL = тип ЛО (СИ, ИО, ВО); MODEL2 = ServiceEquipment...; """
    """MODEL3 = поверка/аттестация; MODEL4 = ServiceEquipmentU...MODEL5 = ServiceEquipmentUFact... и MODEL6 это план ТО добавлена на перспективу"""

    company = Company.objects.get(userid=request.user.profile.userid) 
    affirmation = f'УТВЕРЖДАЮ \n{company.direktor_position}\n{company.name}\n____________/{company.direktor_name}/\n«__» ________20__ г.'     
    row_num += 1
    columns = [
        f'{equipment_type}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_bold_borders)
        ws.merge(row_num, row_num, 0, 19, style_bold_borders)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 600

    for note in MODEL:
        try:
            person = Personchange.objects.filter(equipment__pk=note.equipment.pk).order_by('pk').last().person.name
        except:
            person = 'Ответственный за метрологическое обеспечение'

        try:
            note2 = MODEL2.objects.get(charakters__pk=note.charakters.pk)
            descriptiont0 = note2.descriptiont0
            descriptiont1 = note2.descriptiont1
            descriptiont2 = note2.descriptiont2
            if note2.descriptiont0:
                to0_shed = 'ежедневно'
            else:
                to0_shed = ' '
            if note2.descriptiont1:
                to1_shed = 'ежемесячно'
            else:
                to1_shed = ' '
        except:
            descriptiont0 = ' '
            descriptiont1 = ' '
            descriptiont2 = ' '
            to0_shed = ''
            to1_shed = ''

        try:
            note4 = MODEL4.objects.get(equipment__pk=note.equipment.pk)
            commentservice = note4.commentservice
            if note4.t2month1 == True:
                t2month1 = 'V'
            else:
                t2month1 = ' '
            if note4.t2month2 == True:
                t2month2 = 'V'
            else:
                t2month2 = ' '
            if note4.t2month3 == True:
                t2month3 = 'V'
            else:
                t2month3 = ' '
            if note4.t2month4 == True:
                t2month4 = 'V'
            else:
                t2month4 = ' '
            if note4.t2month5 == True:
                t2month5 = 'V'
            else:
                t2month5 = ' '
            if note4.t2month6 == True:
                t2month6 = 'V'
            else:
                t2month6 = ' '
            if note4.t2month7 == True:
                t2month7 = 'V'
            else:
                t2month7 = ' '
            if note4.t2month8 == True:
                t2month8 = 'V'
            else:
                t2month8 = ' '
            if note4.t2month9 == True:
                t2month9 = 'V'
            else:
                t2month9 = ' '
            if note4.t2month10 == True:
                t2month10 = 'V'
            else:
                t2month10 = ' '
            if note4.t2month11 == True:
                t2month11 = 'V'
            else:
                t2month11 = ' '
            if note4.t2month12 == True:
                t2month12 = 'V'
            else:
                t2month12 = ' '
        except:
            commentservice = ' '
            t2month1 = ''
            t2month2 = ''
            t2month3 = ''
            t2month4 = ''
            t2month5 = ''
            t2month6 = ''
            t2month7 = ''
            t2month8 = ''
            t2month9 = ''
            t2month10 = ''
            t2month11 = ''
            t2month12 = ''

        try:
            note5 = MODEL5.objects.get(equipment__pk=note.equipment.pk)
            if note5.t2month1 == True:
                t2month1f = 'V'
            else:
                t2month1f = ' '
            if note5.t2month2 == True:
                t2month2f = 'V'
            else:
                t2month2f = ' '
            if note5.t2month3 == True:
                t2month3f = 'V'
            else:
                t2month3f = ' '
            if note5.t2month4 == True:
                t2month4f = 'V'
            else:
                t2month4f = ' '
            if note5.t2month5 == True:
                t2month5f = 'V'
            else:
                t2month5f = ' '
            if note5.t2month6 == True:
                t2month6f = 'V'
            else:
                t2month6f = ' '
            if note5.t2month7 == True:
                t2month7f = 'V'
            else:
                t2month7f = ' '
            if note5.t2month8 == True:
                t2month8f = 'V'
            else:
                t2month8f = ' '
            if note5.t2month9 == True:
                t2month9f = 'V'
            else:
                t2month9f = ' '
            if note5.t2month10 == True:
                t2month10f = 'V'
            else:
                t2month10f = ' '
            if note5.t2month11 == True:
                t2month11f = 'V'
            else:
                t2month11f = ' '
            if note5.t2month12 == True:
                t2month12f = 'V'
            else:
                t2month12f = ' '
        except:
            t2month1f = ''
            t2month2f = ''
            t2month3f = ''
            t2month4f = ''
            t2month5f = ''
            t2month6f = ''
            t2month7f = ''
            t2month8f = ''
            t2month9f = ''
            t2month10f = ''
            t2month11f = ''
            t2month12f = ''

            
        t3month1 = ''
        t3month2 = ''
        t3month3 = ''
        t3month4 = ''
        t3month5 = ''
        t3month6 = ''
        t3month7 = ''
        t3month8 = ''
        t3month9 = ''
        t3month10 = ''
        t3month11 = ''
        t3month12 = ''
        t3month1f = ''
        t3month2f = ''
        t3month3f = ''
        t3month4f = ''
        t3month5f = ''
        t3month6f = ''
        t3month7f = ''
        t3month8f = ''
        t3month9f = ''
        t3month10f = ''
        t3month11f = ''
        t3month12f = ''

        # подставляем месяц плана поверки/аттестации/проверки
        if to3:
            try:
                note3 = MODEL3.objects.filter(equipmentSM__equipment__pk=note.equipment.pk).exclude(
                dateorder__isnull=True)

                q = note3.get(dateorder__year=year_search)
                t3month = int(q.dateorder.month)

                if t3month == 1:
                    t3month1 = 'V'
                if t3month == 2:
                    t3month2 = 'V'
                if t3month == 3:
                    t3month3 = 'V'
                if t3month == 4:
                    t3month4 = 'V'
                if t3month == 5:
                    t3month5 = 'V'
                if t3month == 6:
                    t3month6 = 'V'
                if t3month == 7:
                    t3month7 = 'V'
                if t3month == 8:
                    t3month8 = 'V'
                if t3month == 9:
                    t3month9 = 'V'
                if t3month == 10:
                    t3month10 = 'V'
                if t3month == 11:
                    t3month11 = 'V'
                if t3month == 12:
                    t3month12 = 'V'
            except:
                t3month1 = ''
                t3month2 = ''
                t3month3 = ''
                t3month4 = ''
                t3month5 = ''
                t3month6 = ''
                t3month7 = ''
                t3month8 = ''
                t3month9 = ''
                t3month10 = ''
                t3month11 = ''
                t3month12 = ''

        #  подставляем месяц факта поверки/аттестации/проверки
            try:
                note3 = MODEL3.objects.filter(equipmentSM__equipment__pk=note.equipment.pk).exclude(
                    date__isnull=True)
                q = note3.get(date__year=year_search)
                t3monthf = int(q.date.month)

                if t3monthf == 1:
                    t3month1f = 'V'
                if t3monthf == 2:
                    t3month2f = 'V'
                if t3monthf == 3:
                    t3month3f = 'V'
                if t3monthf == 4:
                    t3month4f = 'V'
                if t3monthf == 5:
                    t3month5f = 'V'
                if t3monthf == 6:
                    t3month6f = 'V'
                if t3monthf == 7:
                    t3month7f = 'V'
                if t3monthf == 8:
                    t3month8f = 'V'
                if t3monthf == 9:
                    t3month9f = 'V'
                if t3monthf == 10:
                    t3month10f = 'V'
                if t3monthf == 11:
                    t3month11f = 'V'
                if t3monthf == 12:
                    t3month12f = 'V'
            except:
                t3month1f = ''
                t3month2f = ''
                t3month3f = ''
                t3month4f = ''
                t3month5f = ''
                t3month6f = ''
                t3month7f = ''
                t3month8f = ''
                t3month9f = ''
                t3month10f = ''
                t3month11f = ''
                t3month12f = ''

        row_num += 1
        columns = [
            '',
            f'{note.charakters.name}, {note.charakters.typename}',
            f'{note.charakters.name}, {note.charakters.typename}',
            f'{note.exnumber}',
            f'{note.equipment.lot}',
            '',
            'январь',
            'февраль',
            'март',
            'апрель',
            'май',
            'июнь',
            'июль',
            'август',
            'сентябрь',
            'октябрь',
            'ноябрь',
            'декабрь',
            f'{person}',
            f'{commentservice}',
        ]
        for col_num in range(7):
            ws.write(row_num, col_num, columns[col_num], style_plain)
            ws.merge(row_num, row_num, 1, 2, style_plain)
            ws.merge(row_num, row_num + 1, 6, 6, style_plain)
        for col_num in range(6, 18):
            ws.write(row_num, col_num, columns[col_num], style_plain_90)
            ws.merge(row_num, row_num + 1, 7, 7, style_plain_90)
            ws.merge(row_num, row_num + 1, 8, 8, style_plain_90)
            ws.merge(row_num, row_num + 1, 9, 9, style_plain_90)
            ws.merge(row_num, row_num + 1, 10, 10, style_plain_90)
            ws.merge(row_num, row_num + 1, 11, 11, style_plain_90)
            ws.merge(row_num, row_num + 1, 12, 12, style_plain_90)
            ws.merge(row_num, row_num + 1, 13, 13, style_plain_90)
            ws.merge(row_num, row_num + 1, 14, 14, style_plain_90)
            ws.merge(row_num, row_num + 1, 15, 15, style_plain_90)
            ws.merge(row_num, row_num + 1, 16, 16, style_plain_90)
            ws.merge(row_num, row_num + 1, 17, 17, style_plain_90)
        for col_num in range(18, len(columns)):
            ws.write(row_num, col_num, columns[col_num], style_plain)
            ws.merge(row_num, row_num + 5, 18, 18, style_plain)
            ws.merge(row_num, row_num + 7, 19, 19, style_plain)
            ws.merge(row_num, row_num + 3, 5, 5, style_plain)
            ws.merge(row_num, row_num + 6, 0, 0, style_plain)
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 2400


        row_num += 1
        columns = [
            '',
            'Тип ТО',
            'Объем технического обслуживания',
            '',
            '',
            '',
            'январь',
            'февраль',
            'март',
            'апрель',
            'май',
            'июнь',
            'июль',
            'август',
            'сентябрь',
            'октябрь',
            'ноябрь',
            'декабрь',
            f'{person}',
            f'{commentservice}',
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style_plain)
            ws.merge(row_num, row_num, 2, 4, style_plain)
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 500

        row_num += 1
        columns = [
            '',
            f'ТО 0',
            f'{descriptiont0}',
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            to0_shed,
            f'{person}',
            f'{commentservice}',
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style_plain)
            ws.merge(row_num, row_num, 2, 4, style_plain)
            ws.merge(row_num, row_num, 6, 17, style_plain)
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 2500

        row_num += 1
        columns = [
            '',
            f'ТО 1',
            f'{descriptiont1}',
            '',
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            to1_shed,
            f'{person}',
            f'{commentservice}',
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style_plain)
            ws.merge(row_num, row_num, 2, 4, style_plain)
            ws.merge(row_num, row_num, 6, 17, style_plain)
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 2500

        row_num += 1
        columns = [
            '',
            f'ТО 2',
            f'{descriptiont2}',
            f'{descriptiont2}',
            f'{descriptiont2}',
            'план',
            t2month1,
            t2month2,
            t2month3,
            t2month4,
            t2month5,
            t2month6,
            t2month7,
            t2month8,
            t2month9,
            t2month10,
            t2month11,
            t2month12,
            f'{person}',
            f'{commentservice}',
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style_plain)
            ws.merge(row_num, row_num + 1, 1, 1, style_plain)
            ws.merge(row_num, row_num + 1, 2, 4, style_plain)
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 1300

        row_num += 1
        columns = [
            '',
            f'ТО 2',
            f'{descriptiont2}',
            f'{descriptiont2}',
            f'{descriptiont2}',
            'факт',
            t2month1f,
            t2month2f,
            t2month3f,
            t2month4f,
            t2month5f,
            t2month6f,
            t2month7f,
            t2month8f,
            t2month9f,
            t2month10f,
            t2month11f,
            t2month12f,
            f'{person}',
            f'',
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style_plain)

            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 1300

        if to3:
            row_num += 1
            columns = [
                '',
                f'ТО 3',
                f'{to3}',
                f'{to3}',
                f'{to3}',
                'план',
                t3month1,
                t3month2,
                t3month3,
                t3month4,
                t3month5,
                t3month6,
                t3month7,
                t3month8,
                t3month9,
                t3month10,
                t3month11,
                t3month12,
                f'Ответственный за метрологическое обеспечение',
                f'{commentservice}',
                ]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], style_plain)
                ws.merge(row_num, row_num, 2, 4, style_plain)
                ws.merge(row_num, row_num + 1, 1, 1, style_plain)
                ws.merge(row_num, row_num + 1, 2, 4, style_plain)
                ws.merge(row_num, row_num + 1, 18, 18, style_plain)
                ws.row(row_num).height_mismatch = True
                ws.row(row_num).height = 1300

            row_num += 1
            columns = [
                '',
                f'ТО 3',
                f'{to3}',
                f'{to3}',
                f'{to3}',
                'факт',
                t3month1f,
                t3month2f,
                t3month3f,
                t3month4f,
                t3month5f,
                t3month6f,
                t3month7f,
                t3month8f,
                t3month9f,
                t3month10f,
                t3month11f,
                t3month12f,
                f'Ответственный за метрологическое обеспечение',
                f'{commentservice}',
                ]
            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], style_plain)
                ws.merge(row_num, row_num, 2, 4, style_plain)
                ws.row(row_num).height_mismatch = True
                ws.row(row_num).height = 1300

        row_num += 1
        columns = [
            ''
        ]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], style_black)
            ws.merge(row_num, row_num, 0, 19, style_black)
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 40
    return row_num

# график тоир техобслуживания
def export_maintenance_schedule_xls(request):
    """представление для выгрузки графика ТО на указанную дату"""
    company = Company.objects.get(userid=request.user.profile.userid)
    affirmation = f'УТВЕРЖДАЮ \n{company.direktor_position}\n{company.name}\n____________/{company.direktor_name}/\n«__» ________20__ г.'
        
    # получаем дату от пользователя
    serdate = request.GET['date']
    year_search = str(serdate)[0:4]

    # создаем выгрузку
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="TO_{serdate}.xls"'

    # добавляем книгу и страницу с названием
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(f'ТОиР СИ, ИО, ВО {serdate}', cell_overwrite_ok=True)
    ws.header_str = b''
    ws.footer_str = b''

    # ширина столбцов
    ws.col(0).width = 200
    ws.col(1).width = 2000
    ws.col(2).width = 4000
    ws.col(3).width = 2000
    ws.col(4).width = 3000
    ws.col(5).width = 2000
    ws.col(6).width = 1200
    ws.col(7).width = 1200
    ws.col(8).width = 1200
    ws.col(9).width = 1200
    ws.col(10).width = 1200
    ws.col(11).width = 1200
    ws.col(12).width = 1200
    ws.col(13).width = 1200
    ws.col(14).width = 1200
    ws.col(15).width = 1200
    ws.col(16).width = 1200
    ws.col(17).width = 1200
    ws.col(18).width = 4500
    ws.col(19).width = 4000
        

        
    # шапка
    row_num = 1
    columns = [
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        '',
        affirmation,
        affirmation,
        affirmation,
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_plain_nobor_r)
        ws.merge(row_num, row_num + 6, 17, 19, style_plain_nobor_r)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 2000

    row_num += 7
    columns = [
        f'График технического обслуживания и ремонта лабораторного оборудования'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_plain_nobor_bold)
        ws.merge(row_num, row_num, 0, 19, style_plain_nobor_bold)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 600


    # заголовки ТОиР
    row_num += 3
    columns = [
        '',
        'Наименование, модификация, тип',
        'Наименование, модификация, тип',
        'Внутренний номер',
        'Заводской номер',
        'Время выполнения ТОиР*',
        'I КВАРТАЛ',
        'I КВАРТАЛ',
        'I КВАРТАЛ',
        'II КВАРТАЛ',
        'II КВАРТАЛ',
        'II КВАРТАЛ',
        'III КВАРТАЛ',
        'III КВАРТАЛ',
        'III КВАРТАЛ',
        'IV КВАРТАЛ',
        'IV КВАРТАЛ',
        'IV КВАРТАЛ',
        'Ответственный за ТО',
        'Примечание',
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_bold_borders)
        ws.merge(row_num, row_num, 1, 2, style_bold_borders)
        ws.merge(row_num, row_num, 6, 8, style_bold_borders)
        ws.merge(row_num, row_num, 9, 11, style_bold_borders)
        ws.merge(row_num, row_num, 12, 14, style_bold_borders)
        ws.merge(row_num, row_num, 15, 17, style_bold_borders)


    equipment_type = 'СИ'
    
    MODEL = MeasurEquipment.objects.filter(equipment__pointer=request.user.profile.userid).exclude(equipment__status='С').annotate(exnumber=Substr('equipment__exnumber',1,5)).annotate(all=Exists(ServiceEquipmentU.objects.filter(year=year_search, equipment=equipment))).filter(all=True)
    MODEL2 = ServiceEquipmentME
    MODEL3 = Verificationequipment
    MODEL4 = ServiceEquipmentU.objects.filter(year=year_search)
    MODEL5 = ServiceEquipmentUFact.objects.filter(year=year_search)
    to3 = 'Поверка'


    get_rows_service_shedule(request, row_num, ws, MODEL, to3, equipment_type, MODEL2, MODEL3, MODEL4, MODEL5, year_search)

    row_num = get_rows_service_shedule(request, row_num, ws, MODEL, to3, equipment_type, MODEL2, MODEL3, MODEL4, MODEL5, year_search) + 1

    # equipment_type = 'ИО'
    # MODEL = TestingEquipment.objects.filter(equipment__pointer=request.user.profile.userid).exclude(equipment__status='С').annotate(exnumber=Substr('equipment__exnumber',1,5))
    # MODEL2 = ServiceEquipmentTE
    # MODEL3 = Attestationequipment
    # MODEL4 = ServiceEquipmentU.objects.filter(year=year_search)
    # MODEL5 = ServiceEquipmentUFact.objects.filter(year=year_search)
    # to3 = 'Аттестация'



    # get_rows_service_shedule(request, row_num, ws, MODEL, to3, equipment_type, MODEL2, MODEL3, MODEL4, MODEL5, year_search)

    # row_num = get_rows_service_shedule(request, row_num, ws, MODEL, to3, equipment_type, MODEL2, MODEL3, MODEL4, MODEL5, year_search) + 1

    # equipment_type = 'ВО'
    # MODEL = HelpingEquipment.objects.filter(equipment__pointer=request.user.profile.userid).exclude(equipment__status='С').annotate(exnumber=Substr('equipment__exnumber',1,5))
    # MODEL2 = ServiceEquipmentHE
    # MODEL3 = None
    # to3 = None
    # MODEL4 = ServiceEquipmentU.objects.filter(year=year_search)
    # MODEL5 = ServiceEquipmentUFact.objects.filter(year=year_search)


    # get_rows_service_shedule(request, row_num, ws, MODEL, to3, equipment_type, MODEL2, MODEL3, MODEL4, MODEL5, year_search)

    # row_num = get_rows_service_shedule(request, row_num, ws, MODEL, to3, equipment_type, MODEL2, MODEL3, MODEL4, MODEL5, year_search) + 1

    row_num += 2
    columns = [
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
        f'* Виды и периодичность технического обслуживания',
    ]
    for col_num in range(1, len(columns)-2):
        ws.write(row_num, col_num, columns[col_num], style_bold_borders)
        ws.merge(row_num, row_num, 1, 17, style_bold_borders)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 600

    row_num += 1
    columns = [
        '',
        'ТО 0',
        'Ежедневное/еженедельное ',
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        servicedesc0,
        '',
        '',
    ]
    for col_num in range(1, len(columns)-2):
        ws.write(row_num, col_num, columns[col_num], style_plain)
        ws.merge(row_num, row_num, 3, 17, style_plain)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 3000

    row_num += 1
    columns = [
        '',
        'ТО 1',
        'Ежемесячное',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        '',
        '',
    ]
    for col_num in range(1, len(columns)-2):
        ws.write(row_num, col_num, columns[col_num], style_plain)
        ws.merge(row_num, row_num, 3, 17, style_plain)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 3000

    row_num += 1
    columns = [
        '',
        'ТО 2',
        'Ежеквартальное',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        'В соответствии с Руководством по эксплуатации',
        '',
        '',
    ]
    for col_num in range(1, len(columns)-2):
        ws.write(row_num, col_num, columns[col_num], style_plain)
        ws.merge(row_num, row_num, 3, 17, style_plain)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 3000

    row_num += 1
    columns = [
        '',
        'ТО 3',
        'Годовое',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        'Поверка/калибровка/аттестатция',
        '',
        '',
    ]
    for col_num in range(1, len(columns)-2):
        ws.write(row_num, col_num, columns[col_num], style_plain)
        ws.merge(row_num, row_num, 3, 17, style_plain)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 3000

    # все сохраняем
    wb.save(response)
    return response




# блок 7 - график поверки и формы для паспорта лаборатории

# стили

b1 = Borders()
b1.left = 1
b1.right = 1
b1.top = 1
b1.bottom = 1

style_border_bold = xlwt.XFStyle()
style_border_bold.font.bold = True
style_border_bold.font.name = 'Times New Roman'
style_border_bold.borders = b1
style_border_bold.alignment = alg_hc_vc_w1

style_bold = xlwt.XFStyle()
style_bold.font.bold = True
style_bold.font.name = 'Times New Roman'
style_bold.alignment = alg_hc_vc_w1

style_border = xlwt.XFStyle()
style_border.font.name = 'Times New Roman'
style_border.borders = b1
style_border.alignment = alg_hc_vc_w1

style_date = xlwt.XFStyle()
style_date.font.name = 'Times New Roman'
style_date.borders = b1
style_date.alignment = alg_hc_vc_w1
style_date.num_format_str = 'DD.MM.YYYY'

# график поверки и калибровки и аттестации
def export_me_xls(request):
    '''представление для выгрузки графика поверки и калибровки и аттестации'''
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="pov_att_shedule_{now.year}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('График поверки и калибровки СИ', cell_overwrite_ok=True)
    ws1 = wb.add_sheet('График аттестации ИО', cell_overwrite_ok=True)

    # ширина столбцов графика поверки
    ws.col(0).width = 3000
    ws.col(1).width = 3000
    ws.col(2).width = 4500
    ws.col(3).width = 3000
    ws.col(4).width = 4200
    ws.col(8).width = 4200
    ws.col(9).width = 3000
    ws.col(10).width = 4200
    ws.col(12).width = 4200
    ws.col(13).width = 4200
    ws.col(14).width = 3000
    ws.col(15).width = 3000
    ws.col(16).width = 3000
    ws.col(17).width = 3000
    ws.col(20).width = 6500
    ws.col(21).width = 6500
    ws.col(22).width = 9000
    ws.col(23).width = 3000
    ws.col(24).width = 3000
    ws.col(25).width = 3000
    ws.col(26).width = 3000

    # ширина столбцов графика аттестации
    ws1.col(0).width = 3000
    ws1.col(1).width = 4500
    ws1.col(2).width = 3500
    ws1.col(3).width = 4200
    ws1.col(7).width = 4200
    ws1.col(8).width = 4200
    ws1.col(9).width = 4200
    ws1.col(11).width = 4200
    ws1.col(12).width = 3000
    ws1.col(13).width = 3000
    ws1.col(14).width = 3000
    ws1.col(17).width = 8500
    ws1.col(18).width = 6500
    ws1.col(19).width = 6500
    ws1.col(20).width = 9000




    # название графика поверки, первый ряд
    row_num = 1
    columns = [
        f'График поверки и калибровки средств измерений на {now.year} год'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_bold)
        ws.merge(row_num, row_num, 0, 15, style_bold)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 600


    # заголовки графика поверки, первый ряд
    row_num += 2
    columns = [
                'Внутренний  номер',
                'Номер в госреестре',
                'Наименование',
                'Тип/Модификация',
                'Заводской номер',
                'Год выпуска',
                'Новый или б/у',
                'Год ввода в эксплуатацию',
                'Страна, наименование производителя',
                'Место установки или хранения',
                'Ответственный за СИ',
                'Статус',
                'Ссылка на сведения о поверке',
                'Номер свидетельства',
                'Дата поверки',
                'Дата окончания свидетельства',
                'Дата заказа поверки',
                'Дата заказа замены',
                'Периодичность поверки(месяцы)',
                'Инвентарный номер',
                'Диапазон измерений',
                'Метрологические характеристики',
                'Дополнительная информация/\nвыписка из текущих сведений о поверке',
                'Номер сертификата калибровки',
                'Дата калибровки',
                'Дата окончания калибровки',
                'Дата заказа калибровки',
               ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_border_bold)

    rows = MeasurEquipment.objects.annotate(exnumber=Substr('equipment__exnumber',1,5),
    manuf_country=Concat('equipment__manufacturer__country', Value(', '), 'equipment__manufacturer__companyName')).\
        filter(equipment__pointer=request.user.profile.userid).\
        exclude(equipment__status='С').\
        values_list(
            'exnumber',
            'charakters__reestr',
            'charakters__name',
            'charakters__typename',
            'equipment__lot',
            'equipment__yearmanuf',
            'equipment__new',
            'equipment__yearintoservice',
            'manuf_country',
            'equipment__newroomnumber',
            'equipment__newperson',
            'equipment__status',
            'newarshin',
            'newcertnumber',
            'newdate',
            'newdatedead',
            'newdateorder',
            'newdateordernew',
            'charakters__calinterval',
            'equipment__invnumber',
            'charakters__measurydiapason',
            'charakters__accuracity',
            'newextra',
            'calnewcertnumber',
            'calnewdate',
            'calnewdatedead',
            'calnewdateorder',
        )

    for row in rows:
        row_num += 1
        for col_num in range(0, 14):
            ws.write(row_num, col_num, row[col_num], style_border)
        for col_num in range(14, 18):
            ws.write(row_num, col_num, row[col_num], style_date)
        for col_num in range(18, 23):
            ws.write(row_num, col_num, row[col_num], style_border)
        for col_num in range(23, len(row)):
            ws.write(row_num, col_num, row[col_num], style_date)

        # название графика аттестации, первый ряд
    row_num = 1
    columns = [
        f'График аттестации испытательного оборудования на {now.year} год'
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_bold)
        ws1.merge(row_num, row_num, 0, 15, style_bold)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 600

        # заголовки графика аттестации, первый ряд
    row_num += 2
    columns = [
        'Внутренний  номер',
        'Наименование',
        'Тип/Модификация',
        'Заводской номер',
        'Год выпуска',
        'Новый или б/у',
        'Год ввода в эксплуатацию',
        'Страна, наименование производителя',
        'Место установки или хранения',
        'Ответственный за ИО',
        'Статус',
        'Номер аттестата',
        'Дата аттестации',
        'Дата окончания аттестации',
        'Дата заказа аттестации',
        'Периодичность аттестации',
        'Инвентарный номер',
        'Основные технические характеристики',
        'Наименование видов испытаний',
        'Дополнительная информация/\nвыписка из текущего аттестата',
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_border_bold)

    rows = TestingEquipment.objects.filter(pointer=request.user.profile.userid)
    rows = rows.annotate(exnumber=Substr('equipment__exnumber',1,5),
                 manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName')). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__personchange__in=setperson). \
        filter(equipmentSM_att__in=setatt). \
        exclude(equipment__status='С'). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipment__yearmanuf',
        'equipment__new',
        'equipment__yearintoservice',
        'manuf_country',
        'equipment__roomschange__roomnumber__roomnumber',
        'equipment__newperson',
        'equipment__status',
        'equipmentSM_att__certnumber',
        'equipmentSM_att__date',
        'equipmentSM_att__datedead',
        'equipmentSM_att__dateorder',
        'charakters__calinterval',
        'equipment__invnumber',
        'charakters__main_technical_characteristics',
        'charakters__aim',
        'equipmentSM_att__extra'
    )
    for row in rows:
        row_num += 1
        for col_num in range(0, 12):
            ws1.write(row_num, col_num, row[col_num], style_border)
        for col_num in range(12, 15):
            ws1.write(row_num, col_num, row[col_num], style_date)
        for col_num in range(15, len(row)):
            ws1.write(row_num, col_num, row[col_num], style_border)

    wb.save(response)
    return response


b1 = Borders()
b1.left = 1
b1.right = 1
b1.top = 1
b1.bottom = 1

style_border_bold = xlwt.XFStyle()
style_border_bold.font.bold = True
style_border_bold.font.name = 'Times New Roman'
style_border_bold.borders = b1
style_border_bold.alignment = alg_hc_vc_w1

style_bold = xlwt.XFStyle()
style_bold.font.bold = True
style_bold.font.name = 'Times New Roman'
style_bold.alignment = alg_hc_vc_w1

style_border = xlwt.XFStyle()
style_border.font.name = 'Times New Roman'
style_border.borders = b1
style_border.alignment = alg_hc_vc_w1

style_date = xlwt.XFStyle()
style_date.font.name = 'Times New Roman'
style_date.borders = b1
style_date.alignment = alg_hc_vc_w1
style_date.num_format_str = 'DD.MM.YYYY'


def export_me_xls(request):
    '''представление для выгрузки графика поверки и калибровки и аттестации'''
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="pov_att_shedule_{now.year}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('График поверки и калибровки СИ', cell_overwrite_ok=True)
    ws1 = wb.add_sheet('График аттестации ИО', cell_overwrite_ok=True)

    # ширина столбцов графика поверки
    ws.col(0).width = 3000
    ws.col(1).width = 3000
    ws.col(2).width = 4500
    ws.col(3).width = 3000
    ws.col(4).width = 4200
    ws.col(8).width = 4200
    ws.col(9).width = 3000
    ws.col(10).width = 4200
    ws.col(12).width = 4200
    ws.col(13).width = 4200
    ws.col(14).width = 3000
    ws.col(15).width = 3000
    ws.col(16).width = 3000
    ws.col(17).width = 3000
    ws.col(20).width = 6500
    ws.col(21).width = 6500
    ws.col(22).width = 9000
    ws.col(23).width = 3000
    ws.col(24).width = 3000
    ws.col(25).width = 3000
    ws.col(26).width = 3000

    # ширина столбцов графика аттестации
    ws1.col(0).width = 3000
    ws1.col(1).width = 4500
    ws1.col(2).width = 3500
    ws1.col(3).width = 4200
    ws1.col(7).width = 4200
    ws1.col(8).width = 4200
    ws1.col(9).width = 4200
    ws1.col(11).width = 4200
    ws1.col(12).width = 3000
    ws1.col(13).width = 3000
    ws1.col(14).width = 3000
    ws1.col(17).width = 8500
    ws1.col(18).width = 6500
    ws1.col(19).width = 6500
    ws1.col(20).width = 9000




    # название графика поверки, первый ряд
    row_num = 1
    columns = [
        f'График поверки и калибровки средств измерений на {now.year} год'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_bold)
        ws.merge(row_num, row_num, 0, 15, style_bold)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 600


    # заголовки графика поверки, первый ряд
    row_num += 2
    columns = [
                'Внутренний  номер',
                'Номер в госреестре',
                'Наименование',
                'Тип/Модификация',
                'Заводской номер',
                'Год выпуска',
                'Новый или б/у',
                'Год ввода в эксплуатацию',
                'Страна, наименование производителя',
                'Место установки или хранения',
                'Ответственный за СИ',
                'Статус',
                'Ссылка на сведения о поверке',
                'Номер свидетельства',
                'Дата поверки',
                'Дата окончания свидетельства',
                'Дата заказа поверки',
                'Дата заказа замены',
                'Периодичность поверки(месяцы)',
                'Инвентарный номер',
                'Диапазон измерений',
                'Метрологические характеристики',
                'Дополнительная информация/\nвыписка из текущих сведений о поверке',
                'Номер сертификата калибровки',
                'Дата калибровки',
                'Дата окончания калибровки',
                'Дата заказа калибровки',
               ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_border_bold)

    rows = MeasurEquipment.objects.annotate(exnumber=Substr('equipment__exnumber',1,5),
    manuf_country=Concat('equipment__manufacturer__country', Value(', '), 'equipment__manufacturer__companyName')).\
        filter(equipment__pointer=request.user.profile.userid).\
        exclude(equipment__status='С').\
        values_list(
            'exnumber',
            'charakters__reestr',
            'charakters__name',
            'charakters__typename',
            'equipment__lot',
            'equipment__yearmanuf',
            'equipment__new',
            'equipment__yearintoservice',
            'manuf_country',
            'equipment__newroomnumber',
            'equipment__newperson',
            'equipment__status',
            'newarshin',
            'newcertnumber',
            'newdate',
            'newdatedead',
            'newdateorder',
            'newdateordernew',
            'charakters__calinterval',
            'equipment__invnumber',
            'charakters__measurydiapason',
            'charakters__accuracity',
            'newextra',
            'calnewcertnumber',
            'calnewdate',
            'calnewdatedead',
            'calnewdateorder',
        )

    for row in rows:
        row_num += 1
        for col_num in range(0, 14):
            ws.write(row_num, col_num, row[col_num], style_border)
        for col_num in range(14, 18):
            ws.write(row_num, col_num, row[col_num], style_date)
        for col_num in range(18, 23):
            ws.write(row_num, col_num, row[col_num], style_border)
        for col_num in range(23, len(row)):
            ws.write(row_num, col_num, row[col_num], style_date)

        # название графика аттестации, первый ряд
    row_num = 1
    columns = [
        f'График аттестации испытательного оборудования на {now.year} год'
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_bold)
        ws1.merge(row_num, row_num, 0, 15, style_bold)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 600

        # заголовки графика аттестации, первый ряд
    row_num += 2
    columns = [
        'Внутренний  номер',
        'Наименование',
        'Тип/Модификация',
        'Заводской номер',
        'Год выпуска',
        'Новый или б/у',
        'Год ввода в эксплуатацию',
        'Страна, наименование производителя',
        'Место установки или хранения',
        'Ответственный за ИО',
        'Статус',
        'Номер аттестата',
        'Дата аттестации',
        'Дата окончания аттестации',
        'Дата заказа аттестации',
        'Периодичность аттестации',
        'Инвентарный номер',
        'Основные технические характеристики',
        'Наименование видов испытаний',
        'Дополнительная информация/\nвыписка из текущего аттестата',
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_border_bold)

    rows = TestingEquipment.objects.filter(pointer=request.user.profile.userid)
    rows = rows.annotate(exnumber=Substr('equipment__exnumber',1,5),
                 manuf_country=Concat('equipment__manufacturer__country', Value(', '),
                                      'equipment__manufacturer__companyName')). \
        filter(equipment__roomschange__in=setroom). \
        filter(equipment__personchange__in=setperson). \
        filter(equipmentSM_att__in=setatt). \
        exclude(equipment__status='С'). \
        values_list(
        'exnumber',
        'charakters__name',
        'charakters__typename',
        'equipment__lot',
        'equipment__yearmanuf',
        'equipment__new',
        'equipment__yearintoservice',
        'manuf_country',
        'equipment__roomschange__roomnumber__roomnumber',
        'equipment__newperson',
        'equipment__status',
        'equipmentSM_att__certnumber',
        'equipmentSM_att__date',
        'equipmentSM_att__datedead',
        'equipmentSM_att__dateorder',
        'charakters__calinterval',
        'equipment__invnumber',
        'charakters__main_technical_characteristics',
        'aim',
        'equipmentSM_att__extra'
    )
    for row in rows:
        row_num += 1
        for col_num in range(0, 12):
            ws1.write(row_num, col_num, row[col_num], style_border)
        for col_num in range(12, 15):
            ws1.write(row_num, col_num, row[col_num], style_date)
        for col_num in range(15, len(row)):
            ws1.write(row_num, col_num, row[col_num], style_border)

    wb.save(response)
    return response



def export_accanalytica_xls(request):
    '''представление для выгрузки форм приложение к паспорту лаборатории по форме АЦЦ Аналитика'''
    company = Company.objects.get(userid=request.user.profile.userid)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="ACC_Analytica.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Форма_4_СИ' , cell_overwrite_ok=True)
    ws1 = wb.add_sheet('Форма_5_ИО', cell_overwrite_ok=True)
    ws2 = wb.add_sheet('Форма_6_ВО', cell_overwrite_ok=True)
    ws.header_str = b''
    ws.footer_str = b''
    ws1.header_str = b''
    ws1.footer_str = b''    
    ws2.header_str = b''
    ws2.footer_str = b''
        
    alg_hc_vc_w1 = Alignment()
    alg_hc_vc_w1.horz = Alignment.HORZ_CENTER
    alg_hc_vc_w1.vert = Alignment.VERT_CENTER
    alg_hc_vc_w1.wrap = 1

    b1 = Borders()
    b1.left = 1
    b1.right = 1
    b1.top = 1
    b1.bottom = 1

    style_border_bold = xlwt.XFStyle()
    style_border_bold.font.bold = True
    style_border_bold.font.name = 'Times New Roman'
    style_border_bold.borders = b1
    style_border_bold.alignment = alg_hc_vc_w1

    style_bold = xlwt.XFStyle()
    style_bold.font.bold = True
    style_bold.font.name = 'Times New Roman'
    style_bold.alignment = alg_hc_vc_w1

    style_border = xlwt.XFStyle()
    style_border.font.name = 'Times New Roman'
    style_border.borders = b1
    style_border.alignment = alg_hc_vc_w1

    style_date = xlwt.XFStyle()
    style_date.font.name = 'Times New Roman'
    style_date.borders = b1
    style_date.alignment = alg_hc_vc_w1
    style_date.num_format_str = 'DD.MM.YYYY'

    # ширина столбцов форма по СИ
    ws.col(0).width = 1000
    ws.col(1).width = 3100
    ws.col(2).width = 3000
    ws.col(3).width = 3000
    ws.col(4).width = 2500
    ws.col(6).width = 3500
    ws.col(7).width = 2500
    ws.col(9).width = 3000
    ws.col(10).width = 3800


    # ширина столбцов форма по ИО
    ws1.col(0).width = 1000
    ws1.col(1).width = 3100
    ws1.col(2).width = 3000
    ws1.col(3).width = 3000
    ws1.col(4).width = 2500
    ws1.col(6).width = 3500
    ws1.col(7).width = 3800
    ws1.col(9).width = 3000
    ws1.col(10).width = 3800


    # ширина столбцов форма по ВО
    ws2.col(0).width = 1000
    ws2.col(1).width = 3100
    ws2.col(2).width = 3000
    ws2.col(3).width = 3000
    ws2.col(4).width = 2500
    ws2.col(5).width = 3500
    ws2.col(6).width = 3500
    ws2.col(7).width = 2500
    ws2.col(9).width = 3000
    ws2.col(10).width = 3800

        
    # название форма по СИ
    len_table_ws = 12
    row_num = 1
    columns = [
        f'Сведения о средствах измерений {company.name}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_bold)
        ws.merge(row_num, row_num, 0, len_table_ws, style_bold)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 600


    # заголовки форма по СИ 
    row_num += 2
    columnsup = [
                            '№',
                'Наименование',
                'Тип (модель)',
                'Идентификационные сведения',
                'Поверка',
                'Поверка',
                'Поверка',
                'Калибровка',
                'Калибровка',
                'Калибровка',
                'Ответственное лицо',
                'Место нахождения',
                'Примечания',

    ]
    for col_num in range(4):
        ws.write(row_num, col_num, columnsup[col_num], style_border)
    for col_num in range(4, 7):
        ws.write(row_num, col_num, columnsup[col_num], style_border)
        ws.merge(row_num, row_num, 4, 6, style_border)
    for col_num in range(7,10):
        ws.write(row_num, col_num, columnsup[col_num], style_border)
        ws.merge(row_num, row_num, 7,9, style_border)
    for col_num in range(10, 13):
        ws.write(row_num, col_num, columnsup[col_num], style_border)
              
    row_num += 1
    columnslow = [
                '№',
                'Наименование',
                'Тип (модель)',
                'Идентификационные сведения',
                'Дата',
                'Период',
                'Постоянный адрес  записи сведений о результатах поверки СИ из ФГИС АРШИН',
                'Дата',
                'Период',
                'Калибровочная  лаборатория',
                'Ответственное лицо',
                'Место нахождения',
                'Примечания',
               ]
        
    for col_num in range(4):
        ws.write(row_num, col_num, columnslow[col_num], style_border)
        ws.merge(3, 4, col_num, col_num, style_border)
    for col_num in range(4,10):
        ws.write(row_num, col_num, columnslow[col_num], style_border)
    for col_num in range(10, len(columnslow)):
        ws.write(row_num, col_num, columnslow[col_num], style_border)
        ws.merge(3, 4, col_num, col_num, style_border)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 2200


    row_num += 1
    columns = [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
                '11',
                '12',
                '13',
               ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_border)


    rows = MeasurEquipment.objects.annotate(blanc= Value(' ')).\
        filter(equipment__pointer=request.user.profile.userid).\
        filter(equipment__status='Э').\
        values_list(
            'charakters__name',
            'charakters__typename',
            'equipment__lot',
            'newdate',
            'charakters__calinterval',
            'newarshin',
            'calnewdate',
            'charakters__calinterval',
            'calnewverificator',
            'equipment__newperson',
            'equipment__newroomnumber',
                'equipment__pravo_have'
            
        )

    for row in rows:
        row_num += 1
        for col_num in range(3):
            ws.write(row_num, col_num + 1, row[col_num], style_border)
        for col_num in range(3, 4):
            ws.write(row_num, col_num + 1, row[col_num], style_date)
        for col_num in range(4, 9):
            ws.write(row_num, col_num + 1, row[col_num], style_border)
        for col_num in range(9, 10):
            ws.write(row_num, col_num + 1, row[col_num], style_date)
        for col_num in range(10, len(row)):
            ws.write(row_num, col_num + 1, row[col_num], style_border)
                
    a = row_num
    for col_num in range(1):
        for row_num in range(6, a + 1):
            ws.write(row_num, col_num, f'{row_num - 5}', style_border)

        

    # название форма по ИО
    len_table_ws = 9
    row_num = 1
    columns = [
        f'Сведения об испытательном оборудовании {company.name}'
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_bold)
        ws1.merge(row_num, row_num, 0, len_table_ws, style_bold)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 600


    # заголовки форма по ИО 
    row_num += 2
    columnsup = [
                            '№',
                'Наименование',
                'Тип (модель)',
                'Идентификационные сведения',
                'Аттестация',
                'Аттестация',
                'Аттестация',
                'Ответственное лицо',
                'Место нахождения',
                'Примечания',

    ]
    for col_num in range(4):
        ws1.write(row_num, col_num, columnsup[col_num], style_border)
    for col_num in range(4, 7):
        ws1.write(row_num, col_num, columnsup[col_num], style_border)
        ws1.merge(row_num, row_num, 4, 6, style_border)
    for col_num in range(7, 10):
        ws1.write(row_num, col_num, columnsup[col_num], style_border)
              
    row_num += 1
    columnslow = [
                '№',
                'Наименование',
                'Тип (модель)',
                'Идентификационные сведения',
                'Дата',
                'Период',
                'Аттестующая организация',
                'Ответственное лицо',
                'Место нахождения',
                'Примечания',
               ]
        
    for col_num in range(4):
        ws1.write(row_num, col_num, columnslow[col_num], style_border)
        ws1.merge(3, 4, col_num, col_num, style_border)
    for col_num in range(4,7):
        ws1.write(row_num, col_num, columnslow[col_num], style_border)
    for col_num in range(7, len(columnslow)):
        ws1.write(row_num, col_num, columnslow[col_num], style_border)
        ws1.merge(3, 4, col_num, col_num, style_border)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 2200


    row_num += 1
    columns = [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
               ]

    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_border)


    rows = TestingEquipment.objects.annotate(blanc= Value(' ')).\
        filter(equipment__pointer=request.user.profile.userid).\
        filter(equipment__status='Э').\
        values_list(
            'charakters__name',
            'charakters__typename',
            'equipment__lot',
            'newdate',
            'charakters__calinterval',
            'newverificator',
            'equipment__newperson',
            'equipment__newroomnumber',
                'equipment__pravo_have'
            
        )

    for row in rows:
        row_num += 1
        for col_num in range(3):
            ws1.write(row_num, col_num + 1, row[col_num], style_border)
        for col_num in range(3, 4):
            ws1.write(row_num, col_num + 1, row[col_num], style_date)
        for col_num in range(4, len(row)):
            ws1.write(row_num, col_num + 1, row[col_num], style_border)

                
    a = row_num
    for col_num in range(1):
        for row_num in range(6, a + 1):
            ws1.write(row_num, col_num, f'{row_num - 5}', style_border)


    # название форма по ВО
    len_table_ws = 7
    row_num = 1
    columns = [
        f'Сведения о вспомогательном оборудовании {company.name}'
    ]
    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], style_bold)
        ws2.merge(row_num, row_num, 0, len_table_ws, style_bold)
        ws2.row(row_num).height_mismatch = True
        ws2.row(row_num).height = 600

        
    # заголовки форма по ВО 
              
    row_num += 2
    columnslow = [
                '№',
                'Наименование',
                'Тип (модель)',
                'Идентификационные сведения',
                'Техническое обслуживание',
                'Ответственное лицо',
                'Место нахождения',
                'Примечания',
               ]
        

    for col_num in range(len(columnslow)):
        ws2.write(row_num, col_num, columnslow[col_num], style_border)
    ws2.row(row_num).height_mismatch = True
    ws2.row(row_num).height = 2200


    row_num += 1
    columns = [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
               ]

    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], style_border)


    rows = HelpingEquipment.objects.annotate(blanc= Value(' ')).\
        filter(equipment__pointer=request.user.profile.userid).\
        filter(equipment__status='Э').\
        values_list(
            'charakters__name',
            'charakters__typename',
            'equipment__lot',
                'blanc',
            'equipment__newperson',
            'equipment__newroomnumber',
                'equipment__pravo_have'
            
        )

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws2.write(row_num, col_num + 1, row[col_num], style_border)

                
    a = row_num
    for col_num in range(1):
        for row_num in range(5, a + 1):
            ws2.write(row_num, col_num, f'{row_num - 4}', style_border)

        
    wb.save(response)
    return response


def export_rossaccreditacia_xls(request):
    '''представление для выгрузки форм приложение к паспорту лаборатории по форме Росаккредитации'''
    company = Company.objects.get(userid=request.user.profile.userid)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="FSA.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Форма_4_СИ' , cell_overwrite_ok=True)
    ws1 = wb.add_sheet('Форма_5_ИО', cell_overwrite_ok=True)
    ws2 = wb.add_sheet('Форма_6_ВО', cell_overwrite_ok=True)
    ws.header_str = b''
    ws.footer_str = b''
    ws1.header_str = b''
    ws1.footer_str = b''    
    ws2.header_str = b''
    ws2.footer_str = b''
        
    alg_hc_vc_w1 = Alignment()
    alg_hc_vc_w1.horz = Alignment.HORZ_CENTER
    alg_hc_vc_w1.vert = Alignment.VERT_CENTER
    alg_hc_vc_w1.wrap = 1

    b1 = Borders()
    b1.left = 1
    b1.right = 1
    b1.top = 1
    b1.bottom = 1

    style_border_bold = xlwt.XFStyle()
    style_border_bold.font.bold = True
    style_border_bold.font.name = 'Times New Roman'
    style_border_bold.borders = b1
    style_border_bold.alignment = alg_hc_vc_w1

    style_bold = xlwt.XFStyle()
    style_bold.font.bold = True
    style_bold.font.name = 'Times New Roman'
    style_bold.alignment = alg_hc_vc_w1

    style_border = xlwt.XFStyle()
    style_border.font.name = 'Times New Roman'
    style_border.borders = b1
    style_border.alignment = alg_hc_vc_w1

    style_date = xlwt.XFStyle()
    style_date.font.name = 'Times New Roman'
    style_date.borders = b1
    style_date.alignment = alg_hc_vc_w1
    style_date.num_format_str = 'DD.MM.YYYY'

    # ширина столбцов форма по СИ
    ws.col(0).width = 1000
    ws.col(1).width = 4500
    ws.col(2).width = 4500
    ws.col(3).width = 4500
    ws.col(4).width = 4500
    ws.col(5).width = 4500
    ws.col(6).width = 4500
    ws.col(7).width = 4500
    ws.col(8).width = 4500
    ws.col(9).width = 4500
    ws.col(10).width = 4500


    # ширина столбцов форма по ИО
    ws1.col(0).width = 1000
    ws1.col(1).width = 4500
    ws1.col(2).width = 4500
    ws1.col(3).width = 4500
    ws1.col(4).width = 4500
    ws1.col(5).width = 4500
    ws1.col(6).width = 4500
    ws1.col(7).width = 4500
    ws1.col(8).width = 4500
    ws1.col(9).width = 4500
    ws1.col(10).width = 4500


    # ширина столбцов форма по ВО
    ws2.col(0).width = 1000
    ws2.col(1).width = 4500
    ws2.col(2).width = 4500
    ws2.col(3).width = 4500
    ws2.col(4).width = 4500
    ws2.col(5).width = 4500
    ws2.col(6).width = 4500
    ws2.col(7).width = 4500
    ws2.col(8).width = 4500
    ws2.col(9).width = 4500
    ws2.col(10).width = 4500

        
    # название форма по СИ
    len_table_ws = 10
    row_num = 1
    columns = [
        f'Оснащенность средствами измерений {company.name}'
    ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_bold)
        ws.merge(row_num, row_num, 0, len_table_ws, style_bold)
        ws.row(row_num).height_mismatch = True
        ws.row(row_num).height = 600


    # заголовки форма по СИ 
    row_num += 2
    columnsup = [
                            '№',
                'Наименование определяемых (измеряемых) характеристик (параметров) продукции',
                'Наименование СИ, тип (марка), регистрационный номер в Федеральном информационном фонде по обеспечению единства измерений (при наличии)',
                'Изготовитель (страна, наименование организации, год выпуска)',
                'Год ввода в эксплуатацию, заводской номер',
                'Метрологические характеристики',
                'Метрологические характеристики',
                'Сведения о результатах поверки СИ в Федеральном информационном фонде по обеспечению единства измерений (номер, дата, срок действия) и (или) сертификат о калибровке СИ (номер, дата, срок действия (при наличии)',
                'Право собственности или иное законное основание, предусматривающее право владения и пользования (реквизиты подтверждающих документов)',
                'Место установки или хранения',
                'Примечания',
    ]
    for col_num in range(5):
        ws.write(row_num, col_num, columnsup[col_num], style_border)
    for col_num in range(5, 7):
        ws.write(row_num, col_num, columnsup[col_num], style_border)
        ws.merge(row_num, row_num, 5, 6, style_border)
    for col_num in range(7, len(columnsup)):
        ws.write(row_num, col_num, columnsup[col_num], style_border)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 1200
              
    row_num += 1
    columnslow = [
                '№',
                'Наименование определяемых (измеряемых) характеристик (параметров) продукции',
                'Наименование СИ, тип (марка), регистрационный номер в Федеральном информационном фонде по обеспечению единства измерений (при наличии)',
                'Изготовитель (страна, наименование организации, год выпуска)',
                'Год ввода в эксплуатацию, заводской номер',
                'Диапазон измерений',
                'Класс точности (разряд), погрешность и (или) неопределенность (класс, разряд)',
                'Сведения о результатах поверки СИ в Федеральном информационном фонде по обеспечению единства измерений (номер, дата, срок действия) и (или) сертификат о калибровке СИ (номер, дата, срок действия (при наличии)',
                'Право собственности или иное законное основание, предусматривающее право владения и пользования (реквизиты подтверждающих документов)',
                'Место установки или хранения',
                'Примечания',
               ]
        
    for col_num in range(5):
        ws.write(row_num, col_num, columnslow[col_num], style_border)
        ws.merge(3, 4, col_num, col_num, style_border)
    for col_num in range(5,7):
        ws.write(row_num, col_num, columnslow[col_num], style_border)
    for col_num in range(7, len(columnslow)):
        ws.write(row_num, col_num, columnslow[col_num], style_border)
        ws.merge(3, 4, col_num, col_num, style_border)
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 4000


    row_num += 1
    columns = [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
                '11',
               ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], style_border)


    rows = MeasurEquipment.objects.annotate(blanc= Value(' '),\
          name=Concat('charakters__name', Value(', '), 'charakters__typename', Value(', '), 'charakters__reestr', output_field=CharField()),\
          manuf = Concat('equipment__manufacturer__country', Value(', '), 'equipment__manufacturer__companyName', Value(', '), 'equipment__yearmanuf', output_field=CharField()),\
          exp = Concat('equipment__yearintoservice', Value(', зав. № '), 'equipment__lot', output_field=CharField()),\
          metro = Concat('newcertnumber', Value(', от '), 'newdate', Value(' до '), 'newdatedead', output_field=CharField())).\
          filter(equipment__pointer=request.user.profile.userid).\
          filter(equipment__status='Э').\
          values_list(
            'aim',
            'name',
            'manuf',
            'exp',
            'charakters__measurydiapason',
            'charakters__accuracity',
            'metro',
            'equipment__pravo',
            'equipment__newroomnumber',   
            'blanc',
        )

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num + 1, row[col_num], style_border)
                
    a = row_num
    for col_num in range(1):
        for row_num in range(6, a + 1):
            ws.write(row_num, col_num, f'{row_num - 5}', style_border)

        

    # название форма по ИО
    len_table_ws = 9
    row_num = 1
    columns = [
        f'Оснащенность испытательным оборудованием {company.name}'
    ]
    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_bold)
        ws1.merge(row_num, row_num, 0, len_table_ws, style_bold)
        ws1.row(row_num).height_mismatch = True
        ws1.row(row_num).height = 600


    # заголовки форма по ИО 
    row_num += 2
    columnsup = [
                            '№',
                'Наименование определяемых (измеряемых) характеристик (параметров) продукции',
                'Наименование испытуемых групп объектов',  
                'Наименование испытательного оборудования (ИО), тип (марка)',
                'Изготовитель (страна, наименование организации, год выпуска)',
                'Основные технические характеристики',
                'Год ввода в эксплуатацию, заводской номер',
                'Дата и номер документа об аттестации ИО, срок его действия',
                'Право собственности или иное законное основание, предусматривающее право владения и пользования (реквизиты подтверждающих документов)',
                'Место установки или хранения',
                'Примечания',
    ]
    for col_num in range(len(columnsup)):
        ws1.write(row_num, col_num, columnsup[col_num], style_border)
    ws1.row(row_num).height_mismatch = True
    ws1.row(row_num).height = 3600
              

    row_num += 1
    columns = [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
                '11',
               ]

    for col_num in range(len(columns)):
        ws1.write(row_num, col_num, columns[col_num], style_border)


    rows = TestingEquipment.objects.annotate(blanc= Value(' '),\
          name=Concat('charakters__name', Value(', '), 'charakters__typename', Value(', '), output_field=CharField()),\
          manuf = Concat('equipment__manufacturer__country', Value(', '), 'equipment__manufacturer__companyName', Value(', '), 'equipment__yearmanuf', output_field=CharField()),\
          exp = Concat('equipment__yearintoservice', Value(', зав. № '), 'equipment__lot', output_field=CharField()),\
          metro = Concat('newcertnumber', Value(', от '), 'newdate', Value(' до '), 'newdatedead', output_field=CharField())).\
          filter(equipment__pointer=request.user.profile.userid).\
          filter(equipment__status='Э').\
          values_list(
            'aim',
            'analited_objects',
            'name',
            'manuf',
            'charakters__main_technical_characteristics',
            'exp',
            'metro',
            'equipment__pravo',
            'equipment__newroomnumber',   
            'blanc',
        )

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws1.write(row_num, col_num + 1, row[col_num], style_border)
                
    a = row_num
    for col_num in range(1):
        for row_num in range(5, a + 1):
            ws1.write(row_num, col_num, f'{row_num - 4}', style_border)


    # название форма по ВО
    len_table_ws = 7
    row_num = 1
    columns = [
        f'Оснащенность вспомогательным оборудованием {company.name}'
    ]
    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], style_bold)
        ws2.merge(row_num, row_num, 0, len_table_ws, style_bold)
        ws2.row(row_num).height_mismatch = True
        ws2.row(row_num).height = 600


    # заголовки форма по ВО 
    row_num += 2
    columnsup = [
                            '№',
                'Наименование',
                'Изготовитель (страна, наименование организации, год выпуска)',
                'Год ввода в эксплуатацию, заводской номер',
                'Назначение',
                'Право собственности или иное законное основание, предусматривающее право владения и пользования (реквизиты подтверждающих документов)',
                'Место установки или хранения',
                'Примечания',
    ]
    for col_num in range(len(columnsup)):
        ws2.write(row_num, col_num, columnsup[col_num], style_border)
    ws2.row(row_num).height_mismatch = True
    ws2.row(row_num).height = 3600
              

    row_num += 1
    columns = [
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
               ]

    for col_num in range(len(columns)):
        ws2.write(row_num, col_num, columns[col_num], style_border)


    rows = HelpingEquipment.objects.annotate(blanc= Value(' '),\
          name=Concat('charakters__name', Value(', '), 'charakters__typename', Value(', '), output_field=CharField()),\
          manuf = Concat('equipment__manufacturer__country', Value(', '), 'equipment__manufacturer__companyName', Value(', '), 'equipment__yearmanuf', output_field=CharField()),\
          exp = Concat('equipment__yearintoservice', Value(', зав. № '), 'equipment__lot', output_field=CharField())).\
          filter(equipment__pointer=request.user.profile.userid).\
          filter(equipment__status='Э').\
          values_list(
            'name',
            'manuf',
            'exp',
            'aim',
            'equipment__pravo',
            'equipment__newroomnumber',   
            'blanc',
        )

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws2.write(row_num, col_num + 1, row[col_num], style_border)
                
    a = row_num
    for col_num in range(1):
        for row_num in range(5, a + 1):
            ws2.write(row_num, col_num, f'{row_num - 4}', style_border)

        
    wb.save(response)
    return response


