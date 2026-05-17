from abc import ABC, abstractmethod

class Metro_train(ABC):
    """Абстрактный базовый класс для всех типов поездов метро."""

    # Список характеристик – будет переопределён в наследниках
    characteristics_names = []
    # Веса характеристик – сумма = 1
    weights = {}
    # Опорные диапазоны (min, max) для нормализации
    reference_ranges = {}

    def __init__(self, name: str, characteristics: dict):
        self.name = name
        self.characteristics = characteristics
        self.technical_level = None

    @classmethod
    @abstractmethod
    def from_input(cls):
        """Ввод характеристик вручную (реализуется в наследниках)."""
        pass

    @classmethod
    def from_dict(cls, data: dict):
        """Создание объекта из словаря (для загрузки из файла)."""
        return cls(data['name'], data['characteristics'])

    def normalize_value(self, char_name: str, value: float) -> float:
        """Нормирование значения к интервалу [0,1]."""
        min_val, max_val = self.reference_ranges[char_name]
        # Если характеристика "шум" или любая другая, где меньше = лучше
        if char_name in ["Уровень шума (дБ)", "Энергопотребление (кВт·ч/км)"]:
            if max_val - min_val == 0:
                return 1.0
            return 1.0 - (value - min_val) / (max_val - min_val)
        else:
            if max_val - min_val == 0:
                return 1.0
            return (value - min_val) / (max_val - min_val)

    def calculate_technical_level(self) -> float:
        """Интегральный технический уровень как взвешенная сумма нормированных значений."""
        total = 0.0
        for char, value in self.characteristics.items():
            if char in self.weights:
                norm_val = self.normalize_value(char, value)
                total += norm_val * self.weights[char]
        self.technical_level = total
        return self.technical_level

    def get_normalized_characteristics(self) -> dict:
        """Возвращает нормированные значения для радиальной диаграммы."""
        return {char: self.normalize_value(char, val) for char, val in self.characteristics.items()}

    def to_dict(self) -> dict:
        """Сериализация в словарь."""
        return {
            'name': self.name,
            'characteristics': self.characteristics
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, level={self.technical_level})"