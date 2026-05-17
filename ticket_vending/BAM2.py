# Файл: tvm/BAM2.py
from ticket_vending.TicketVendingBase import TicketVendingMachine

class BAM2(TicketVendingMachine):
    """БАМ-2: базовые автоматы (2011–2012), только пополнение «Тройки» и билеты на 1–2 поездки."""
    
    # Сохраняем тот же набор характеристик, но корректируем веса
    weights = {
        "Скорость транзакции (сек)": 0.30,
        "Количество поддерживаемых типов билетов": 0.20,
        "Наличие приёма наличных (0/1)": 0.15,
        "Наличие бесконтактной оплаты (0/1)": 0.15,
        "Наличие биометрии (0/1)": 0.00,      # отсутствует
        "Наличие видеосвязи с оператором (0/1)": 0.00,  # отсутствует
        "Энергопотребление (кВт·ч)": 0.10,
        "Срок службы (лет)": 0.10
    }
    
    # Эталонные диапазоны (с учётом более старого оборудования)
    reference_ranges = {
        "Скорость транзакции (сек)": (10, 30),
        "Количество поддерживаемых типов билетов": (2, 5),
        "Наличие приёма наличных (0/1)": (0, 1),
        "Наличие бесконтактной оплаты (0/1)": (0, 1),
        "Наличие биометрии (0/1)": (0, 0),
        "Наличие видеосвязи с оператором (0/1)": (0, 0),
        "Энергопотребление (кВт·ч)": (0.3, 0.5),
        "Срок службы (лет)": (8, 12)
    }
    
    @classmethod
    def from_input(cls):
        name = input("Введите название модели (по умолчанию БАМ-2): ") or "БАМ-2"
        chars = {}
        print("Введите характеристики БАМ-2:")
        for char in cls.characteristics_names:
            if char in ["Наличие биометрии (0/1)", "Наличие видеосвязи с оператором (0/1)"]:
                chars[char] = 0  # фиксировано отсутствует
                continue
            prompt = f"{char} (мин {cls.reference_ranges[char][0]}, макс {cls.reference_ranges[char][1]}): "
            val_str = input(prompt).strip()
            if val_str == "":
                val = (cls.reference_ranges[char][0] + cls.reference_ranges[char][1]) / 2
            else:
                try:
                    val = float(val_str) if "Наличие" not in char else int(val_str)
                except ValueError:
                    val = (cls.reference_ranges[char][0] + cls.reference_ranges[char][1]) / 2
            chars[char] = val
        return cls(name, chars)