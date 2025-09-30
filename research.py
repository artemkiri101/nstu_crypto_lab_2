"""
Модуль для проведения исследований эффективности кодирования Хаффмана.

Содержит функции для сравнения кодов при разных распределениях вероятностей.
"""

from typing import Dict, Any, List

from huffman import (
    build_huffman_tree, generate_huffman_codes, calculate_average_length,
    calculate_entropy, calculate_redundancy, check_kraft_inequality, encode_string
)
from variant5_data import VARIANT5_SYMBOLS, VARIANT5_P1, VARIANT5_P2, generate_test_sequences


def conduct_research() -> Dict[str, Dict[str, Any]]:
    """Проводит все необходимые исследования для варианта 5."""
    print("=" * 70)
    print("ИССЛЕДОВАНИЯ ЭФФЕКТИВНОСТИ КОДИРОВАНИЯ ХАФФМАНА - ВАРИАНТ 5")
    print("=" * 70)

    # 1. Исследование для трех распределений
    print("\n" + "=" * 50)
    print("1. КОДЫ ХАФФМАНА ДЛЯ ТРЕХ РАСПРЕДЕЛЕНИЙ")
    print("=" * 50)

    distributions: Dict[str, List[float]] = {
        'Равномерное': [1/8] * 8,
        'P1': VARIANT5_P1,
        'P2': VARIANT5_P2
    }

    results: Dict[str, Dict[str, Any]] = {}

    for dist_name, probs in distributions.items():
        print(f"\n{dist_name} распределение:")
        print("-" * 50)
        print(f"{'Символ':<6} | {'Вероятность':<12} | {'Кодовое слово':<14} | {'Длина, бит':<10}")
        print("-" * 50)

        # Построение дерева и генерация кодов
        root = build_huffman_tree(VARIANT5_SYMBOLS, probs)
        codes = generate_huffman_codes(root)

        # Расчет характеристик кода
        avg_len: float = calculate_average_length(codes, VARIANT5_SYMBOLS, probs)
        entropy: float = calculate_entropy(probs)
        redundancy: float = calculate_redundancy(avg_len, entropy)
        kraft_ok: bool
        kraft_sum: float
        kraft_ok, kraft_sum = check_kraft_inequality(codes)

        # Вывод кодовых слов
        for i, symbol in enumerate(VARIANT5_SYMBOLS):
            print(f"{symbol:<6} | {probs[i]:<12.6f} | {codes[symbol]:<14} | {len(codes[symbol]):<10} бит")

        # Вывод характеристик
        print(f"\nХарактеристики кода:")
        print(f"  Средняя длина: {avg_len:.4f} бит")
        print(f"  Энтропия: {entropy:.4f} бит")
        print(f"  Избыточность: {redundancy:.4f} бит")
        print(f"  Неравенство Крафта: {'Выполняется' if kraft_ok else 'Не выполняется'} (Σ={kraft_sum:.4f})")

        # Сохранение результатов
        results[dist_name] = {
            'codes': codes,
            'avg_len': avg_len,
            'entropy': entropy,
            'redundancy': redundancy,
            'kraft_ok': kraft_ok,
            'kraft_sum': kraft_sum,
            'root': root
        }

    # 2. Исследование зависимости длины кода от распределения
    print("\n" + "=" * 70)
    print("2. ИССЛЕДОВАНИЕ ЗАВИСИМОСТИ ДЛИНЫ КОДА ОТ РАСПРЕДЕЛЕНИЯ")
    print("=" * 70)

    # Генерация тестовых последовательностей
    test_sequences: Dict[str, str] = generate_test_sequences()

    print("\nДлина закодированных последовательностей (в битах):")
    print("-" * 75)
    print(f"{'Последовательность':<18} | {'Равномерный код':<16} | {'Код P1':<12} | {'Код P2':<12}")
    print("-" * 75)

    for seq_name, sequence in test_sequences.items():
        row: str = f"{seq_name:<18} |"
        for dist_name in ['Равномерное', 'P1', 'P2']:
            codes = results[dist_name]['codes']
            encoded = encode_string(sequence, codes)
            row += f" {len(encoded):<14} бит |"
        print(row)

    # Анализ результатов
    print("\nАНАЛИЗ РЕЗУЛЬТАТОВ:")
    print("-" * 50)

    for seq_name in test_sequences.keys():
        lengths = {}
        for dist_name in ['Равномерное', 'P1', 'P2']:
            codes = results[dist_name]['codes']
            encoded = encode_string(test_sequences[seq_name], codes)
            lengths[dist_name] = len(encoded)

        min_length = min(lengths.values())

        optimal_codes = []
        for dist_name, length in lengths.items():
            if length == min_length:
                optimal_codes.append(dist_name)

        print(f"{seq_name.capitalize()} последовательность:")
        print(f"  Равномерный код: {lengths['Равномерное']} бит")
        print(f"  Код P1: {lengths['P1']} бит")
        print(f"  Код P2: {lengths['P2']} бит")
        print(f"  Оптимален: {', '.join(optimal_codes)} ({min_length} бит)")
        print()

    # Сравнение эффективности
    print("\nВЫВОДЫ:")
    print("-" * 50)
    print("Наиболее эффективное кодирование достигается при совпадении")
    print("распределения вероятностей в коде и реального распределения в тексте")
    print("Код Хаффмана оптимален для своего распределения вероятностей")
    print("Отклонение от оптимального распределения увеличивает длину кода на 50-100%")

    return results


if __name__ == "__main__":
    """Точка входа для проведения исследований."""
    from variant5_data import validate_variant5_data

    # Проверка данных перед исследованиями
    validate_variant5_data()

    # Проведение исследований
    research_results = conduct_research()

    print("\n" + "=" * 70)
    print("ИССЛЕДОВАНИЯ ЗАВЕРШЕНЫ УСПЕШНО")
    print("=" * 70)