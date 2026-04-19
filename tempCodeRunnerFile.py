import Moskva_2020
import Numberseries


if __name__ == "__main__":
    # Пример создания объекта через ручной ввод (закомментировано для автоматического теста)
    # train = NumberSeries.from_input()
    # train.calculate_technical_level()
    # print(train)

    # Пример создания из словаря (имитация загрузки из файла)
    data = {
        'name': '81-717.5М/714.5М',
        'characteristics': {
            "Максимальная скорость (км/ч)": 85,
            "Сидячие места (шт)": 40,
            "Энергопотребление (кВт·ч/км)": 20,
            "Уровень шума (дБ)": 80,
            "Срок службы (лет)": 30
        }
    }
    train1 = Numberseries.from_dict(data)
    print(train1.calculate_technical_level())
    print(train1.get_normalized_characteristics())

    # Пример для «Москва-2020»
    data2 = {
        'name': 'Москва-2020',
        'characteristics': {
            "Максимальная скорость (км/ч)": 95,
            "Сидячие места (шт)": 36,
            "Ширина межвагонного перехода (мм)": 1500,
            "Наличие USB-зарядок (0/1)": 1,
            "Уровень шума (дБ)": 65
        }
    }
    
    print(train1.calculate_technical_level())
    print(train1.get_normalized_characteristics())