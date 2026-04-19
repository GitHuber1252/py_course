import matplotlib.pyplot as plt
import numpy as np

from Numberseries import Numberseries
from Rusich import Rusich
from Oka import Oka
from Moskva import Moskva
from Moskva_2020 import Moskva_2020

# ========== Функции для работы с данными ==========

def unify_to_numberseries_characteristics(train):
    """
    Приводит характеристики объекта к набору характеристик Numberseries:
    - Максимальная скорость (км/ч)
    - Сидячие места (шт)
    - Энергопотребление (кВт·ч/км)
    - Уровень шума (дБ)
    - Срок службы (лет)

    Если характеристика отсутствует в объекте, используется значение по умолчанию.
    """
    default = {
        "Максимальная скорость (км/ч)": 85,
        "Сидячие места (шт)": 40,
        "Энергопотребление (кВт·ч/км)": 20,
        "Уровень шума (дБ)": 75,
        "Срок службы (лет)": 30
    }
    unified = {}
    for key in default:
        if key in train.characteristics:
            unified[key] = train.characteristics[key]
        else:
            unified[key] = default[key]
    return unified


def normalize_relative_to_base(chars, base_chars):
    """
    Нормирует характеристики делением на значения базового образца.
    Для шума и энергопотребления, где чем меньше, тем лучше,
    используется обратное отношение (base / value), чтобы сохранить смысл.
    """
    normalized = {}
    for key in chars:
        value = chars[key]
        base_val = base_chars[key]
        if base_val == 0:
            normalized[key] = 1.0
        else:
            # Характеристики, где меньше = лучше
            if key == "Уровень шума (дБ)" or key == "Энергопотребление (кВт·ч/км)":
                if value != 0:
                    normalized[key] = base_val / value
                else:
                    normalized[key] = 1.0
            else:
                normalized[key] = value / base_val
    return normalized


def create_radial_relative(trains_data, base_name, base_chars, title="Сравнение характеристик"):
    """
    Строит радиальную диаграмму для нескольких объектов,
    используя относительные значения (деление на базовый образец).
    trains_data: список кортежей (имя_объекта, унифицированные_характеристики)
    base_chars: характеристики базового образца (для нормализации)
    """
    if not trains_data:
        print("Нет данных для радиальной диаграммы.")
        return

    char_names = []
    for key in base_chars:
        char_names.append(key)

    # Углы для осей
    angles = []
    step = 2 * np.pi / len(char_names)
    for i in range(len(char_names)):
        angles.append(i * step)
    angles.append(angles[0])  # замыкаем круг

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))

    for name, chars in trains_data:
        rel = normalize_relative_to_base(chars, base_chars)
        values = []
        for char in char_names:
            values.append(rel[char])
        values.append(values[0])  # замыкаем

        ax.plot(angles, values, 'o-', linewidth=2, label=name)

    # Подписи осей
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(char_names, fontsize=10)

    # Находим максимальное значение для масштаба
    max_val = 0
    for _, chars in trains_data:
        rel = normalize_relative_to_base(chars, base_chars)
        for char in char_names:
            if rel[char] > max_val:
                max_val = rel[char]
    ax.set_ylim(0, max_val + 0.1)

    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
    ax.set_title(title, pad=20)
    plt.tight_layout()
    plt.show()


def create_bar_chart_relative(trains, base_train):
    """
    Столбчатая диаграмма технического уровня относительно базового образца.
    """
    base_level = base_train.technical_level
    names = []
    rel_levels = []
    for t in trains:
        names.append(t.name + "\n(" + t.__class__.__name__ + ")")
        rel_levels.append(t.technical_level / base_level)

    # Сортируем по убыванию rel_levels (простой пузырьковой сортировкой)
    n = len(rel_levels)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if rel_levels[j] < rel_levels[j + 1]:
                # Меняем местами значения
                rel_levels[j], rel_levels[j + 1] = rel_levels[j + 1], rel_levels[j]
                names[j], names[j + 1] = names[j + 1], names[j]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, rel_levels, color='skyblue')
    # Подписываем значения
    for i in range(len(bars)):
        bar = bars[i]
        val = rel_levels[i]
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 '%.2f' % val, ha='center', va='bottom')

    plt.xlabel("Образец")
    plt.ylabel("Относительный технический уровень (база = 1)")
    plt.title("Сравнение технического уровня образцов (Numberseries = 1)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


# ========== Основная программа ==========

def main():
    # Создаём базовый объект (Numberseries)
    base_train = Numberseries.from_dict({
        'name': '81-717.5М/714.5М (базовый)',
        'characteristics': {
            "Максимальная скорость (км/ч)": 85,
            "Сидячие места (шт)": 40,
            "Энергопотребление (кВт·ч/км)": 20,
            "Уровень шума (дБ)": 80,
            "Срок службы (лет)": 30
        }
    })
    base_train.calculate_technical_level()
    print("Базовый объект: %s -> уровень = %.4f" % (base_train.name, base_train.technical_level))

    # Создаём остальные объекты
    train_rusich = Rusich.from_dict({
        'name': '81-740.4/741.4 «Русич»',
        'characteristics': {
            "Максимальная скорость (км/ч)": 90,
            "Сидячие места (шт)": 46,
            "Ширина дверного проёма (мм)": 1400,
            "Наличие кондиционирования (0/1)": 1,
            "Уровень шума (дБ)": 72
        }
    })

    train_oka = Oka.from_dict({
        'name': '81-760А/761А/763А «Ока»',
        'characteristics': {
            "Максимальная скорость (км/ч)": 95,
            "Сидячие места (шт)": 40,
            "Наличие сквозного прохода (0/1)": 1,
            "Энергопотребление (кВт·ч/км)": 22,
            "Уровень шума (дБ)": 75
        }
    })

    train_moskva = Moskva.from_dict({
        'name': '81-765.4/766.4/767.4 «Москва-2019»',
        'characteristics': {
            "Максимальная скорость (км/ч)": 95,
            "Сидячие места (шт)": 38,
            "Ширина дверного проёма (мм)": 1600,
            "Наличие USB-зарядок (0/1)": 1,
            "Уровень шума (дБ)": 68
        }
    })

    train_moskva2020 = Moskva_2020.from_dict({
        'name': '81-775/776/777 «Москва-2020»',
        'characteristics': {
            "Максимальная скорость (км/ч)": 100,
            "Сидячие места (шт)": 36,
            "Ширина межвагонного перехода (мм)": 1600,
            "Наличие USB-зарядок (0/1)": 1,
            "Уровень шума (дБ)": 65
        }
    })

    all_trains = [base_train, train_rusich, train_oka, train_moskva, train_moskva2020]

    # Вычисляем технический уровень для всех (каждый по своим весам)
    for t in all_trains:
        t.calculate_technical_level()
        print("%s (%s): уровень = %.4f" % (t.name, t.__class__.__name__, t.technical_level))

    # Столбчатая диаграмма относительно базового
    create_bar_chart_relative(all_trains, base_train)

    # Подготавливаем унифицированные характеристики для радиальной диаграммы
    base_unified = unify_to_numberseries_characteristics(base_train)
    unified_data = []
    for t in all_trains:
        unified = unify_to_numberseries_characteristics(t)
        unified_data.append((t.name, unified))

    # Радиальная диаграмма с нормализацией относительно базового
    print("\nРадиальная диаграмма (база = Numberseries):")
    create_radial_relative(unified_data, base_train.name, base_unified,
                           title="Сравнение характеристик (относительно базового образца)")


if __name__ == "__main__":
    main()