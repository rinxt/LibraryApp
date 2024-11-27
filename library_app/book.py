from enum import Enum
from typing import Dict, Union, Optional

class BookStatus(Enum):
    """Статус книги."""
    AVAILABLE = "в наличии"
    ISSUED = "выдана"

    @classmethod
    def from_input(cls, input_str: str) -> Optional['BookStatus']:
        input_str = input_str.lower()
        if input_str in ("1", "в наличии"):
            return cls.AVAILABLE
        elif input_str in ("0", "выдана"):
            return cls.ISSUED
        else:
            return None

class Book:
    """
    Класс, представляющий книгу.

    Attributes:
        id (int): Уникальный идентификатор книги.
        title (str): Название книги.
        author (str): Автор книги.
        year (int): Год издания книги.
        status (BookStatus): Статус книги ("в наличии" или "выдана").
    """

    def __init__(self, book_id: int, title: str, author: str, year: int,
                 status: BookStatus = BookStatus.AVAILABLE):
        """
        Инициализирует объект Book.

        Args:
            book_id (int): Уникальный идентификатор книги.
            title (str): Название книги.
            author (str): Автор книги.
            year (int): Год издания книги.
            status (BookStatus, optional): Статус книги. По умолчанию BookStatus.AVAILABLE.

        Raises:
            TypeError: Если тип года издания книги не является целым числом.
            TypeError: Если тип названия или автора книги не является строкой.
        """
        if not isinstance(book_id, int):
            raise TypeError("ID книги должен быть целым числом")
        if not isinstance(year, int):
            raise TypeError("Год издания книги должен быть целым числом")
        if not isinstance(title, str) or not isinstance(author, str):
            raise TypeError("Название и автор книги должны быть строками")

        self.id: int = book_id
        self.title: str = title
        self.author: str = author
        self.year: int = year
        self.status: BookStatus = status

    def __str__(self) -> str:
        """
        Возвращает строковое представление книги.

        Returns:
            str: Отформатированная строка с информацией о книге.
        """
        return (f"\nID: {self.id}\nНазвание: {self.title}\n"
                f"Автор: {self.author}\nГод: {self.year}\nСтатус: {self.status.value}\n{'-' * 20}")

    def to_dict(self) -> Dict[str, Union[int, str]]:
        """
        Преобразует объект Book в словарь.

        Returns:
            Dict[str, Union[int, str]]: Словарь, представляющий книгу.
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Union[int, str]]) -> "Book":
        """
        Создает объект Book из словаря.

        Args:
            data (Dict[str, Union[int, str]]): Словарь с данными книги.

        Returns:
            Book: Объект Book, созданный из словаря.

        Raises:
            KeyError: Если в словаре отсутствуют необходимые ключи.
            ValueError: Если значение ID или года издания книги не является целым числом.
            ValueError: Если значение статуса книги не является допустимым.
        """
        required_keys = {"id", "title", "author", "year", "status"}
        if not required_keys.issubset(data):
            raise KeyError(f"В словаре отсутствуют необходимые ключи: {required_keys - set(data)}")

        try:
            book_id = int(data["id"])
        except ValueError as e:
            raise ValueError(f"ID книги должен быть целым числом: {e}")

        try:
            year = int(data["year"])
        except ValueError as e:
            raise ValueError(f"Год издания книги должен быть целым числом: {e}")

        try:
            status = BookStatus(data["status"])
        except ValueError as e:
            raise ValueError(f"Недопустимый статус книги: {e}")

        return cls(
            book_id=book_id,
            title=data["title"],
            author=data["author"],
            year=year,
            status=status,
        )