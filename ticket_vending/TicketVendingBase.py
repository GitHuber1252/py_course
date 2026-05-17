class TicketVendingMachine:
    """Базовый класс автомата по продаже билетов (БАМ). Содержит общие характеристики и методику расчёта технического уровня."""

    # Наименования характеристик (общие для всех автоматов)
    characteristics_names = [
        "Скорость транзакции (сек)",
        "Количество поддерживаемых типов билетов",
        "Наличие приёма наличных (0/1)",
        "Наличие бесконтактной оплаты (0/1)",
        "Наличие биометрии (0/1)",
        "Наличие видеосвязи с оператором (0/1)",
        "Энергопотребление (кВт·ч)",
        "Срок службы (лет)"
    ]

    # Весовые коэффициенты для расчёта технического уровня
    weights = {
        "Скорость транзакции (сек)": 0.20,
        "Количество поддерживаемых типов билетов": 0.25,
        "Наличие приёма наличных (0/1)": 0.10,
        "Наличие бесконтактной оплаты (0/1)": 0.15,
        "Наличие биометрии (0/1)": 0.10,
        "Наличие видеосвязи с оператором (0/1)": 0.05,
        "Энергопотребление (кВт·ч)": 0.05,
        "Срок службы (лет)": 0.10
    }

    # Эталонные диапазоны (min, max) для нормализации (при необходимости)
    reference_ranges = {
        "Скорость транзакции (сек)": (5, 30),
        "Количество поддерживаемых типов билетов": (2, 20),
        "Наличие приёма наличных (0/1)": (0, 1),
        "Наличие бесконтактной оплаты (0/1)": (0, 1),
        "Наличие биометрии (0/1)": (0, 1),
        "Наличие видеосвязи с оператором (0/1)": (0, 1),
        "Энергопотребление (кВт·ч)": (0.1, 0.5),
        "Срок службы (лет)": (5, 15)
    }

    # Характеристики, для которых меньшее значение лучше (инверсные)
    inverse_indicators = ["Скорость транзакции (сек)", "Энергопотребление (кВт·ч)"]

    def __init__(self, name, characteristics):
        """
        Параметры:
        name - наименование модели автомата
        characteristics - словарь с характеристиками (ключи должны соответствовать characteristics_names)
        """
        self.name = name
        self.characteristics = characteristics
        self.technical_level = 0.0

    def calculate_technical_level(self, base_characteristics=None):
        """
        Рассчитывает технический уровень автомата относительно базового образца.
        Если base_characteristics не задан, используется среднее значение эталонного диапазона как база.
        """
        if base_characteristics is None:
            # Используем среднее значение эталонного диапазона в качестве базы по умолчанию
            base_characteristics = {
                char: (self.reference_ranges[char][0] + self.reference_ranges[char][1]) / 2
                for char in self.characteristics_names
            }

        level = 0.0
        for char, weight in self.weights.items():
            value = self.characteristics.get(char)
            if value is None:
                # Если характеристика не задана, используем среднее значение (оценка нейтральная)
                value = base_characteristics[char]

            base_val = base_characteristics[char]
            if base_val == 0:
                rel = 1.0
            else:
                if char in self.inverse_indicators:
                    # Чем меньше, тем лучше
                    rel = base_val / value if value != 0 else 1.0
                else:
                    # Чем больше, тем лучше
                    rel = value / base_val

            level += weight * rel

        self.technical_level = level
        return level

    @classmethod
    def from_input(cls):
        """Создаёт экземпляр класса, запрашивая характеристики у пользователя в консоли."""
        name = input("Введите название модели автомата: ")
        chars = {}
        print("Введите характеристики (для пропуска нажмите Enter, будет использовано среднее значение):")
        for char in cls.characteristics_names:
            prompt = f"{char} (мин {cls.reference_ranges[char][0]}, макс {cls.reference_ranges[char][1]}): "
            val_str = input(prompt).strip()
            if val_str == "":
                # Используем среднее значение диапазона
                val = (cls.reference_ranges[char][0] + cls.reference_ranges[char][1]) / 2
                print(f"  Принято значение по умолчанию: {val}")
            else:
                try:
                    if char.startswith("Наличие"):
                        val = int(val_str)
                    else:
                        val = float(val_str)
                except ValueError:
                    print("Ошибка ввода, используется среднее значение.")
                    val = (cls.reference_ranges[char][0] + cls.reference_ranges[char][1]) / 2
            chars[char] = val
        return cls(name, chars)

    @classmethod
    def from_dict(cls, data):
        """
        Создаёт экземпляр из словаря.
        data должен содержать ключи 'name' и 'characteristics'.
        """
        return cls(data['name'], data['characteristics'])

    def __repr__(self):
        return f"{self.name} (тех. уровень: {self.technical_level:.3f})"