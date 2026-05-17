from .EscalatorBase import EscalatorBase

class LT_series(EscalatorBase):
    """
    Эскалаторы серии ЛТ (1962-1979).
    Модели: ЛТ-3, ЛТ-4, ЛТ-5, ЛП-6 (поэтажные).
    Улучшенная плавность хода и сниженный шум.
    """
    characteristics_names = EscalatorBase.characteristics_names
    
    weights = {
        "Максимальная высота подъема (м)": 0.20,
        "Скорость движения (м/с)": 0.20,
        "Пропускная способность (чел/час)": 0.20,
        "Энергопотребление (кВт·ч)": 0.15,
        "Уровень шума (дБ)": 0.15,
        "Срок службы (лет)": 0.10
    }
    
    reference_ranges = {
        "Максимальная высота подъема (м)": (5, 50),
        "Скорость движения (м/с)": (0.5, 0.75),
        "Пропускная способность (чел/час)": (4000, 10000),
        "Энергопотребление (кВт·ч)": (7, 20),
        "Уровень шума (дБ)": (60, 75),
        "Срок службы (лет)": (25, 45)
    }
    
    @classmethod
    def from_input(cls):
        name = input("Введите модель серии ЛТ (ЛТ-3, ЛТ-4, ЛТ-5, ЛП-6): ")
        chars = {}
        for char in cls.characteristics_names:
            val = float(input(f"Введите {char}: "))
            chars[char] = val
        return cls(name, chars)