class EscalatorBase:
    """Базовый класс эскалатора. Содержит общие характеристики и методику расчёта технического уровня."""
    
    # Наименования характеристик (общие для всех эскалаторов)
    characteristics_names = [
        "Максимальная высота подъема (м)",
        "Скорость движения (м/с)",
        "Пропускная способность (чел/час)",
        "Энергопотребление (кВт·ч)",
        "Уровень шума (дБ)",
        "Срок службы (лет)"
    ]
    
    # Весовые коэффициенты для расчёта технического уровня
    weights = {
        "Максимальная высота подъема (м)": 0.15,
        "Скорость движения (м/с)": 0.25,
        "Пропускная способность (чел/час)": 0.25,
        "Энергопотребление (кВт·ч)": 0.15,
        "Уровень шума (дБ)": 0.10,
        "Срок службы (лет)": 0.10
    }
    
    # Эталонные диапазоны (min, max) для нормализации (при необходимости)
    reference_ranges = {
        "Максимальная высота подъема (м)": (5, 100),
        "Скорость движения (м/с)": (0.5, 1.0),
        "Пропускная способность (чел/час)": (4000, 12000),
        "Энергопотребление (кВт·ч)": (5, 30),
        "Уровень шума (дБ)": (60, 80),
        "Срок службы (лет)": (20, 50)
    }
    
    # Характеристики, для которых меньшее значение лучше (инверсные)
    inverse_indicators = ["Энергопотребление (кВт·ч)", "Уровень шума (дБ)"]
    
    def __init__(self, name, characteristics):
        """
        Параметры:
        name - наименование модели эскалатора
        characteristics - словарь с характеристиками (ключи должны соответствовать characteristics_names)
        """
        self.name = name
        self.characteristics = characteristics
        self.technical_level = 0.0
    
    def calculate_technical_level(self, base_characteristics=None):
        """
        Рассчитывает технический уровень эскалатора относительно базового образца.
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
        name = input("Введите название модели эскалатора: ")
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