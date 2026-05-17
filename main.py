import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import matplotlib.pyplot as plt
import numpy as np

# Импорт классов поездов
from trains.Numberseries import Numberseries
from trains.Rusich import Rusich
from trains.Oka import Oka
from trains.Moskva import Moskva
from trains.Moskva_2020 import Moskva_2020

# Импорт классов эскалаторов
from escalators.EscalatorBase import EscalatorBase
from escalators.EscalatorN import N_series
from escalators.EscalatorEM import EM_series
from escalators.EscalatorLT import LT_series
from escalators.EscalatorET import ET_series
from escalators.EscalatorE import E_series
from escalators.EscalatorModern import Modern_series

from PassengerForecast import PassengerForecast

# Импорт классов билетных автоматов
from ticket_vending.TicketVendingBase import TicketVendingMachine
from ticket_vending.BAM2 import BAM2
from ticket_vending.BAM3 import BAM3
from ticket_vending.NewTerminal import NewGenerationTVM
from ticket_vending.InfoTerminal import InformationTerminal

# ========== Вспомогательные функции ==========

def unify_to_numberseries_characteristics(train):
    default = {
        "Максимальная скорость (км/ч)": 85,
        "Сидячие места (шт)": 40,
        "Энергопотребление (кВт·ч/км)": 20,
        "Уровень шума (дБ)": 75,
        "Срок службы (лет)": 30
    }
    unified = {}
    for key in default:
        unified[key] = train.characteristics.get(key, default[key])
    return unified

def normalize_relative_to_base(chars, base_chars, inverse_keys):
    normalized = {}
    for key in chars:
        value = chars[key]
        base_val = base_chars[key]
        if base_val == 0:
            normalized[key] = 1.0
        else:
            if key in inverse_keys:
                normalized[key] = base_val / value if value != 0 else 1.0
            else:
                normalized[key] = value / base_val
    return normalized

def create_radial_relative(data, base_chars, inverse_keys, title="Сравнение характеристик"):
    if not data:
        print("Нет данных для радиальной диаграммы.")
        return

    char_names = list(base_chars.keys())
    angles = np.linspace(0, 2 * np.pi, len(char_names), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))

    for name, chars in data:
        rel = normalize_relative_to_base(chars, base_chars, inverse_keys)
        values = [rel[char] for char in char_names]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=name)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(char_names, fontsize=10)
    ax.set_ylim(0, max([max(normalize_relative_to_base(chars, base_chars, inverse_keys).values())
                         for _, chars in data]) + 0.1)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
    ax.set_title(title, pad=20)
    plt.tight_layout()
    plt.show()

def create_bar_chart_relative(objects, base_obj, title="Сравнение технического уровня"):
    base_level = base_obj.technical_level
    names = [f"{obj.name}\n({obj.__class__.__name__})" for obj in objects]
    rel_levels = [obj.technical_level / base_level for obj in objects]

    sorted_pairs = sorted(zip(rel_levels, names), reverse=True)
    rel_levels, names = zip(*sorted_pairs)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, rel_levels, color='skyblue')
    for bar, val in zip(bars, rel_levels):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f"{val:.2f}", ha='center', va='bottom')
    plt.xlabel("Образец")
    plt.ylabel("Относительный технический уровень (база = 1)")
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# ========== Унификация для эскалаторов ==========
def unify_to_escalatorbase_characteristics(escalator):
    default = {
        "Максимальная высота подъема (м)": 30,
        "Скорость движения (м/с)": 0.75,
        "Пропускная способность (чел/час)": 8000,
        "Энергопотребление (кВт·ч)": 15,
        "Уровень шума (дБ)": 70,
        "Срок службы (лет)": 40
    }
    unified = {}
    for key in default:
        unified[key] = escalator.characteristics.get(key, default[key])
    return unified

# ========== Унификация для билетных автоматов ==========
def unify_to_tvm_characteristics(machine, exclude_binary=False):
    default = {
        "Скорость транзакции (сек)": 15,
        "Количество поддерживаемых типов билетов": 8,
        "Наличие приёма наличных (0/1)": 1,
        "Наличие бесконтактной оплаты (0/1)": 1,
        "Наличие биометрии (0/1)": 0,
        "Наличие видеосвязи с оператором (0/1)": 0,
        "Энергопотребление (кВт·ч)": 0.3,
        "Срок службы (лет)": 10
    }
    binary_keys = ["Наличие приёма наличных (0/1)", "Наличие бесконтактной оплаты (0/1)",
                   "Наличие биометрии (0/1)", "Наличие видеосвязи с оператором (0/1)"]
    unified = {}
    for key in default:
        if exclude_binary and key in binary_keys:
            continue
        unified[key] = machine.characteristics.get(key, default[key])
    return unified

# ========== Инициализация предустановленных данных ==========
def create_default_trains():
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
    for t in all_trains:
        t.calculate_technical_level()
    return base_train, all_trains

def create_default_escalators():
    base_esc = N_series.from_dict({
        'name': 'Эскалатор серии Н',
        'characteristics': {
            "Максимальная высота подъема (м)": 40,
            "Скорость движения (м/с)": 0.75,
            "Пропускная способность (чел/час)": 8000,
            "Энергопотребление (кВт·ч)": 20,
            "Уровень шума (дБ)": 75,
            "Срок службы (лет)": 30
        }
    })
    base_esc.calculate_technical_level()

    esc_em = EM_series.from_dict({
        'name': 'Эскалатор серии ЭМ',
        'characteristics': {
            "Максимальная высота подъема (м)": 53.5,
            "Скорость движения (м/с)": 0.8,
            "Пропускная способность (чел/час)": 8500,
            "Энергопотребление (кВт·ч)": 18,
            "Уровень шума (дБ)": 72,
            "Срок службы (лет)": 35
        }
    })

    esc_lt = LT_series.from_dict({
        'name': 'Эскалатор серии ЛТ',
        'characteristics': {
            "Максимальная высота подъема (м)": 50,
            "Скорость движения (м/с)": 0.9,
            "Пропускная способность (чел/час)": 9000,
            "Энергопотребление (кВт·ч)": 16,
            "Уровень шума (дБ)": 70,
            "Срок службы (лет)": 40
        }
    })

    esc_et = ET_series.from_dict({
        'name': 'Эскалатор серии ЭТ',
        'characteristics': {
            "Максимальная высота подъема (м)": 65,
            "Скорость движения (м/с)": 0.95,
            "Пропускная способность (чел/час)": 9500,
            "Энергопотребление (кВт·ч)": 15,
            "Уровень шума (дБ)": 68,
            "Срок службы (лет)": 45
        }
    })

    esc_e = E_series.from_dict({
        'name': 'Эскалатор серии Е',
        'characteristics': {
            "Максимальная высота подъема (м)": 75,
            "Скорость движения (м/с)": 1.0,
            "Пропускная способность (чел/час)": 10000,
            "Энергопотребление (кВт·ч)": 14,
            "Уровень шума (дБ)": 65,
            "Срок службы (лет)": 50
        }
    })

    esc_modern = Modern_series.from_dict({
        'name': 'Современные серии эскалаторов (ТК-65, FT-935 и др.)',
        'characteristics': {
            "Максимальная высота подъема (м)": 100,
            "Скорость движения (м/с)": 1.0,
            "Пропускная способность (чел/час)": 12000,
            "Энергопотребление (кВт·ч)": 12,
            "Уровень шума (дБ)": 62,
            "Срок службы (лет)": 50
        }
    })

    all_escalators = [base_esc, esc_em, esc_lt, esc_et, esc_e, esc_modern]
    for e in all_escalators:
        e.calculate_technical_level()
    return base_esc, all_escalators

def create_default_tvm():
    base_tvm = BAM2.from_dict({
        'name': 'БАМ-2',
        'characteristics': {
            "Скорость транзакции (сек)": 25,
            "Количество поддерживаемых типов билетов": 3,
            "Наличие приёма наличных (0/1)": 1,
            "Наличие бесконтактной оплаты (0/1)": 0,
            "Наличие биометрии (0/1)": 0,
            "Наличие видеосвязи с оператором (0/1)": 0,
            "Энергопотребление (кВт·ч)": 0.4,
            "Срок службы (лет)": 10
        }
    })
    base_tvm.calculate_technical_level()

    tvm_bam3 = BAM3.from_dict({
        'name': 'БАМ-3',
        'characteristics': {
            "Скорость транзакции (сек)": 18,
            "Количество поддерживаемых типов билетов": 12,
            "Наличие приёма наличных (0/1)": 1,
            "Наличие бесконтактной оплаты (0/1)": 1,
            "Наличие биометрии (0/1)": 0,
            "Наличие видеосвязи с оператором (0/1)": 0,
            "Энергопотребление (кВт·ч)": 0.35,
            "Срок службы (лет)": 10
        }
    })

    tvm_newgen = NewGenerationTVM.from_dict({
        'name': 'Инновационный автомат (новое поколение)',
        'characteristics': {
            "Скорость транзакции (сек)": 10,
            "Количество поддерживаемых типов билетов": 15,
            "Наличие приёма наличных (0/1)": 0,
            "Наличие бесконтактной оплаты (0/1)": 1,
            "Наличие биометрии (0/1)": 1,
            "Наличие видеосвязи с оператором (0/1)": 1,
            "Энергопотребление (кВт·ч)": 0.25,
            "Срок службы (лет)": 12
        }
    })

    tvm_infoterm = InformationTerminal.from_dict({
        'name': 'Информационный терминал',
        'characteristics': {
            "Скорость транзакции (сек)": 15,
            "Количество поддерживаемых типов билетов": 10,
            "Наличие приёма наличных (0/1)": 0,
            "Наличие бесконтактной оплаты (0/1)": 1,
            "Наличие биометрии (0/1)": 0,
            "Наличие видеосвязи с оператором (0/1)": 0,
            "Энергопотребление (кВт·ч)": 0.3,
            "Срок службы (лет)": 10
        }
    })

    all_tvm = [base_tvm, tvm_bam3, tvm_newgen, tvm_infoterm]
    for m in all_tvm:
        m.calculate_technical_level()
    return base_tvm, all_tvm

# ========== Класс приложения ==========
class TransportComparisonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сравнение транспортных средств")
        self.root.geometry("800x600")

        # Данные поездов
        self.base_train, self.default_trains = create_default_trains()
        self.user_trains = []

        # Данные эскалаторов
        self.base_esc, self.default_escalators = create_default_escalators()
        self.user_escalators = []

        # Данные билетных автоматов
        self.base_tvm, self.default_tvm = create_default_tvm()
        self.user_tvm = []

        # Прогноз 
        self.forecast_model = PassengerForecast('Metro.csv')

        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладки предустановленных данных
        self.frame_trains_default = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_trains_default, text="Поезда")
        self.setup_trains_default_tab()

        self.frame_escalators = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_escalators, text="Эскалаторы")
        self.setup_escalators_tab()

        self.frame_tvm = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_tvm, text="Билетные автоматы")
        self.setup_tvm_tab()

        # Вкладки загрузки JSON
        self.frame_trains_user = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_trains_user, text="Поезда (загрузить JSON)")
        self.setup_trains_user_tab()

        self.frame_escalators_user = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_escalators_user, text="Эскалаторы (загрузить JSON)")
        self.setup_escalators_user_tab()

        self.frame_tvm_user = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_tvm_user, text="Билетные автоматы (загрузить JSON)")
        self.setup_tvm_user_tab()

        self.frame_forecast = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_forecast, text="Прогноз")
        self.setup_forecast_tab()
        

    # ------------------- Вкладка поездов (предустановленные) -------------------
    def setup_trains_default_tab(self):
        columns = ('name', 'level')
        self.tree_trains_default = ttk.Treeview(self.frame_trains_default, columns=columns, show='headings', height=8)
        self.tree_trains_default.heading('name', text='Название поезда')
        self.tree_trains_default.heading('level', text='Технический уровень')
        self.tree_trains_default.column('name', width=400)
        self.tree_trains_default.column('level', width=150, anchor='center')
        self.tree_trains_default.pack(pady=10, padx=10, fill='both', expand=True)
        self.update_trains_default_table()
        btn_plot = ttk.Button(self.frame_trains_default, text="Построить диаграммы",
                              command=self.plot_trains_default_diagrams)
        btn_plot.pack(pady=10)

    def update_trains_default_table(self):
        for item in self.tree_trains_default.get_children():
            self.tree_trains_default.delete(item)
        for train in self.default_trains:
            self.tree_trains_default.insert('', 'end', values=(train.name, f"{train.technical_level:.4f}"))

    def plot_trains_default_diagrams(self):
        create_bar_chart_relative(self.default_trains, self.base_train,
                                  title="Сравнение технического уровня поездов (база = Numberseries)")
        base_unified = unify_to_numberseries_characteristics(self.base_train)
        unified_data = [(t.name, unify_to_numberseries_characteristics(t)) for t in self.default_trains]
        create_radial_relative(unified_data, base_unified,
                               inverse_keys=["Уровень шума (дБ)", "Энергопотребление (кВт·ч/км)"],
                               title="Сравнение характеристик поездов (относительно базового)")

    # ------------------- Вкладка поездов (загрузка JSON) -------------------
    def setup_trains_user_tab(self):
        lbl_info = ttk.Label(self.frame_trains_user,
                             text="Загрузите JSON-файл с данными поездов.\n"
                                  "Формат: список объектов с полями 'name' и 'characteristics'.\n"
                                  "Характеристики: Максимальная скорость (км/ч), Сидячие места (шт),\n"
                                  "Энергопотребление (кВт·ч/км), Уровень шума (дБ), Срок службы (лет).")
        lbl_info.pack(pady=10)
        btn_load = ttk.Button(self.frame_trains_user, text="Загрузить JSON", command=self.load_trains_json)
        btn_load.pack(pady=5)
        columns = ('name', 'level')
        self.tree_trains_user = ttk.Treeview(self.frame_trains_user, columns=columns, show='headings', height=6)
        self.tree_trains_user.heading('name', text='Название поезда')
        self.tree_trains_user.heading('level', text='Технический уровень')
        self.tree_trains_user.column('name', width=400)
        self.tree_trains_user.column('level', width=150, anchor='center')
        self.tree_trains_user.pack(pady=10, padx=10, fill='both', expand=True)
        self.btn_plot_trains_user = ttk.Button(self.frame_trains_user, text="Построить диаграммы по загруженным данным",
                                               command=self.plot_trains_user_diagrams, state='disabled')
        self.btn_plot_trains_user.pack(pady=10)

    def load_trains_json(self):
        filepath = filedialog.askopenfilename(
            title="Выберите JSON-файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            return
        if not isinstance(data, list):
            messagebox.showerror("Ошибка", "JSON должен содержать список объектов.")
            return
        self.user_trains.clear()
        for item in self.tree_trains_user.get_children():
            self.tree_trains_user.delete(item)
        for idx, item in enumerate(data):
            if not isinstance(item, dict) or 'name' not in item or 'characteristics' not in item:
                messagebox.showwarning("Предупреждение",
                                       f"Элемент {idx} пропущен: отсутствуют 'name' или 'characteristics'.")
                continue
            try:
                train = Numberseries.from_dict(item)
                train.calculate_technical_level()
                self.user_trains.append(train)
                self.tree_trains_user.insert('', 'end', values=(train.name, f"{train.technical_level:.4f}"))
            except Exception as e:
                messagebox.showwarning("Предупреждение",
                                       f"Не удалось создать поезд из элемента {idx}:\n{e}")
        if self.user_trains:
            self.btn_plot_trains_user.config(state='normal')
            messagebox.showinfo("Готово", f"Загружено поездов: {len(self.user_trains)}")
        else:
            self.btn_plot_trains_user.config(state='disabled')
            messagebox.showwarning("Внимание", "Не удалось загрузить ни одного поезда.")

    def plot_trains_user_diagrams(self):
        if not self.user_trains:
            messagebox.showwarning("Нет данных", "Сначала загрузите корректный JSON-файл.")
            return
        all_for_bar = [self.base_train] + self.user_trains
        create_bar_chart_relative(all_for_bar, self.base_train,
                                  title="Сравнение технического уровня (пользовательские поезда)")
        base_unified = unify_to_numberseries_characteristics(self.base_train)
        unified_data = [(t.name, unify_to_numberseries_characteristics(t)) for t in self.user_trains]
        create_radial_relative(unified_data, base_unified,
                               inverse_keys=["Уровень шума (дБ)", "Энергопотребление (кВт·ч/км)"],
                               title="Сравнение характеристик загруженных поездов (база = Numberseries)")

    # ------------------- Вкладка эскалаторов (предустановленные) -------------------
    def setup_escalators_tab(self):
        columns = ('name', 'level')
        self.tree_escalators = ttk.Treeview(self.frame_escalators, columns=columns, show='headings', height=8)
        self.tree_escalators.heading('name', text='Название эскалатора')
        self.tree_escalators.heading('level', text='Технический уровень')
        self.tree_escalators.column('name', width=400)
        self.tree_escalators.column('level', width=150, anchor='center')
        self.tree_escalators.pack(pady=10, padx=10, fill='both', expand=True)
        self.update_escalators_table()
        btn_plot = ttk.Button(self.frame_escalators, text="Построить диаграммы",
                              command=self.plot_escalators_diagrams)
        btn_plot.pack(pady=10)

    def update_escalators_table(self):
        for item in self.tree_escalators.get_children():
            self.tree_escalators.delete(item)
        for esc in self.default_escalators:
            self.tree_escalators.insert('', 'end', values=(esc.name, f"{esc.technical_level:.4f}"))

    def plot_escalators_diagrams(self):
        create_bar_chart_relative(self.default_escalators, self.base_esc,
                                  title="Сравнение технического уровня эскалаторов (база = серия Н)")
        base_unified = unify_to_escalatorbase_characteristics(self.base_esc)
        unified_data = [(e.name, unify_to_escalatorbase_characteristics(e)) for e in self.default_escalators]
        create_radial_relative(unified_data, base_unified,
                               inverse_keys=["Энергопотребление (кВт·ч)", "Уровень шума (дБ)"],
                               title="Сравнение характеристик эскалаторов (относительно базового)")

    # ------------------- Вкладка эскалаторов (загрузка JSON) -------------------
    def setup_escalators_user_tab(self):
        lbl_info = ttk.Label(self.frame_escalators_user,
                             text="Загрузите JSON-файл с данными эскалаторов.\n"
                                  "Формат: список объектов с полями 'name' и 'characteristics'.\n"
                                  "Характеристики: Максимальная высота подъема (м), Скорость движения (м/с),\n"
                                  "Пропускная способность (чел/час), Энергопотребление (кВт·ч),\n"
                                  "Уровень шума (дБ), Срок службы (лет).")
        lbl_info.pack(pady=10)
        btn_load = ttk.Button(self.frame_escalators_user, text="Загрузить JSON", command=self.load_escalators_json)
        btn_load.pack(pady=5)
        columns = ('name', 'level')
        self.tree_escalators_user = ttk.Treeview(self.frame_escalators_user, columns=columns, show='headings', height=6)
        self.tree_escalators_user.heading('name', text='Название эскалатора')
        self.tree_escalators_user.heading('level', text='Технический уровень')
        self.tree_escalators_user.column('name', width=400)
        self.tree_escalators_user.column('level', width=150, anchor='center')
        self.tree_escalators_user.pack(pady=10, padx=10, fill='both', expand=True)
        self.btn_plot_escalators_user = ttk.Button(self.frame_escalators_user, text="Построить диаграммы по загруженным данным",
                                                   command=self.plot_escalators_user_diagrams, state='disabled')
        self.btn_plot_escalators_user.pack(pady=10)

    def load_escalators_json(self):
        filepath = filedialog.askopenfilename(
            title="Выберите JSON-файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            return
        if not isinstance(data, list):
            messagebox.showerror("Ошибка", "JSON должен содержать список объектов.")
            return
        self.user_escalators.clear()
        for item in self.tree_escalators_user.get_children():
            self.tree_escalators_user.delete(item)
        for idx, item in enumerate(data):
            if not isinstance(item, dict) or 'name' not in item or 'characteristics' not in item:
                messagebox.showwarning("Предупреждение",
                                       f"Элемент {idx} пропущен: отсутствуют 'name' или 'characteristics'.")
                continue
            try:
                # Используем базовый класс EscalatorBase для создания объекта
                esc = EscalatorBase.from_dict(item)
                esc.calculate_technical_level()
                self.user_escalators.append(esc)
                self.tree_escalators_user.insert('', 'end', values=(esc.name, f"{esc.technical_level:.4f}"))
            except Exception as e:
                messagebox.showwarning("Предупреждение",
                                       f"Не удалось создать эскалатор из элемента {idx}:\n{e}")
        if self.user_escalators:
            self.btn_plot_escalators_user.config(state='normal')
            messagebox.showinfo("Готово", f"Загружено эскалаторов: {len(self.user_escalators)}")
        else:
            self.btn_plot_escalators_user.config(state='disabled')
            messagebox.showwarning("Внимание", "Не удалось загрузить ни одного эскалатора.")

    def plot_escalators_user_diagrams(self):
        if not self.user_escalators:
            messagebox.showwarning("Нет данных", "Сначала загрузите корректный JSON-файл.")
            return
        all_for_bar = [self.base_esc] + self.user_escalators
        create_bar_chart_relative(all_for_bar, self.base_esc,
                                  title="Сравнение технического уровня (пользовательские эскалаторы)")
        base_unified = unify_to_escalatorbase_characteristics(self.base_esc)
        unified_data = [(e.name, unify_to_escalatorbase_characteristics(e)) for e in self.user_escalators]
        create_radial_relative(unified_data, base_unified,
                               inverse_keys=["Энергопотребление (кВт·ч)", "Уровень шума (дБ)"],
                               title="Сравнение характеристик загруженных эскалаторов (база = серия Н)")

    # ------------------- Вкладка билетных автоматов (предустановленные) -------------------
    def setup_tvm_tab(self):
        columns = ('name', 'level')
        self.tree_tvm = ttk.Treeview(self.frame_tvm, columns=columns, show='headings', height=8)
        self.tree_tvm.heading('name', text='Название автомата')
        self.tree_tvm.heading('level', text='Технический уровень')
        self.tree_tvm.column('name', width=400)
        self.tree_tvm.column('level', width=150, anchor='center')
        self.tree_tvm.pack(pady=10, padx=10, fill='both', expand=True)
        self.update_tvm_table()
        btn_plot = ttk.Button(self.frame_tvm, text="Построить диаграммы",
                              command=self.plot_tvm_diagrams)
        btn_plot.pack(pady=10)

    def update_tvm_table(self):
        for item in self.tree_tvm.get_children():
            self.tree_tvm.delete(item)
        for tvm in self.default_tvm:
            self.tree_tvm.insert('', 'end', values=(tvm.name, f"{tvm.technical_level:.4f}"))

    def plot_tvm_diagrams(self):
        create_bar_chart_relative(self.default_tvm, self.base_tvm,
                                  title="Сравнение технического уровня билетных автоматов (база = БАМ-2)")
        base_unified = unify_to_tvm_characteristics(self.base_tvm, exclude_binary=True)
        unified_data = [(m.name, unify_to_tvm_characteristics(m, exclude_binary=True)) for m in self.default_tvm]
        create_radial_relative(unified_data, base_unified,
                               inverse_keys=["Скорость транзакции (сек)", "Энергопотребление (кВт·ч)"],
                               title="Сравнение характеристик билетных автоматов (без учёта бинарных признаков)")

    # ------------------- Вкладка билетных автоматов (загрузка JSON) -------------------
    def setup_tvm_user_tab(self):
        lbl_info = ttk.Label(self.frame_tvm_user,
                             text="Загрузите JSON-файл с данными билетных автоматов.\n"
                                  "Формат: список объектов с полями 'name' и 'characteristics'.\n"
                                  "Характеристики: Скорость транзакции (сек), Количество поддерживаемых типов билетов,\n"
                                  "Наличие приёма наличных (0/1), Наличие бесконтактной оплаты (0/1),\n"
                                  "Наличие биометрии (0/1), Наличие видеосвязи с оператором (0/1),\n"
                                  "Энергопотребление (кВт·ч), Срок службы (лет).")
        lbl_info.pack(pady=10)
        btn_load = ttk.Button(self.frame_tvm_user, text="Загрузить JSON", command=self.load_tvm_json)
        btn_load.pack(pady=5)
        columns = ('name', 'level')
        self.tree_tvm_user = ttk.Treeview(self.frame_tvm_user, columns=columns, show='headings', height=6)
        self.tree_tvm_user.heading('name', text='Название автомата')
        self.tree_tvm_user.heading('level', text='Технический уровень')
        self.tree_tvm_user.column('name', width=400)
        self.tree_tvm_user.column('level', width=150, anchor='center')
        self.tree_tvm_user.pack(pady=10, padx=10, fill='both', expand=True)
        self.btn_plot_tvm_user = ttk.Button(self.frame_tvm_user, text="Построить диаграммы по загруженным данным",
                                            command=self.plot_tvm_user_diagrams, state='disabled')
        self.btn_plot_tvm_user.pack(pady=10)

    def load_tvm_json(self):
        filepath = filedialog.askopenfilename(
            title="Выберите JSON-файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
            return
        if not isinstance(data, list):
            messagebox.showerror("Ошибка", "JSON должен содержать список объектов.")
            return
        self.user_tvm.clear()
        for item in self.tree_tvm_user.get_children():
            self.tree_tvm_user.delete(item)
        for idx, item in enumerate(data):
            if not isinstance(item, dict) or 'name' not in item or 'characteristics' not in item:
                messagebox.showwarning("Предупреждение",
                                       f"Элемент {idx} пропущен: отсутствуют 'name' или 'characteristics'.")
                continue
            try:
                tvm = TicketVendingMachine.from_dict(item)
                tvm.calculate_technical_level()
                self.user_tvm.append(tvm)
                self.tree_tvm_user.insert('', 'end', values=(tvm.name, f"{tvm.technical_level:.4f}"))
            except Exception as e:
                messagebox.showwarning("Предупреждение",
                                       f"Не удалось создать автомат из элемента {idx}:\n{e}")
        if self.user_tvm:
            self.btn_plot_tvm_user.config(state='normal')
            messagebox.showinfo("Готово", f"Загружено автоматов: {len(self.user_tvm)}")
        else:
            self.btn_plot_tvm_user.config(state='disabled')
            messagebox.showwarning("Внимание", "Не удалось загрузить ни одного автомата.")

    def plot_tvm_user_diagrams(self):
        if not self.user_tvm:
            messagebox.showwarning("Нет данных", "Сначала загрузите корректный JSON-файл.")
            return
        all_for_bar = [self.base_tvm] + self.user_tvm
        create_bar_chart_relative(all_for_bar, self.base_tvm,
                                  title="Сравнение технического уровня (пользовательские автоматы)")
        base_unified = unify_to_tvm_characteristics(self.base_tvm, exclude_binary=True)
        unified_data = [(m.name, unify_to_tvm_characteristics(m, exclude_binary=True)) for m in self.user_tvm]
        create_radial_relative(unified_data, base_unified,
                               inverse_keys=["Скорость транзакции (сек)", "Энергопотребление (кВт·ч)"],
                               title="Сравнение характеристик загруженных автоматов (без учёта бинарных признаков)")

    def setup_forecast_tab(self):
        # Обучаем все модели сразу при открытии вкладки
        self.forecast_model = PassengerForecast("Metro.csv")
        self.forecast_model.train_models()  # теперь этот метод выводит формулы и R²

        # Заголовок
        title = ttk.Label(self.frame_forecast, text="Прогноз пассажиропотока метро",
                        font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # Блок с результатами обучения
        info_frame = ttk.LabelFrame(self.frame_forecast, text="Результаты обучения моделей")
        info_frame.pack(fill='x', padx=10, pady=10)

        # Текстовое поле для вывода R² и формул
        self.info_text = tk.Text(info_frame, height=10, width=80, state='disabled')
        self.info_text.pack(padx=5, pady=5)

        # Вывод результатов обучения в текстовое поле
        self.update_info_text()

        # Выбор степени модели
        degree_frame = ttk.Frame(self.frame_forecast)
        degree_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(degree_frame, text="Выберите степень модели:").pack(side='left')
        self.degree_var = tk.IntVar(value=1)
        degree_combo = ttk.Combobox(degree_frame, textvariable=self.degree_var,
                                    values=[1, 2, 3], state='readonly', width=5)
        degree_combo.pack(side='left', padx=5)

        # Блок ввода признаков
        input_frame = ttk.LabelFrame(self.frame_forecast, text="Введите признаки")
        input_frame.pack(fill='x', padx=10, pady=10)

        # Температура
        ttk.Label(input_frame, text="Температура (°C)").grid(row=0, column=0, padx=5, pady=5)
        self.temp_entry = ttk.Entry(input_frame)
        self.temp_entry.grid(row=0, column=1, padx=5, pady=5)

        # Будний день
        ttk.Label(input_frame, text="Будний день (0/1)").grid(row=1, column=0, padx=5, pady=5)
        self.weekday_entry = ttk.Entry(input_frame)
        self.weekday_entry.grid(row=1, column=1, padx=5, pady=5)

        # Массовое мероприятие
        ttk.Label(input_frame, text="Массовое мероприятие (0/1)").grid(row=2, column=0, padx=5, pady=5)
        self.event_entry = ttk.Entry(input_frame)
        self.event_entry.grid(row=2, column=1, padx=5, pady=5)

        # Частота поездов
        ttk.Label(input_frame, text="Частота поездов").grid(row=3, column=0, padx=5, pady=5)
        self.frequency_entry = ttk.Entry(input_frame)
        self.frequency_entry.grid(row=3, column=1, padx=5, pady=5)

        # Цена билета
        ttk.Label(input_frame, text="Цена билета").grid(row=4, column=0, padx=5, pady=5)
        self.price_entry = ttk.Entry(input_frame)
        self.price_entry.grid(row=4, column=1, padx=5, pady=5)

        # Кнопка прогноза
        btn_predict = ttk.Button(self.frame_forecast, text="Получить прогноз",
                                command=self.make_forecast)
        btn_predict.pack(pady=10)

        # Результат прогноза
        self.result_label = ttk.Label(self.frame_forecast, text="", font=("Arial", 12, "bold"))
        self.result_label.pack(pady=5)

        # Блок построения графика зависимости
        graph_frame = ttk.LabelFrame(self.frame_forecast, text="Построение зависимости")
        graph_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(graph_frame, text="Выберите изменяемый признак").grid(row=0, column=0, padx=5, pady=5)
        self.feature_combo = ttk.Combobox(graph_frame,
                                        values=['avg_temp_c', 'is_weekday', 'special_event',
                                                'train_frequency', 'ticket_price'],
                                        state='readonly')
        self.feature_combo.grid(row=0, column=1, padx=5, pady=5)
        self.feature_combo.current(0)

        # Начало интервала
        ttk.Label(graph_frame, text="Начало интервала").grid(row=1, column=0, padx=5, pady=5)
        self.range_start_entry = ttk.Entry(graph_frame)
        self.range_start_entry.grid(row=1, column=1, padx=5, pady=5)

        # Конец интервала
        ttk.Label(graph_frame, text="Конец интервала").grid(row=2, column=0, padx=5, pady=5)
        self.range_end_entry = ttk.Entry(graph_frame)
        self.range_end_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка графика
        btn_plot = ttk.Button(graph_frame, text="Построить график",
                            command=self.plot_dependency)
        btn_plot.grid(row=3, column=0, columnspan=2, pady=10)


    def update_info_text(self):
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        info = "Сравнение моделей:\n"
        for deg in [1, 2, 3]:
            _, r2, formula = self.forecast_model.models[deg]
            info += f"Степень {deg}: //R² = {r2:.4f}\n"
            info += f"Формула: {formula}\n\n"
        self.info_text.insert(tk.END, info)
        self.info_text.config(state='disabled')


    def make_forecast(self):
        try:
            degree = self.degree_var.get()  # 1, 2 или 3
            prediction = self.forecast_model.predict(
                degree,
                float(self.temp_entry.get()),
                int(self.weekday_entry.get()),
                int(self.event_entry.get()),
                float(self.frequency_entry.get()),
                float(self.price_entry.get())
            )
            self.result_label.config(text=f"Прогноз числа пассажиров: {prediction:.2f} тыс. чел.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный ввод данных:\n{e}")


    def plot_dependency(self):
        """Построение графика зависимости для выбранного признака и степени."""
        try:
            feature_name = self.feature_combo.get()
            start = float(self.range_start_entry.get())
            end = float(self.range_end_entry.get())
            degree = self.degree_var.get()

            # Фиксированные значения (берутся из полей ввода как базовые, кроме варьируемого)
            fixed_data = {
                'avg_temp_c': float(self.temp_entry.get()),
                'is_weekday': int(self.weekday_entry.get()),
                'special_event': int(self.event_entry.get()),
                'train_frequency': float(self.frequency_entry.get()),
                'ticket_price': float(self.price_entry.get())
            }

            x_vals = np.linspace(start, end, 50)
            predictions = []

            # Получаем модель по степени
            model_data = self.forecast_model.models[degree]
            if degree == 1:
                model = model_data[0]  # LinearRegression
                for val in x_vals:
                    data = fixed_data.copy()
                    data[feature_name] = val
                    X_test = np.array([list(data.values())])
                    pred = model.predict(X_test)[0]
                    predictions.append(pred)
            else:
                model = model_data[0]  # Pipeline
                for val in x_vals:
                    data = fixed_data.copy()
                    data[feature_name] = val
                    X_test = np.array([list(data.values())])
                    pred = model.predict(X_test)[0]
                    predictions.append(pred)

            # Построение графика
            plt.figure(figsize=(10, 6))
            plt.plot(x_vals, predictions, linewidth=2)
            plt.xlabel(feature_name)
            plt.ylabel("Прогноз пассажиропотока")
            plt.title(f"Зависимость от {feature_name} (степень {degree})")
            plt.grid(True)
            plt.show()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график:\n{e}")

# ========== Запуск ==========
def main():
    root = tk.Tk()
    app = TransportComparisonApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()