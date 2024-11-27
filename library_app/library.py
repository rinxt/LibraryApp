import json
import os
import datetime
import re
from typing import Dict, List, Union, Any, Optional
from library_app.book import Book, BookStatus

DATABASE_FILE: str = "library.json"


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

    def _generate_id(self) -> int:
        """
        Генерирует уникальный ID для книги.

        Returns:
            int: Уникальный идентификатор.
        """
        if not self.books:
            self.next_id = 1
        else:
            self.next_id = max(self.books.keys()) + 1
        return self.next_id

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
                print("Ошибка при чтении файла JSON:", e)
                return {}
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

    def _get_valid_input(self, prompt: str, validation_regex: str, error_message: str, max_attempts: int = 3) -> \
    Optional[str]:
        """Получает введенные пользователем данные и проверяет их на соответствие шаблону регулярного выражения."""
        for attempt in range(max_attempts):
            user_input = input(prompt).strip()
            if not user_input:
                print("Ввод не может быть пустым.")
                continue
            if re.match(validation_regex, user_input):
                return user_input
            else:
                print(f"{error_message} Попытка {attempt + 1} из {max_attempts}.")
        print("Превышено количество попыток ввода.")
        return None

    def _get_book_id(self) -> Optional[int]:
        """Получает и проверяет идентификатор книги, введенный пользователем."""
        book_id_str = self._get_valid_input(
            "Введите ID книги: ",
            r"^\d+$",
            "ID книги должно быть целым числом.",
        )
        if book_id_str:
            return int(book_id_str)
        return None


    def _get_new_book_status(self) -> Optional[BookStatus]:
        """Получает и проверяет статус новой книги на основе введенных пользователем данных."""
        validation_regex = r"^(?:0|1|в наличии|выдана)$"
        error_message = "Некорректный статус. Используйте 1, 0 или 'в наличии', 'выдана'."
        status_input = self._get_valid_input(
            "Введите новый статус (1 - в наличии, 0 - выдана): ",
            validation_regex,
            error_message,
        )

        if status_input:
            new_status = BookStatus.from_input(status_input)
            if new_status:
                return new_status
        return None

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
        book_id = self._get_book_id()

        if book_id is None:
            return

        if book_id in self.books:
            del self.books[book_id]
            self._save_library()
            print("Книга удалена!")
        else:
            print("Книга с таким ID не найдена.")

    def _get_search_choice(self) -> Optional[str]:
        """Получает и проверяет выбор критериев поиска из введенных пользователем данных."""
        print("Выберите критерий поиска:")
        print("1. Название")
        print("2. Автор")
        print("3. Год издания")
        print("4. Все")
        return self._get_valid_input("Введите номер критерия поиска: ", r"^[1-4]$",
                                     "Некорректный выбор. Введите число от 1 до 4.")

    def _perform_search(self, choice: str) -> List[Book]:
        """Выполняет поиск книг на основе выбора пользователя."""
        if choice == "1":
            search_term = input("Введите название книги для поиска: ")
            return [book for book in self.books.values() if search_term.lower() in book.title.lower()]
        elif choice == "2":
            search_term = input("Введите автора книги для поиска: ")
            return [book for book in self.books.values() if search_term.lower() in book.author.lower()]
        elif choice == "3":
            search_term = input("Введите год издания книги для поиска: ")
            return [book for book in self.books.values() if search_term in str(book.year)]
        elif choice == "4":
            search_term = input("Введите название, автора или год для поиска: ")
            return [
                book for book in self.books.values()
                if search_term.lower() in book.title.lower()
                   or search_term.lower() in book.author.lower()
                   or search_term in str(book.year)
            ]
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

        min_column_width: int = 10
        column_widths: List[int] = [max(width, min_column_width) for width in column_widths]

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
        """
        Изменяет статус книги по ID.
        """
        book_id = self._get_book_id()

        if book_id is None:
            return

        if book_id not in self.books:
            print(f"Книга с ID {book_id} не найдена.")
            return

        book = self.books[book_id]
        print("Выбрана книга:")
        print(book)

        new_status = None
        attempts = 0
        while new_status is None and attempts < 3:
            new_status = self._get_new_book_status()
            attempts += 1
            if new_status is None and attempts < 3:
                print("Пожалуйста, попробуйте снова.")
            elif new_status is None:
                print("Превышено количество попыток ввода статуса.")

            if new_status == book.status:
                print(f"Книга уже имеет статус '{new_status.value}'.")
                return

        if new_status is None:
            return

        book.status = new_status
        self._save_library()
        print(f"Статус книги с ID {book_id} успешно изменен на '{book.status.value}'.")