"""
Модуль проекта LabJournal, корневые модули.
Данный модуль funcstandart.py содержит функции и константы для всего проекта.
После 2050 года обратить внимание на функцию  get_dateformat_django :)
"""
from datetime import date
import re
from decimal import *
now = date.today()

K = 2  #(двойка из правила округления двойки)

def get_dateformat_django(date):
    """переводит дату из формата дд.мм.гггг в гггг-мм-дд"""
    pattern = re.compile(r'\d\d\d\d-\d\d-\d\d')
    if str(date).isalpha():
        date = None
    else:
        
        try:
            if not pattern.match(date):
                dateformat = str(date)
                y = dateformat[1]
                if not y.isdigit():
                    dateformat = "0" + dateformat
                day = dateformat[:2]
                month = dateformat[3:5]
                year = dateformat[6:]
                a = int(str(now.year)[:2]) + 10
                if len(year) == 2 and int(year) <= a:
                    year = f'20{year}'
                elif len(year) == 2 and int(year) >= a:
                    year = f'19{year}'            
                date = f'{year}-{month}-{day}'
    
            # dates = ['09-31', '02-30', '02-31', '04-31', '06-31', '11-31']
            # if date[5:] in dates:
            #     dyy = str(int(date[:-2]) - 1)
            #     date = f'{year}-{month}-{dyy}'

        except:
            date = None
    return date

def rounder(value: Decimal, m: str) -> Decimal:
    '''каскадно округляет числа с неизвестным количесвом знаков после точки(запятой)(value)
    до указанного количества знаков (m)'''
    st = str(value)
    index = st.find(".")
    frac_abserror = st[index + 1:]
    nst = '1.' + (len(m) - 2) * '0'
    n = len(nst) - 2
    print(n)
    for j in range(len(frac_abserror), n, -1):
        k = '1.' + j * '0'
        value = value.quantize(Decimal(k), ROUND_HALF_UP)
        print(value)
    value = value.quantize(Decimal(m), ROUND_HALF_UP)
    return Decimal(value)

def mrerrow(abserror) -> Decimal:
    '''округляет абсолютную погрешность в соответствии с правилами метрологии (правило двойки)'''
    if abserror > K + 1:
        return Decimal(abserror).quantize(Decimal('1'), ROUND_HALF_UP)
    abserror = str(abserror)
    index = abserror.find(".")
    if index > 0:
        int_abserror = abserror[:index]
        frac_abserror = abserror[index + 1:]
        if int(int_abserror) in range(1, K + 1):
            result = Decimal(abserror).quantize(Decimal('1.0'), ROUND_HALF_UP)
            return Decimal(result)
        if int(int_abserror) == 0:
            i = 0
            while i < len(frac_abserror):
                if int(frac_abserror[i]) == 0:
                    i += 1
                if 0 < int(frac_abserror[i]) <= 2:
                    frac_index = i + 2
                    k = '1.' + frac_index * '0'
                    result = Decimal(abserror).quantize(Decimal(k), ROUND_HALF_UP)
                    return result
                if int(frac_abserror[i]) > 2:
                    frac_index = i + 1
                    k = '1.' + frac_index * '0'
                    result = Decimal(abserror).quantize(Decimal(k), ROUND_HALF_UP)
                    return result
    if index <= 0:
        result = Decimal(abserror).quantize(Decimal('1.0'), ROUND_HALF_UP)
        return result

def  numberDigits(avg: Decimal, abserror: Decimal) -> Decimal:
    '''округляет АЗ СО в соответствии с абсолютной погрешностью
    abserror: абсолютная погрешность
    avg: среднее из 2 измерений без округления
    return: АЗ СО в формате Decimal
    '''
    if abserror >= K+1:
        certifiedValue = Decimal(avg).quantize(Decimal(1), ROUND_HALF_UP)
        return certifiedValue
    abserror = str(abserror)
    index = abserror.find(".")
    if index > 0:
        frac_abserror = abserror[index + 1:]
        j = len(frac_abserror)
        k = '1.' + j * '0'
        certifiedValue = avg.quantize(Decimal(k), ROUND_HALF_UP)
        return certifiedValue

from decimal import *

def get_avg(X1: Decimal, X2: Decimal, nums: int = 6):
    """
    находит среднее арифметическое из X1 и X2 и округляет до заданного числа знаков nums
    :param X1:
    :param X2:
    :param nums: число знаков после запятой
    :return Xсреднее:
    """
    k = '1.' + nums * '0'
    avg = ((X1 + X2)/Decimal(2)).quantize(Decimal(k), ROUND_HALF_UP)
    return avg

def get_acc_measurement(X1: Decimal, X2: Decimal, nums: int = 2 ):
    """находит разницу между измерениями X1 и X2 в процентах и округляет до задланного количества знаков после запятой nums"""
    k = '1.' + nums * '0'
    acc = ((X1 - X2).copy_abs() / get_avg(X1, X2) * Decimal(100)).quantize(Decimal(k), ROUND_HALF_UP)
    return acc

def get_sec(minutes: Decimal, secundes: Decimal):
    """переводит минуты и секунды в секунды и округляет"""
    k = '1.00'
    sec = (minutes * Decimal(60) + secundes).quantize(Decimal(k), ROUND_HALF_UP)
    return Decimal(sec)

def get_abserror(x_avg: Decimal, relerror: Decimal) -> Decimal:
    """находит абсолютную погрешность исходя из Хсреднего и относительной погрешности"""
    abserror = (x_avg * relerror) / Decimal('100')
    return abserror


def get_dateformat(date):
    """переводит дату из формата гггг-мм-дд в дд.мм.гггг"""
    dateformat = str(date)
    day = dateformat[8:]
    month = dateformat[5:7]
    year = dateformat[:4]
    rdate = f'{day}.{month}.{year}'
    return rdate

def get_dateformat_to_number(date):
    """переводит дату из формата гггг-мм-дд в ггммдд01"""
    dateformat = str(date)
    day = dateformat[8:]
    month = dateformat[5:7]
    year = dateformat[2:4]
    rdate = f'{year}{month}{day}01'
    return rdate

def get_round_signif_digit(x_avg: Decimal, numdig: int) -> Decimal:
    """округляет число x_avg до числа значащих цифр numdig для чисел соизмеримых со значением вязкости"""
    aa = x_avg.quantize(Decimal('1.000000000000'), ROUND_HALF_UP)
    a = str(aa)
    if int(a[0]) != 0:
        index1 = numdig + 2
        b = a[0:index1]
        index2 = a.find('.')
        if len(a[0:index2]) <= numdig - 1:
            c = b[index2::]
            numfrac = len(c) - 2
            k = '1.' + numfrac * '0'
            x_res = x_avg.quantize(Decimal(k), ROUND_HALF_UP)
        if len(a[0:index2]) == numdig:
            x_res = x_avg.quantize(Decimal(1), ROUND_HALF_UP)
        if len(a[0:index2]) > numdig:
            d = a[0:index2]
            e = f'{d[:4]}.{d[4:]}'
            f = Decimal(e).quantize(Decimal(1), ROUND_HALF_UP)
            g = str(f) + '0' * (len(d) - 4)
            x_res = Decimal(g)
    if int(a[0]) == 0:
        h = str(x_avg)
        i = 2
        while True:
            if int(h[i]) == 0:
                i += 1
            else:
                break
        numfrac = i + 2
        k = '1.' + numfrac * '0'
        x_res = x_avg.quantize(Decimal(k), ROUND_HALF_UP)
    return x_res

def get_rid_point(value):
    a = str(value)
    b = a.find('.')
    if b != -1 and len(a[b:]) <= 2:
        value = str(value)[0:b]  
    return value



