import json
import os
import datetime
from typing import Dict, List, Union, Any
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

    def add_book(self) -> None:
        """
        Добавляет новую книгу в библиотеку.
        Запрашивает у пользователя название, автора и год издания книги.
        """
        current_year = datetime.datetime.now().year

        for attempt in range(3):
            title: str = input("Введите название книги: ").strip()
            if not title:
                print("Название книги не может быть пустой строкой.")
                continue

            author: str = input("Введите автора книги: ").strip()
            if not author:
                print("Автор книги не может быть пустой строкой.")
                continue

            year_str: str = input("Введите год издания (четырехзначное число): ").strip()

            try:
                year: int = int(year_str)
                if not (1000 <= year <= current_year):
                    raise ValueError("Год должен быть четырехзначным числом и не может быть больше текущего года.")
                book_id = self._generate_id()
                new_book: Book = Book(book_id, title, author, year)
                self.books[new_book.id] = new_book
                self._save_library()
                print("Книга добавлена!")
                return
            except ValueError as e:
                print(f"Ошибка: {e}")
                if attempt < 2:
                    print("Попробуйте еще раз.")
            except Exception as e:
                print(f"Произошла непредвиденная ошибка: {e}")
                if attempt < 2:
                    print("Попробуйте еще раз.")

        print("Превышено количество попыток. Книга не добавлена.")

    def delete_book(self) -> None:
        """
        Удаляет книгу из библиотеки по ID.
        Запрашивает у пользователя ID книги для удаления.
        """
        for attempt in range(3):
            book_id_str: str = input("Введите ID книги для удаления: ").strip()
            if not book_id_str.isdigit():
                print("ID книги должен быть целым числом.")
                continue

            book_id: int = int(book_id_str)

            if book_id in self.books:
                del self.books[book_id]
                self._save_library()
                print("Книга удалена!")
                return
            else:
                print("Книга с таким ID не найдена.")
                if attempt < 2:
                    print("Попробуйте еще раз.")
        print("Превышено количество попыток. Книга не удалена.")

    def search_book(self) -> None:
        """
        Ищет книги по названию, автору или году издания.
        Запрашивает у пользователя строку для поиска.
        """
        while True:
            print("Выберите критерий поиска:")
            print("1. Название")
            print("2. Автор")
            print("3. Год издания")
            print("4. Все")
            choice = input("Введите номер критерия поиска: ")

            if choice == "1":
                search_term: str = input("Введите название книги для поиска: ")
                results: List[Book] = [book for book in self.books.values() if
                                       search_term.lower() in book.title.lower()]
            elif choice == "2":
                search_term: str = input("Введите автора книги для поиска: ")
                results: List[Book] = [book for book in self.books.values() if
                                       search_term.lower() in book.author.lower()]
            elif choice == "3":
                search_term: str = input("Введите год издания книги для поиска: ")
                results: List[Book] = [book for book in self.books.values() if search_term in str(book.year)]
            elif choice == "4":
                search_term: str = input("Введите название, автора или год для поиска: ")
                results: List[Book] = [
                    book for book in self.books.values()
                    if search_term.lower() in book.title.lower()
                       or search_term.lower() in book.author.lower()
                       or search_term in str(book.year)
                ]
            else:
                print("Некорректный выбор. Пожалуйста, выберите снова.")
                continue

            if results:
                print("Найденные книги:")
                for book in results:
                    print(book)
            else:
                print("Книги не найдены.")
            break

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
        Запрашивает у пользователя ID книги и новый статус (1 - в наличии, 0 - выдана).
        """
        status_map: Dict[str, BookStatus] = {
            "1": BookStatus.AVAILABLE,
            "0": BookStatus.ISSUED,
        }

        for attempt in range(3):
            try:
                book_id: int = int(input("Введите ID книги для изменения статуса: "))

                if book_id in self.books:
                    for _ in range(3):
                        new_status_input: str = input("Введите новый статус (1 - в наличии, 0 - выдана): ")
                        if not new_status_input:
                            print("Новый статус не может быть пустой строкой.")
                            continue

                        try:
                            new_status = status_map[new_status_input]
                            self.books[book_id].status = new_status
                            self._save_library()
                            print("Статус книги изменен!")
                            return
                        except KeyError:
                            print("Некорректный статус. Используйте 1 (в наличии) или 0 (выдана).")
                            continue

                    print("Превышено количество попыток ввода статуса.")
                    return

                else:
                    print("Книга с таким ID не найдена.")
                    raise ValueError("Книга не найдена")

            except ValueError as e:
                if str(e) == "Книга не найдена":
                    raise
                else:
                    print("ID книги должно быть целым числом.")

        print("Превышено количество попыток.")