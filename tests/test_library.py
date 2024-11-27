import unittest
from io import StringIO
from unittest.mock import patch, mock_open
import os
import json

from library_app.library import Library
from library_app.book import Book, BookStatus

DATABASE_FILE = "library.json"

class TestLibrary(unittest.TestCase):
    """
    Класс, содержащий тесты для класса Library.
    """

    def setUp(self):
        """
        Выполняется перед каждым тестом.
        Создает экземпляр библиотеки и очищает файл базы данных (если существует).
        """
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)
        self.library = Library()
        self.library.DATABASE_FILE = DATABASE_FILE

    def tearDown(self):
        """
        Выполняется после каждого теста.
        Удаляет файл базы данных (если существует).
        """
        if os.path.exists(DATABASE_FILE):
            os.remove(DATABASE_FILE)

    def test_generate_id_empty_library(self):
        """Тестирует генерацию ID в пустой библиотеке."""
        self.assertEqual(self.library._generate_id(), 1)
        self.assertEqual(self.library.next_id, 1)

    def test_generate_id_non_empty_library(self):
        """Тестирует генерацию ID в непустой библиотеке."""
        self.library.books = {
            1: Book(book_id=1, title="Book 1", author="Author 1", year=2000),
            3: Book(book_id=3, title="Book 3", author="Author 3", year=2020)
        }
        self.assertEqual(self.library._generate_id(), 4)
        self.assertEqual(self.library.next_id, 4)

    @patch("json.load")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_load_library_success(self, mock_open, mock_exists, mock_load):
        """Тестирует успешную загрузку библиотеки из файла."""
        mock_load.return_value = [
            {
                "id": 1,
                "title": "Python Crash Course",
                "author": "Eric Matthes",
                "year": 2019,
                "status": "в наличии",
            },
            {
                "id": 2,
                "title": "Гарри Поттер и философский камень",
                "author": "Джоан Роулинг",
                "year": 1997,
                "status": "выдана"
            }
        ]

        loaded_books = self.library._load_library()
        self.assertEqual(len(loaded_books), 2)
        self.assertIsInstance(loaded_books[1], Book)
        self.assertEqual(loaded_books[1].title, "Python Crash Course")
        self.assertEqual(loaded_books[2].status, BookStatus.ISSUED)
        mock_load.assert_called_once()
        mock_exists.assert_called_once()
        mock_open.assert_called_once_with(DATABASE_FILE, "r", encoding='utf-8')

    @patch("os.path.exists", return_value=False)
    def test_load_library_file_not_found(self, mock_exists):
        """Тестирует загрузку библиотеки при отсутствии файла."""
        loaded_books = self.library._load_library()
        self.assertEqual(loaded_books, {})
        mock_exists.assert_called_once()

    @patch("json.load", side_effect=json.JSONDecodeError("Error", "doc", 1))
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open)
    def test_load_library_json_decode_error(self, mock_open, mock_exists, mock_load):
        """Тестирует загрузку библиотеки при ошибке декодирования JSON."""
        loaded_books = self.library._load_library()
        self.assertEqual(loaded_books, {})
        mock_exists.assert_called_once()
        mock_open.assert_called_once_with(DATABASE_FILE, "r", encoding='utf-8')
        mock_load.assert_called_once()

    @patch("json.dump")
    def test_save_library(self, mock_dump):
        """Тестирует сохранение библиотеки в файл."""
        self.library.books = {
            1: Book(book_id=1, title="Python Crash Course", author="Eric Matthes", year=2019,
                    status=BookStatus.AVAILABLE),
            2: Book(book_id=2, title="Clean Code", author="Robert C. Martin", year=2008, status=BookStatus.ISSUED),
        }
        self.library._save_library()
        mock_dump.assert_called_once()

    @patch("builtins.input", side_effect=["New Book", "Eric Matthes", "2019"])
    @patch.object(Library, '_save_library')
    def test_add_book_success(self, mock_save, mock_input):
        """Тестирует успешное добавление книги."""
        self.library.add_book()
        self.assertIn(1, self.library.books)
        self.assertEqual(self.library.books[1].title, "New Book")
        self.assertEqual(self.library.books[1].author, "Eric Matthes")
        self.assertEqual(self.library.books[1].year, 2019)
        self.assertEqual(self.library.books[1].status, BookStatus.AVAILABLE)
        mock_save.assert_called_once()

    @patch("builtins.input", side_effect=["", "", "", "", "", "invalid"])
    def test_add_book_invalid_input(self, mock_input):
        """Тестирует, что книга не добавляется при любом некорректном вводе."""
        initial_book_count = len(self.library.books)
        with patch('sys.stdout', new_callable=StringIO) as mocked_stdout:
            self.library.add_book()
            output = mocked_stdout.getvalue()
            self.assertIn("Ввод не может быть пустым.", output)
            self.assertIn("Не удалось получить данные книги.", output)
        self.assertEqual(len(self.library.books), initial_book_count)

    @patch("builtins.input", side_effect=["1"])
    def test_delete_book_success(self, mock_input):
        """Тестирует успешное удаление книги."""
        self.library.books = {
            1: Book(book_id=1, title="Book 1", author="Author 1", year=2000),
            2: Book(book_id=2, title="Book 2", author="Author 2", year=2010),
        }
        self.library.delete_book()
        self.assertEqual(len(self.library.books), 1)
        self.assertNotIn(1, self.library.books)
        self.assertIn(2, self.library.books)

    @patch("builtins.input", side_effect=["1", "Python", "2", "Matthes", "3", "2019", "4", "Python"])
    def test_search_book(self, mock_input):
        """Тестирует поиск книги по разным критериям."""
        self.library.books = {
            1: Book(book_id=1, title="Python Crash Course", author="Eric Matthes", year=2019),
            2: Book(book_id=2, title="Clean Code", author="Robert C. Martin", year=2008),
            3: Book(book_id=3, title="Python Basics", author="David Mertz", year=2020),
        }

        self.library.search_book()
        self.library.search_book()
        self.library.search_book()
        self.library.search_book()

    def test_display_all_books_empty(self):
        """Тестирует отображение всех книг в пустой библиотеке."""
        with patch("sys.stdout", new_callable=StringIO) as mocked_stdout:
            self.library.display_all_books()
            self.assertIn("Библиотека пуста.", mocked_stdout.getvalue())

    def test_display_all_books_non_empty(self):
        """Тестирует отображение всех книг в непустой библиотеке."""
        self.library.books = {
            1: Book(book_id=1, title="Python Crash Course", author="Eric Matthes", year=2019,
                    status=BookStatus.AVAILABLE),
            2: Book(book_id=2, title="Clean Code", author="Robert C. Martin", year=2008, status=BookStatus.ISSUED),
        }
        with patch("sys.stdout", new_callable=StringIO) as mocked_stdout:
            self.library.display_all_books()
            output = mocked_stdout.getvalue()
            self.assertIn("Python Crash Course", output)
            self.assertIn("Clean Code", output)
            self.assertIn("в наличии", output)
            self.assertIn("выдана", output)

    @patch("builtins.input", side_effect=["1", "0", "1", "1"])
    def test_change_book_status_success(self, mock_input):
        """Тестирует успешное изменение статуса книги."""
        self.library.books = {
            1: Book(book_id=1, title="Book 1", author="Author 1", year=2000, status=BookStatus.AVAILABLE),
        }
        self.library.change_book_status()
        self.assertEqual(self.library.books[1].status, BookStatus.ISSUED)

        self.library.change_book_status()
        self.assertEqual(self.library.books[1].status, BookStatus.AVAILABLE)

    @patch("builtins.input", side_effect=["1", "3", "1"])
    def test_change_book_status_invalid_status(self, mock_input):
        """Тестирует изменение статуса книги с некорректным статусом."""
        self.library.books = {
            1: Book(book_id=1, title="Book 1", author="Author 1", year=2000, status=BookStatus.AVAILABLE),
        }
        self.library.change_book_status()
        self.assertEqual(self.library.books[1].status, BookStatus.AVAILABLE)

    def test_integration_add_and_load(self):
        """Тестирует интеграцию добавления и загрузки книги."""
        with patch("builtins.input", side_effect=["New Book", "New Author", "2023"]):
            self.library.add_book()

        loaded_library = Library()
        self.assertEqual(len(loaded_library.books), 1)
        self.assertEqual(loaded_library.books[1].title, "New Book")
        self.assertEqual(loaded_library.books[1].author, "New Author")
        self.assertEqual(loaded_library.books[1].year, 2023)

    def test_integration_delete_and_load(self):
        """Тестирует интеграцию удаления и загрузки книги."""
        self.library.books = {
            1: Book(book_id=1, title="Book 1", author="Author 1", year=2000),
        }
        self.library._save_library()

        with patch("builtins.input", side_effect=["1"]):
            self.library.delete_book()

        loaded_library = Library()
        self.assertEqual(len(loaded_library.books), 0)

    def test_integration_change_status_and_load(self):
        """Тестирует интеграцию изменения статуса и загрузки."""
        self.library.books = {
            1: Book(book_id=1, title="Book 1", author="Author 1", year=2000, status=BookStatus.AVAILABLE),
        }
        self.library._save_library()

        with patch("builtins.input", side_effect=["1", "0"]):
            self.library.change_book_status()

        loaded_library = Library()
        self.assertEqual(loaded_library.books[1].status, BookStatus.ISSUED)


if __name__ == "__main__":
    unittest.main()