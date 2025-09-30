"""
Модуль реализации алгоритма Хаффмана для побуквенного кодирования.

Содержит классы и функции для построения дерева Хаффмана, генерации кодовых слов,
кодирования/декодирования строк и расчета характеристик кода.
"""

import math
from typing import Dict, List, Tuple, Optional


class HuffmanNode:
    """Узел дерева Хаффмана.

    Attributes:
        symbol (Optional[str]): Символ алфавита (None для внутренних узлов)
        prob (float): Вероятность символа или сумма вероятностей потомков
        left (Optional[HuffmanNode]): Левый потомок
        right (Optional[HuffmanNode]): Правый потомок
    """

    def __init__(self, symbol: Optional[str], prob: float) -> None:
        """Инициализирует узел дерева Хаффмана.

        Args:
            symbol: Символ алфавита или None для внутренних узлов
            prob: Вероятность символа или сумма вероятностей потомков
        """
        self.symbol: Optional[str] = symbol
        self.prob: float = prob
        self.left: Optional[HuffmanNode] = None
        self.right: Optional[HuffmanNode] = None

    def __lt__(self, other: 'HuffmanNode') -> bool:
        """Сравнение узлов по вероятности для сортировки.

        Args:
            other: Другой узел для сравнения

        Returns:
            True если текущий узел имеет меньшую вероятность
        """
        return self.prob < other.prob


def build_huffman_tree(symbols: List[str], probs: List[float]) -> Optional[HuffmanNode]:
    """Строит дерево Хаффмана на основе символов и их вероятностей.

    Args:
        symbols: Список символов алфавита
        probs: Список вероятностей символов

    Returns:
        Корень построенного дерева Хаффмана или None если дерево пустое

    Raises:
        ValueError: Если количество символов и вероятностей не совпадает
    """
    if len(symbols) != len(probs):
        raise ValueError("Количество символов и вероятностей должно совпадать")

    # Создаем начальные узлы для каждого символа
    nodes: List[HuffmanNode] = []
    for i in range(len(symbols)):
        nodes.append(HuffmanNode(symbols[i], probs[i]))

    # Построение дерева: объединяем узлы с наименьшими вероятностями
    while len(nodes) > 1:
        # Сортируем узлы по вероятности (от меньшей к большей)
        nodes.sort(key=lambda x: x.prob)

        # Берем два узла с наименьшими вероятностями
        left: HuffmanNode = nodes.pop(0)
        right: HuffmanNode = nodes.pop(0)

        # Создаем новый родительский узел
        parent: HuffmanNode = HuffmanNode(None, left.prob + right.prob)
        parent.left = left
        parent.right = right

        nodes.append(parent)

    return nodes[0] if nodes else None


def generate_huffman_codes(root: Optional[HuffmanNode]) -> Dict[str, str]:
    """Рекурсивно генерирует кодовые слова Хаффмана, обходя дерево.

    Args:
        root: Корень дерева Хаффмана

    Returns:
        Словарь, где ключ - символ, значение - кодовое слово

    Raises:
        ValueError: Если дерево пустое
    """
    if root is None:
        raise ValueError("Дерево Хаффмана не может быть пустым")

    codes: Dict[str, str] = {}

    def traverse(node: Optional[HuffmanNode], current_code: str) -> None:
        """Рекурсивно обходит дерево и генерирует коды.

        Args:
            node: Текущий узел дерева
            current_code: Текущее кодовое слово
        """
        if node is None:
            return

        if node.symbol is not None:
            # Достигли листа - сохраняем код
            codes[node.symbol] = current_code
            return

        # Идем в левого потомка, добавляя '0' к коду
        traverse(node.left, current_code + '0')
        # Идем в правого потомка, добавляя '1' к коду
        traverse(node.right, current_code + '1')

    traverse(root, "")
    return codes


def calculate_average_length(codes: Dict[str, str], symbols: List[str],
                           probs: List[float]) -> float:
    """Вычисляет среднюю длину кодового слова.

    Args:
        codes: Словарь кодовых слов
        symbols: Список символов
        probs: Список вероятностей

    Returns:
        Средняя длина кодового слова

    Raises:
        ValueError: Если количество символов и вероятностей не совпадает
    """
    if len(symbols) != len(probs):
        raise ValueError("Количество символов и вероятностей должно совпадать")

    avg_len: float = 0.0
    for i, symbol in enumerate(symbols):
        avg_len += probs[i] * len(codes[symbol])
    return avg_len


def calculate_entropy(probs: List[float]) -> float:
    """Вычисляет энтропию источника.

    Args:
        probs: Список вероятностей символов

    Returns:
        Энтропия источника в битах

    Raises:
        ValueError: Если вероятности содержат отрицательные значения
    """
    entropy: float = 0.0
    for p in probs:
        if p < 0:
            raise ValueError("Вероятности не могут быть отрицательными")
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def calculate_redundancy(avg_len: float, entropy: float) -> float:
    """Вычисляет избыточность кода.

    Args:
        avg_len: Средняя длина кодового слова
        entropy: Энтропия источника

    Returns:
        Избыточность кода
    """
    return avg_len - entropy


def check_kraft_inequality(codes: Dict[str, str]) -> Tuple[bool, float]:
    """Проверяет выполнение неравенства Крафта.

    Args:
        codes: Словарь кодовых слов

    Returns:
        Кортеж (выполняется_ли_неравенство, сумма_Крафта)
    """
    kraft_sum: float = 0.0
    for code in codes.values():
        kraft_sum += 2 ** (-len(code))

    return kraft_sum <= 1.0, kraft_sum


def encode_string(input_string: str, codes: Dict[str, str]) -> str:
    """Кодирует строку с использованием кодовых слов Хаффмана.

    Args:
        input_string: Исходная строка для кодирования
        codes: Словарь кодовых слов

    Returns:
        Закодированная битовая строка

    Raises:
        ValueError: Если в строке присутствуют символы не из алфавита
    """
    encoded: str = ""
    for char in input_string:
        if char in codes:
            encoded += codes[char]
        else:
            raise ValueError(f"Символ '{char}' отсутствует в алфавите")
    return encoded


def decode_string(encoded_string: str, root: HuffmanNode) -> str:
    """Декодирует битовую строку с использованием дерева Хаффмана.

    Args:
        encoded_string: Закодированная битовая строка
        root: Корень дерева Хаффмана

    Returns:
        Раскодированная строка

    Raises:
        ValueError: Если закодированная строка содержит недопустимые биты
                    или является неполной/некорректной
    """
    decoded: str = ""
    current_node: HuffmanNode = root

    for bit in encoded_string:
        if bit == '0':
            current_node = current_node.left
        elif bit == '1':
            current_node = current_node.right
        else:
            raise ValueError(f"Недопустимый бит в закодированной строке: '{bit}'")

        if current_node is None:
            raise ValueError("Некорректное дерево Хаффмана")

        if current_node.symbol is not None:
            # Достигли листа - добавляем символ к результату
            decoded += current_node.symbol
            current_node = root  # Возвращаемся к корню для декодирования следующего символа

    # Проверка, что декодирование завершилось в корне
    if current_node != root:
        raise ValueError("Закодированная строка некорректна или неполна")

    return decoded