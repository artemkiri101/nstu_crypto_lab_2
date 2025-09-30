"""
Модуль для работы с файлами в приложении кодирования Хаффмана.
"""

import os
from typing import List, Tuple


def read_sequence_from_file(filename: str) -> str:
    """
    Читает последовательность символов из файла.

    Args:
        filename: Имя файла для чтения

    Returns:
        Строка с содержимым файла

    Raises:
        FileNotFoundError: Если файл не существует
        IOError: Если произошла ошибка при чтении файла
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{filename}' не найден")
    except Exception as e:
        raise IOError(f"Ошибка при чтении файла '{filename}': {str(e)}")


def write_to_file(filename: str, content: str) -> None:
    """
    Записывает содержимое в файл.

    Args:
        filename: Имя файла для записи
        content: Содержимое для записи

    Raises:
        IOError: Если произошла ошибка при записи файла
    """
    try:
        # Создаем директорию, если она не существует
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        raise IOError(f"Ошибка при записи файла '{filename}': {str(e)}")