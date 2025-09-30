"""
Главный модуль приложения для кодирования Хаффмана.
Содержит графический интерфейс для работы с алгоритмом Хаффмана.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Optional, Tuple, Any

# Импорты из наших модулей
try:
    from huffman import (
        HuffmanNode, build_huffman_tree, generate_huffman_codes,
        calculate_average_length, calculate_entropy, calculate_redundancy,
        check_kraft_inequality, encode_string, decode_string
    )
    from file_operations import read_sequence_from_file, write_to_file
    from variant5_data import VARIANT5_SYMBOLS, VARIANT5_P1, VARIANT5_P2, validate_variant5_data
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что все файлы находятся в одной папке:")
    print("- huffman.py")
    print("- file_operations.py")
    print("- variant5_data.py")
    raise


class HuffmanApp:
    """Основной класс приложения с графическим интерфейсом."""

    def __init__(self, root: tk.Tk) -> None:
        """Инициализирует приложение с графическим интерфейсом."""
        self.root = root
        self.root.title("Основные методы побуквенного кодирования - Вариант 5")
        self.root.geometry("950x750")
        self.root.minsize(900, 700)

        # Проверяем данные варианта
        try:
            validate_variant5_data()
            print("Данные варианта 5 проверены успешно")
        except AssertionError as e:
            messagebox.showerror("Ошибка данных", f"Ошибка в данных варианта 5: {e}")

        # Переменные для хранения данных
        self.symbols = VARIANT5_SYMBOLS.copy()
        self.probs_p1 = VARIANT5_P1.copy()
        self.probs_p2 = VARIANT5_P2.copy()
        self.current_codes: Dict[str, str] = {}
        self.current_tree_root: Optional[HuffmanNode] = None

        self.create_widgets()
        self.update_input_fields()

    def update_input_fields(self) -> None:
        """Заполняет поля ввода данными варианта 5."""
        self.symbols_entry.delete(0, tk.END)
        self.symbols_entry.insert(0, ", ".join(self.symbols))

        self.probs_p1_entry.delete(0, tk.END)
        self.probs_p1_entry.insert(0, ", ".join(f"{p:.6f}" for p in self.probs_p1))

        self.probs_p2_entry.delete(0, tk.END)
        self.probs_p2_entry.insert(0, ", ".join(f"{p:.6f}" for p in self.probs_p2))

    def create_widgets(self) -> None:
        """Создает и размещает все элементы интерфейса."""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="Лабораторная работа №2: Основные методы побуквенного кодирования - Вариант 5",
            font=('Helvetica', 14, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Фрейм для ввода алфавита и вероятностей
        input_frame = ttk.LabelFrame(main_frame, text="Ввод алфавита и вероятностей", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        # Метки и поля для алфавита
        ttk.Label(input_frame, text="Алфавит (через запятую):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.symbols_entry = ttk.Entry(input_frame, width=60)
        self.symbols_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        # Метки и поля для вероятностей P1
        ttk.Label(input_frame, text="Вероятности P1 (через запятую):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.probs_p1_entry = ttk.Entry(input_frame, width=60)
        self.probs_p1_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        # Метки и поля для вероятностей P2
        ttk.Label(input_frame, text="Вероятности P2 (через запятую):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.probs_p2_entry = ttk.Entry(input_frame, width=60)
        self.probs_p2_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        # Кнопки для работы с данными
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="Рассчитать код Хаффмана", command=self.calculate_codes).pack(side=tk.LEFT, padx=(0, 10))

        # Фрейм для выбора распределения
        dist_frame = ttk.LabelFrame(main_frame, text="Выбор распределения для кодирования", padding="10")
        dist_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.dist_var = tk.StringVar(value="P1")
        ttk.Radiobutton(dist_frame, text="Равномерное", variable=self.dist_var, value="uniform").grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Radiobutton(dist_frame, text="P1", variable=self.dist_var, value="P1").grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Radiobutton(dist_frame, text="P2", variable=self.dist_var, value="P2").grid(row=0, column=2, sticky=tk.W)

        # Фрейм для вывода кодовых слов и характеристик
        results_frame = ttk.LabelFrame(main_frame, text="Результаты кодирования", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)

        # Таблица для вывода кодовых слов
        columns = ("Символ", "Вероятность", "Кодовое слово", "Длина")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=8)

        # Настраиваем колонки
        self.tree.heading("Символ", text="Символ")
        self.tree.heading("Вероятность", text="Вероятность")
        self.tree.heading("Кодовое слово", text="Кодовое слово")
        self.tree.heading("Длина", text="Длина")

        self.tree.column("Символ", width=80, anchor=tk.CENTER)
        self.tree.column("Вероятность", width=100, anchor=tk.CENTER)
        self.tree.column("Кодовое слово", width=120, anchor=tk.CENTER)
        self.tree.column("Длина", width=80, anchor=tk.CENTER)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Полоса прокрутки для таблицы
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Настройка весов для растягивания таблицы
        results_frame.rowconfigure(0, weight=1)
        results_frame.columnconfigure(0, weight=1)

        # Фрейм для характеристик кода
        stats_frame = ttk.Frame(results_frame)
        stats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.avg_len_label = ttk.Label(stats_frame, text="Средняя длина: --")
        self.avg_len_label.grid(row=0, column=0, sticky=tk.W)

        self.entropy_label = ttk.Label(stats_frame, text="Энтропия: --")
        self.entropy_label.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))

        self.redundancy_label = ttk.Label(stats_frame, text="Избыточность: --")
        self.redundancy_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        self.kraft_label = ttk.Label(stats_frame, text="Неравенство Крафта: --")
        self.kraft_label.grid(row=1, column=1, sticky=tk.W, padx=(20, 0), pady=(5, 0))

        # Фрейм для операций с файлами
        file_frame = ttk.LabelFrame(main_frame, text="Работа с файлами", padding="10")
        file_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # Выбор режима работы
        ttk.Label(file_frame, text="Режим:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.mode_var = tk.StringVar(value="encode")
        mode_combo = ttk.Combobox(file_frame, textvariable=self.mode_var, values=("encode", "decode"), state="readonly", width=15)
        mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))

        # Входной файл
        ttk.Label(file_frame, text="Входной файл:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.input_file_entry = ttk.Entry(file_frame)
        self.input_file_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Button(file_frame, text="Обзор", command=self.browse_input_file, width=10).grid(row=1, column=2, padx=(5, 0))

        # Выходной файл
        ttk.Label(file_frame, text="Выходной файл:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.output_file_entry = ttk.Entry(file_frame)
        self.output_file_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Button(file_frame, text="Обзор", command=self.browse_output_file, width=10).grid(row=2, column=2, padx=(5, 0))

        # Кнопка выполнения операции
        ttk.Button(file_frame, text="Выполнить операцию", command=self.execute_operation).grid(row=3, column=0, columnspan=3, pady=10)

        # Область для вывода сообщений
        msg_frame = ttk.LabelFrame(main_frame, text="Сообщения и логи", padding="10")
        msg_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        msg_frame.columnconfigure(0, weight=1)
        msg_frame.rowconfigure(0, weight=1)

        self.message_text = tk.Text(msg_frame, height=8, width=80, wrap=tk.WORD)
        self.message_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Полоса прокрутки для области сообщений
        scrollbar_msg = ttk.Scrollbar(msg_frame, orient=tk.VERTICAL, command=self.message_text.yview)
        self.message_text.configure(yscroll=scrollbar_msg.set)
        scrollbar_msg.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Настройка весов для основного фрейма
        main_frame.rowconfigure(5, weight=1)
        msg_frame.rowconfigure(0, weight=1)
        msg_frame.columnconfigure(0, weight=1)

    def log_message(self, message: str) -> None:
        """Добавляет сообщение в текстовую область."""
        self.message_text.insert(tk.END, message + "\n")
        self.message_text.see(tk.END)
        self.root.update()

    def clear_messages(self) -> None:
        """Очищает текстовую область сообщений."""
        self.message_text.delete(1.0, tk.END)

    def browse_input_file(self) -> None:
        """Открывает диалог выбора входного файла."""
        try:
            filename = filedialog.askopenfilename(
                title="Выберите входной файл",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.input_file_entry.delete(0, tk.END)
                self.input_file_entry.insert(0, filename)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при выборе файла: {e}")

    def browse_output_file(self) -> None:
        """Открывает диалог выбора выходного файла."""
        try:
            filename = filedialog.asksaveasfilename(
                title="Выберите выходной файл",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.output_file_entry.delete(0, tk.END)
                self.output_file_entry.insert(0, filename)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при выборе файла: {e}")

    def parse_inputs(self) -> bool:
        """Парсит введенные алфавит и вероятности."""
        try:
            symbols_str = self.symbols_entry.get().strip()
            probs_p1_str = self.probs_p1_entry.get().strip()
            probs_p2_str = self.probs_p2_entry.get().strip()

            if not symbols_str or not probs_p1_str or not probs_p2_str:
                raise ValueError("Все поля должны быть заполнены")

            self.symbols = [s.strip() for s in symbols_str.split(',') if s.strip()]
            self.probs_p1 = [float(p.strip()) for p in probs_p1_str.split(',') if p.strip()]
            self.probs_p2 = [float(p.strip()) for p in probs_p2_str.split(',') if p.strip()]

            if len(self.symbols) != len(self.probs_p1) or len(self.symbols) != len(self.probs_p2):
                raise ValueError("Количество символов и вероятностей должно совпадать")

            if len(self.symbols) == 0:
                raise ValueError("Алфавит не может быть пустым")

            # Нормализация вероятностей
            sum_p1 = sum(self.probs_p1)
            sum_p2 = sum(self.probs_p2)

            if abs(sum_p1 - 1.0) > 1e-6:
                self.log_message(f"Сумма P1 ({sum_p1:.6f}) нормализована до 1.0")
                self.probs_p1 = [p / sum_p1 for p in self.probs_p1]

            if abs(sum_p2 - 1.0) > 1e-6:
                self.log_message(f"Сумма P2 ({sum_p2:.6f}) нормализована до 1.0")
                self.probs_p2 = [p / sum_p2 for p in self.probs_p2]

            return True

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Ошибка при разборе данных: {str(e)}")
            return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неожиданная ошибка: {str(e)}")
            return False

    def calculate_codes(self) -> None:
        """Рассчитывает коды Хаффмана для выбранного распределения."""
        self.clear_messages()

        if not self.parse_inputs():
            return

        dist = self.dist_var.get()

        try:
            probs: List[float]
            if dist == "uniform":
                n = len(self.symbols)
                probs = [1.0 / n] * n
            elif dist == "P1":
                probs = self.probs_p1
            else:
                probs = self.probs_p2

            self.log_message(f"Расчет кодов для распределения {dist}...")

            self.current_tree_root = build_huffman_tree(self.symbols, probs)
            self.current_codes = generate_huffman_codes(self.current_tree_root)

            # Очистка таблицы
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Заполнение таблицы
            for i, symbol in enumerate(self.symbols):
                code = self.current_codes.get(symbol, "")
                self.tree.insert("", tk.END, values=(symbol, f"{probs[i]:.6f}", code, len(code)))

            # Расчет характеристик
            avg_len = calculate_average_length(self.current_codes, self.symbols, probs)
            entropy = calculate_entropy(probs)
            redundancy = calculate_redundancy(avg_len, entropy)
            kraft_ok, kraft_sum = check_kraft_inequality(self.current_codes)

            # Обновление меток
            self.avg_len_label.config(text=f"Средняя длина: {avg_len:.4f}")
            self.entropy_label.config(text=f"Энтропия: {entropy:.4f}")
            self.redundancy_label.config(text=f"Избыточность: {redundancy:.4f}")
            kraft_status = "Выполняется" if kraft_ok else "Не выполняется"
            self.kraft_label.config(text=f"Неравенство Крафта: {kraft_status} (Σ={kraft_sum:.4f})")

            self.log_message(f"Коды рассчитаны успешно!")
            self.log_message(f"Средняя длина: {avg_len:.4f} бит")
            self.log_message(f"Энтропия: {entropy:.4f} бит")
            self.log_message(f"Избыточность: {redundancy:.4f} бит")
            self.log_message(f"Неравенство Крафта: {kraft_status}")

        except Exception as e:
            error_msg = f"Ошибка при расчете кодов: {str(e)}"
            messagebox.showerror("Ошибка расчета", error_msg)
            self.log_message(f"{error_msg}")

    def execute_operation(self) -> None:
        """Выполняет операцию кодирования или декодирования."""
        self.clear_messages()

        mode = self.mode_var.get()
        input_file = self.input_file_entry.get().strip()
        output_file = self.output_file_entry.get().strip()

        if not input_file or not output_file:
            messagebox.showerror("Ошибка", "Укажите входной и выходной файлы")
            return

        try:
            if mode == "encode":
                self.encode_operation(input_file, output_file)
            else:
                self.decode_operation(input_file, output_file)

        except Exception as e:
            error_msg = f"Ошибка при выполнении операции: {str(e)}"
            messagebox.showerror("Ошибка операции", error_msg)
            self.log_message(f"{error_msg}")

    def encode_operation(self, input_file: str, output_file: str) -> None:
        """Выполняет операцию кодирования."""
        if not self.current_codes:
            messagebox.showerror("Ошибка", "Сначала рассчитайте коды Хаффмана")
            return

        try:
            self.log_message("Начало кодирования...")

            input_string = read_sequence_from_file(input_file)
            if not input_string:
                raise ValueError("Входной файл пуст")

            self.log_message(f"Исходный текст: {input_string}")

            encoded_string = encode_string(input_string, self.current_codes)
            write_to_file(output_file, encoded_string)

            original_bits = len(input_string) * 8
            compressed_bits = len(encoded_string)
            compression_ratio = original_bits / compressed_bits if compressed_bits > 0 else 0

            self.log_message("Кодирование завершено!")
            self.log_message(f"Закодированный текст: {encoded_string}")
            self.log_message(f"Исходный размер: {original_bits} бит")
            self.log_message(f"Закодированный размер: {compressed_bits} бит")
            self.log_message(f"Степень сжатия: {compression_ratio:.2f}:1")
            self.log_message(f"Файл сохранен: {output_file}")

        except Exception as e:
            raise e

    def decode_operation(self, input_file: str, output_file: str) -> None:
        """Выполняет операцию декодирования."""
        try:
            self.log_message("Начало декодирования...")

            if not self.current_tree_root:
                messagebox.showerror("Ошибка", "Сначала рассчитайте коды Хаффмана")
                return

            encoded_string = read_sequence_from_file(input_file)

            if not encoded_string:
                raise ValueError("Закодированный файл пуст")

            self.log_message(f"Закодированный текст: {encoded_string}")

            decoded_string = decode_string(encoded_string, self.current_tree_root)
            write_to_file(output_file, decoded_string)

            self.log_message("Декодирование завершено!")
            self.log_message(f"Раскодированный текст: {decoded_string}")
            self.log_message(f"Файл сохранен: {output_file}")

        except Exception as e:
            raise e


def main() -> None:
    """Основная функция запуска приложения."""
    try:
        print("Запуск приложения кодирования Хаффмана...")
        root = tk.Tk()
        app = HuffmanApp(root)

        # Центрирование окна
        root.update_idletasks()
        x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
        y = (root.winfo_screenheight() - root.winfo_reqheight()) // 2
        root.geometry(f"+{x}+{y}")

        print("Приложение успешно запущено")
        root.mainloop()

    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        messagebox.showerror("Критическая ошибка",
                             f"Не удалось запустить приложение:\n{str(e)}\n\n"
                             f"Убедитесь, что все файлы находятся в одной папке.")


if __name__ == "__main__":
    main()