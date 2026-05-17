# Файл: tvm/NewGenerationTVM.py
from ticket_vending.TicketVendingBase import TicketVendingMachine

class NewGenerationTVM(TicketVendingMachine):
    """Инновационные автоматы нового поколения: биометрия, видеосвязь, без приёма наличных."""
    
    weights = {
        "Скорость транзакции (сек)": 0.15,
        "Количество поддерживаемых типов билетов": 0.20,
        "Наличие приёма наличных (0/1)": 0.00,  # отсутствует
        "Наличие бесконтактной оплаты (0/1)": 0.20,
        "Наличие биометрии (0/1)": 0.20,
        "Наличие видеосвязи с оператором (0/1)": 0.10,
        "Энергопотребление (кВт·ч)": 0.05,
        "Срок службы (лет)": 0.10
    }
    
    reference_ranges = {
        "Скорость транзакции (сек)": (5, 15),
        "Количество поддерживаемых типов билетов": (10, 20),
        "Наличие приёма наличных (0/1)": (0, 0),
        "Наличие бесконтактной оплаты (0/1)": (1, 1),
        "Наличие биометрии (0/1)": (1, 1),
        "Наличие видеосвязи с оператором (0/1)": (1, 1),
        "Энергопотребление (кВт·ч)": (0.1, 0.3),
        "Срок службы (лет)": (10, 15)
    }
    
    @classmethod
    def from_input(cls):
        name = input("Введите название модели (по умолчанию Инновационный автомат): ") or "Инновационный автомат"
        chars = {}
        print("Введите характеристики автомата нового поколения:")
        for char in cls.characteristics_names:
            if char == "Наличие приёма наличных (0/1)":
                chars[char] = 0
                continue
            if char in ["Наличие бесконтактной оплаты (0/1)", "Наличие биометрии (0/1)", "Наличие видеосвязи с оператором (0/1)"]:
                chars[char] = 1
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