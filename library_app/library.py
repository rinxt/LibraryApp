import json
import os
import datetime
import re
from typing import Dict, List, Union, Any, Optional, Callable
from library_app.book import Book, BookStatus

DATABASE_FILE: str = "library.json"
MIN_COLUMN_WIDTH = 10
CURRENT_YEAR = datetime.datetime.now().year
MAX_ATTEMPTS = 3

class Library:
    """
    Класс, представляющий библиотеку.

    Attributes:
        books (Dict[int, Book]): Словарь, где ключи - ID книг, а значения - объекты Book.
    """

    def __init__(self):
        """
        Инициализирует объект Library, загружая данные из файла.
        """
        self.books: Dict[int, Book] = self._load_library()

    def _get_valid_input(self, prompt: str, validation_regex: str, error_message: str,
                         data_type: Callable = str, max_attempts: int = MAX_ATTEMPTS) -> Optional[Any]:
        """Получает данные от пользователя и проверяет их."""
        for attempt in range(1, max_attempts + 1):
            user_input = input(prompt).strip()
            if not user_input:
                print("Ввод не может быть пустым.")
            elif re.match(validation_regex, user_input):
                try:
                    return data_type(user_input)
                except ValueError:
                    print(f"Неверный формат данных. Ожидается {data_type.__name__}.")
            else:
                print(f"{error_message} Попытка {attempt} из {max_attempts}.")
        print("Превышено количество попыток ввода.")
        return None

    def _generate_id(self) -> int:
        """
        Генерирует уникальный ID для книги.

        Returns:
            int: Уникальный идентификатор.
        """
        return max(self.books.keys()) + 1 if self.books else 1

    def _load_library(self) -> Dict[int, Book]:
        """
        Загружает данные библиотеки из JSON файла.

        Returns:
            Dict[int, Book]: Словарь с книгами.
                Возвращает пустой словарь, если файл не найден или содержит ошибку.
        """
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, "r", encoding='utf-8') as f:
                    data: List[Dict[str, Any]] = json.load(f)
                    return {book_data["id"]: Book.from_dict(book_data) for book_data in data}
            except json.JSONDecodeError as e:
                raise ValueError(f"Ошибка декодирования JSON: {e}") from e
        else:
            print("Файл библиотеки не найден.")
            return {}

    def _save_library(self) -> None:
        """
        Сохраняет данные библиотеки в JSON файл.
        """
        data: List[Dict[str, Any]] = [book.to_dict() for book in self.books.values()]
        with open(DATABASE_FILE, "w", encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _get_book_data(self) -> Optional[Dict[str, Union[str, int]]]:
        """Получает и проверяет название книги, автора и год, введенные пользователем."""
        current_year = datetime.datetime.now().year
        title = self._get_valid_input("Введите название книги: ", r"^.+$",
                                      "Название книги не может быть пустой строкой.")
        if not title:
            return None

        author = self._get_valid_input("Введите автора книги: ", r"^.+$",
                                       "Автор книги не может быть пустой строкой.")
        if not author:
            return None

        year_str = self._get_valid_input("Введите год издания (четырехзначное число): ", r"^\d{4}$",
                                         f"Год должен быть четырехзначным числом от 1000 до {current_year}.", )

        if not year_str:
            return None

        year = int(year_str)
        if not (1000 <= year <= current_year):
            print(f"Год должен быть четырехзначным числом от 1000 до {current_year}.")
            return None
        return {"title": title, "author": author, "year": year}

    def add_book(self) -> None:
        """
        Добавляет новую книгу в библиотеку.
        """
        book_data = self._get_book_data()
        if book_data:
            book_id = self._generate_id()
            new_book = Book(book_id, book_data["title"], book_data["author"], book_data["year"])
            self.books[new_book.id] = new_book
            self._save_library()
            print("Книга добавлена!")
        else:
            print("Не удалось получить данные книги.")


    def delete_book(self) -> None:
        """
        Удаляет книгу из библиотеки по ID.
        """
        book_id = self._get_valid_input("Введите ID книги: ", r"^\d+$", "ID книги должно быть целым числом.", int)
        if book_id is not None:
            if book_id in self.books:
                del self.books[book_id]
                self._save_library()
                print("Книга удалена!")
            else:
                print("Книга с таким ID не найдена.")

    def _get_search_choice(self) -> Optional[str]:
        """Получает выбор критериев поиска."""

        search_options = {
            "1": "Название",
            "2": "Автор",
            "3": "Год издания",
            "4": "Все",
        }

        print("Выберите критерий поиска:")
        for key, value in search_options.items():
            print(f"{key}. {value}")

        choice = self._get_valid_input("Введите номер критерия поиска: ", r"^[1-4]$", "Некорректный выбор.")
        return choice

    def _perform_search(self, choice: str) -> List[Book]:
        """Выполняет поиск книг на основе выбора пользователя."""
        search_options = {
            "1": ("Название", lambda book, term: term.lower() in book.title.lower()),
            "2": ("Автор", lambda book, term: term.lower() in book.author.lower()),
            "3": ("Год издания", lambda book, term: term in str(book.year)),
            "4": ("Название, Автор или Год", lambda book, term: term.lower() in book.title.lower() or term.lower() in book.author.lower() or term in str(book.year))
        }

        if choice in search_options:
            criterion_name, search_function = search_options[choice] # Распаковываем кортеж
            search_term = input(f"Введите {criterion_name} книги для поиска: ")
            return [book for book in self.books.values() if search_function(book, search_term)]
        return []

    def search_book(self) -> None:
        """
        Ищет книги по названию, автору или году издания.
        """
        choice = self._get_search_choice()

        if choice is None:
            return

        results = self._perform_search(choice)

        if results:
            print("Найденные книги:")
            for book in results:
                print(book)
        else:
            print("Книги не найдены.")

    def display_all_books(self) -> None:
        """
        Выводит список всех книг в библиотеке в табличном формате.
        """
        if not self.books:
            print("Библиотека пуста.")
            return

        print("Все книги:")

        table_data: List[List[Union[int, str, Any]]] = []
        for book_id, book in self.books.items():
            table_data.append([book_id, book.title, book.author, book.year, book.status.value])

        if not table_data:
            print("Нет книг для отображения.")
            return

        sorted_table_data = sorted(table_data, key=lambda x: int(x[0]))

        column_widths: List[int] = [
            max(len(str(row[i])) for row in sorted_table_data)
            for i in range(len(sorted_table_data[0]))
        ]

        column_widths: List[int] = [max(width, MIN_COLUMN_WIDTH) for width in column_widths]

        headers: List[str] = ["ID", "Название", "Автор", "Год", "Статус"]

        for i, header in enumerate(headers):
            column_widths[i] = max(column_widths[i], len(header))

        def print_table_row(row_data: List[Union[int, str, Any]]) -> None:
            row_string: str = "|"
            for i, data in enumerate(row_data):
                row_string += f" {str(data):<{column_widths[i]}} |"
            print(row_string)

        separator_line: str = "+" + "+".join("-" * (w + 2) for w in column_widths) + "+"

        print(separator_line)
        print_table_row(headers)
        print(separator_line)

        for row in sorted_table_data:
            print_table_row(row)
            print(separator_line)

    def change_book_status(self) -> None:
        """Изменяет статус книги по ID."""

        book_id = self._get_valid_input("Введите ID книги: ", r"^\d+$", "ID книги должно быть целым числом.", int)
        if book_id is None:
            return

        if book_id not in self.books:
            print(f"Книга с ID {book_id} не найдена.")
            return

        book = self.books[book_id]
        print("Выбрана книга:")
        print(book)

        new_status_input = self._get_valid_input(
            "Введите новый статус (выдана, в наличии): ",  # Исправлено сообщение
            r"^(?:0|1|в наличии|выдана)$",
            "Некорректный статус. Используйте 'в наличии', 'выдана'."
        )

        if new_status_input is None:
            return

        new_status = BookStatus.from_input(new_status_input)
        if new_status is None:
            print("Некорректный статус.")
            return

        if new_status == book.status:
            print(f"Книга уже имеет статус '{new_status.value}'.")
        else:
            book.status = new_status
            print(f"Статус книги с ID {book_id} успешно изменен на '{book.status.value}'.")

        self._save_library()