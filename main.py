
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import matplotlib.pyplot as plt
import numpy as np

# Импорт классов поездов (предполагается, что файлы находятся в той же директории)
from Numberseries import Numberseries
from Rusich import Rusich
from Oka import Oka
from Moskva import Moskva
from Moskva_2020 import Moskva_2020

# ========== Вспомогательные функции (из оригинального кода) ==========

def unify_to_numberseries_characteristics(train):
    """
    Приводит характеристики объекта к набору характеристик Numberseries.
    """
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

def normalize_relative_to_base(chars, base_chars):
    """
    Нормирует характеристики делением на значения базового образца.
    """
    normalized = {}
    for key in chars:
        value = chars[key]
        base_val = base_chars[key]
        if base_val == 0:
            normalized[key] = 1.0
        else:
            if key in ("Уровень шума (дБ)", "Энергопотребление (кВт·ч/км)"):
                normalized[key] = base_val / value if value != 0 else 1.0
            else:
                normalized[key] = value / base_val
    return normalized

def create_radial_relative(trains_data, base_name, base_chars, title="Сравнение характеристик"):
    """
    Строит радиальную диаграмму для нескольких объектов.
    trains_data: список кортежей (имя_объекта, унифицированные_характеристики)
    """
    if not trains_data:
        print("Нет данных для радиальной диаграммы.")
        return

    char_names = list(base_chars.keys())
    angles = np.linspace(0, 2 * np.pi, len(char_names), endpoint=False).tolist()
    angles += angles[:1]  # замыкаем круг

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))

    for name, chars in trains_data:
        rel = normalize_relative_to_base(chars, base_chars)
        values = [rel[char] for char in char_names]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=name)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(char_names, fontsize=10)
    ax.set_ylim(0, max([max(normalize_relative_to_base(chars, base_chars).values())
                         for _, chars in trains_data]) + 0.1)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
    ax.set_title(title, pad=20)
    plt.tight_layout()
    plt.show()

def create_bar_chart_relative(trains, base_train):
    """
    Столбчатая диаграмма технического уровня относительно базового образца.
    """
    base_level = base_train.technical_level
    names = [f"{t.name}\n({t.__class__.__name__})" for t in trains]
    rel_levels = [t.technical_level / base_level for t in trains]

    # Сортировка по убыванию
    sorted_pairs = sorted(zip(rel_levels, names), reverse=True)
    rel_levels, names = zip(*sorted_pairs)

    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, rel_levels, color='skyblue')
    for bar, val in zip(bars, rel_levels):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f"{val:.2f}", ha='center', va='bottom')

    plt.xlabel("Образец")
    plt.ylabel("Относительный технический уровень (база = 1)")
    plt.title("Сравнение технического уровня образцов (Numberseries = 1)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# ========== Инициализация предустановленных поездов ==========

def create_default_trains():
    """Создаёт базовый поезд и список всех предустановленных поездов."""
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

# ========== Класс приложения ==========

class TrainComparisonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сравнение поездов")
        self.root.geometry("700x500")

        # Предустановленные данные
        self.base_train, self.default_trains = create_default_trains()

        # Данные, загруженные пользователем
        self.user_trains = []

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Создаём Notebook (вкладки)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Первая вкладка – предустановленные поезда
        self.frame_default = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_default, text="Предустановленные поезда")
        self.setup_default_tab()

        # Вторая вкладка – загрузка JSON
        self.frame_user = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_user, text="Загрузить свои данные")
        self.setup_user_tab()

    def setup_default_tab(self):
        """Интерфейс первой вкладки: таблица с поездами и кнопка построения диаграмм."""
        # Таблица (Treeview) с двумя колонками
        columns = ('name', 'level')
        self.tree_default = ttk.Treeview(self.frame_default, columns=columns, show='headings', height=8)
        self.tree_default.heading('name', text='Название поезда')
        self.tree_default.heading('level', text='Технический уровень')
        self.tree_default.column('name', width=400)
        self.tree_default.column('level', width=150, anchor='center')
        self.tree_default.pack(pady=10, padx=10, fill='both', expand=True)

        # Заполнение таблицы
        self.update_default_table()

        # Кнопка построения диаграмм
        btn_plot = ttk.Button(self.frame_default, text="Построить диаграммы",
                              command=self.plot_default_diagrams)
        btn_plot.pack(pady=10)

    def update_default_table(self):
        """Очищает и заполняет таблицу предустановленных поездов."""
        for item in self.tree_default.get_children():
            self.tree_default.delete(item)
        for train in self.default_trains:
            self.tree_default.insert('', 'end', values=(train.name, f"{train.technical_level:.4f}"))

    def plot_default_diagrams(self):
        """Строит диаграммы для предустановленных поездов."""
        # Столбчатая диаграмма
        create_bar_chart_relative(self.default_trains, self.base_train)

        # Радиальная диаграмма
        base_unified = unify_to_numberseries_characteristics(self.base_train)
        unified_data = [(t.name, unify_to_numberseries_characteristics(t)) for t in self.default_trains]
        create_radial_relative(unified_data, self.base_train.name, base_unified,
                               title="Сравнение характеристик (относительно базового образца)")

    def setup_user_tab(self):
        """Интерфейс второй вкладки: загрузка JSON, просмотр данных, построение диаграмм."""
        # Инструкция
        lbl_info = ttk.Label(self.frame_user,
                             text="Загрузите JSON-файл с данными поездов.\n"
                                  "Формат: список объектов с полями 'name' и 'characteristics'.\n"
                                  "Характеристики: Максимальная скорость (км/ч), Сидячие места (шт),\n"
                                  "Энергопотребление (кВт·ч/км), Уровень шума (дБ), Срок службы (лет).")
        lbl_info.pack(pady=10)

        # Кнопка загрузки файла
        btn_load = ttk.Button(self.frame_user, text="Загрузить JSON", command=self.load_json)
        btn_load.pack(pady=5)

        # Таблица для отображения загруженных поездов
        columns = ('name', 'level')
        self.tree_user = ttk.Treeview(self.frame_user, columns=columns, show='headings', height=6)
        self.tree_user.heading('name', text='Название поезда')
        self.tree_user.heading('level', text='Технический уровень')
        self.tree_user.column('name', width=400)
        self.tree_user.column('level', width=150, anchor='center')
        self.tree_user.pack(pady=10, padx=10, fill='both', expand=True)

        # Кнопка построения диаграмм по загруженным данным
        self.btn_plot_user = ttk.Button(self.frame_user, text="Построить диаграммы по загруженным данным",
                                        command=self.plot_user_diagrams, state='disabled')
        self.btn_plot_user.pack(pady=10)

    def load_json(self):
        """Загружает JSON-файл и создаёт объекты Numberseries."""
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

        # Проверка структуры данных: должен быть список
        if not isinstance(data, list):
            messagebox.showerror("Ошибка", "JSON должен содержать список объектов.")
            return

        # Очищаем предыдущие загруженные данные
        self.user_trains.clear()
        for item in self.tree_user.get_children():
            self.tree_user.delete(item)

        # Обрабатываем каждый элемент
        for idx, item in enumerate(data):
            if not isinstance(item, dict) or 'name' not in item or 'characteristics' not in item:
                messagebox.showwarning("Предупреждение",
                                       f"Элемент {idx} пропущен: отсутствуют 'name' или 'characteristics'.")
                continue
            try:
                train = Numberseries.from_dict(item)
                train.calculate_technical_level()
                self.user_trains.append(train)
                self.tree_user.insert('', 'end', values=(train.name, f"{train.technical_level:.4f}"))
            except Exception as e:
                messagebox.showwarning("Предупреждение",
                                       f"Не удалось создать поезд из элемента {idx}:\n{e}")

        if self.user_trains:
            self.btn_plot_user.config(state='normal')
            messagebox.showinfo("Готово", f"Загружено поездов: {len(self.user_trains)}")
        else:
            self.btn_plot_user.config(state='disabled')
            messagebox.showwarning("Внимание", "Не удалось загрузить ни одного поезда.")

    def plot_user_diagrams(self):
        """Строит диаграммы для загруженных пользователем поездов (сравнение с базовым Numberseries)."""
        if not self.user_trains:
            messagebox.showwarning("Нет данных", "Сначала загрузите корректный JSON-файл.")
            return

        # Для сравнения используем тот же базовый поезд (Numberseries)
        # Если среди загруженных есть поезд с именем, совпадающим с базовым, его не дублируем
        # Но для диаграмм используем только пользовательские поезда + базовый как эталон
        all_for_bar = [self.base_train] + self.user_trains
        create_bar_chart_relative(all_for_bar, self.base_train)

        base_unified = unify_to_numberseries_characteristics(self.base_train)
        unified_data = [(t.name, unify_to_numberseries_characteristics(t)) for t in self.user_trains]
        create_radial_relative(unified_data, self.base_train.name, base_unified,
                               title="Сравнение характеристик загруженных поездов (база = Numberseries)")

# ========== Запуск приложения ==========

def main():
    root = tk.Tk()
    app = TrainComparisonApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
