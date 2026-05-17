# Файл: tvm/InformationTerminal.py
from ticket_vending.TicketVendingBase import TicketVendingMachine

class InformationTerminal(TicketVendingMachine):
    """Информационные терминалы: продажа билетов на карту, безналичная оплата (NFC, Apple Pay)."""
    
    weights = {
        "Скорость транзакции (сек)": 0.25,
        "Количество поддерживаемых типов билетов": 0.20,
        "Наличие приёма наличных (0/1)": 0.00,  # нет приёма наличных
        "Наличие бесконтактной оплаты (0/1)": 0.25,
        "Наличие биометрии (0/1)": 0.00,
        "Наличие видеосвязи с оператором (0/1)": 0.00,
        "Энергопотребление (кВт·ч)": 0.15,
        "Срок службы (лет)": 0.15
    }
    
    reference_ranges = {
        "Скорость транзакции (сек)": (5, 20),
        "Количество поддерживаемых типов билетов": (5, 15),
        "Наличие приёма наличных (0/1)": (0, 0),
        "Наличие бесконтактной оплаты (0/1)": (1, 1),
        "Наличие биометрии (0/1)": (0, 0),
        "Наличие видеосвязи с оператором (0/1)": (0, 0),
        "Энергопотребление (кВт·ч)": (0.2, 0.4),
        "Срок службы (лет)": (8, 12)
    }
    
    @classmethod
    def from_input(cls):
        name = input("Введите название модели (по умолчанию Информационный терминал): ") or "Информационный терминал"
        chars = {}
        print("Введите характеристики информационного терминала:")
        for char in cls.characteristics_names:
            if char == "Наличие приёма наличных (0/1)":
                chars[char] = 0
                continue
            if char == "Наличие бесконтактной оплаты (0/1)":
                chars[char] = 1
                continue
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