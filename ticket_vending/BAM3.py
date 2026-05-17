# Файл: tvm/BAM3.py
from ticket_vending.TicketVendingBase import TicketVendingMachine

class BAM3(TicketVendingMachine):
    """БАМ-3: полнофункциональные автоматы, поддержка всех типов билетов и социальных карт."""
    
    weights = {
        "Скорость транзакции (сек)": 0.20,
        "Количество поддерживаемых типов билетов": 0.30,
        "Наличие приёма наличных (0/1)": 0.15,
        "Наличие бесконтактной оплаты (0/1)": 0.15,
        "Наличие биометрии (0/1)": 0.00,      # отсутствует
        "Наличие видеосвязи с оператором (0/1)": 0.00,  # отсутствует
        "Энергопотребление (кВт·ч)": 0.10,
        "Срок службы (лет)": 0.10
    }
    
    reference_ranges = {
        "Скорость транзакции (сек)": (8, 20),
        "Количество поддерживаемых типов билетов": (5, 15),
        "Наличие приёма наличных (0/1)": (0, 1),
        "Наличие бесконтактной оплаты (0/1)": (0, 1),
        "Наличие биометрии (0/1)": (0, 0),
        "Наличие видеосвязи с оператором (0/1)": (0, 0),
        "Энергопотребление (кВт·ч)": (0.2, 0.4),
        "Срок службы (лет)": (8, 12)
    }
    
    @classmethod
    def from_input(cls):
        name = input("Введите название модели (по умолчанию БАМ-3): ") or "БАМ-3"
        chars = {}
        print("Введите характеристики БАМ-3:")
        for char in cls.characteristics_names:
            if char in ["Наличие биометрии (0/1)", "Наличие видеосвязи с оператором (0/1)"]:
                chars[char] = 0
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