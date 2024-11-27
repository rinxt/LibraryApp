import unittest
from library_app.book import Book, BookStatus


class TestBook(unittest.TestCase):
    """
    Класс, содержащий тесты для класса Book.
    """

    def test_book_creation(self):
        """Тестирует создание объекта Book с корректными данными."""
        book = Book(book_id=1, title="Python Crash Course", author="Eric Matthes", year=2019)
        self.assertEqual(book.id, 1)
        self.assertEqual(book.title, "Python Crash Course")
        self.assertEqual(book.author, "Eric Matthes")
        self.assertEqual(book.year, 2019)
        self.assertEqual(book.status, BookStatus.AVAILABLE)

        book_issued = Book(book_id=2, title="Clean Code", author="Robert C. Martin", year=2008,
                           status=BookStatus.ISSUED)
        self.assertEqual(book_issued.status, BookStatus.ISSUED)

    def test_book_creation_with_invalid_id(self):
        """Тестирует создание объекта Book с некорректным типом ID (не целое число)."""
        with self.assertRaises(TypeError):
            Book(book_id="1", title="Python Crash Course", author="Eric Matthes", year=2019)

    def test_book_creation_with_invalid_year(self):
        """Тестирует создание объекта Book с некорректным типом года (не целое число)."""
        with self.assertRaises(TypeError):
            Book(book_id=1, title="Python Crash Course", author="Eric Matthes", year="2019")

    def test_book_creation_with_invalid_title(self):
        """Тестирует создание объекта Book с некорректным типом названия (не строка)."""
        with self.assertRaises(TypeError):
            Book(book_id=1, title=123, author="Eric Matthes", year=2019)

    def test_book_creation_with_invalid_author(self):
        """Тестирует создание объекта Book с некорректным типом автора (не строка)."""
        with self.assertRaises(TypeError):
            Book(book_id=1, title="Python Crash Course", author=123, year=2019)

    def test_book_str(self):
        """Тестирует строковое представление объекта Book."""
        book = Book(book_id=1, title="Python Crash Course", author="Eric Matthes", year=2019)
        expected_str = (
            "\nID: 1\nНазвание: Python Crash Course\n"
            "Автор: Eric Matthes\nГод: 2019\nСтатус: в наличии\n"
            "--------------------"
        )
        self.assertEqual(str(book), expected_str)

    def test_book_to_dict(self):
        """Тестирует преобразование объекта Book в словарь."""
        book = Book(book_id=1, title="Python Crash Course", author="Eric Matthes", year=2019,
                    status=BookStatus.ISSUED)
        expected_dict = {
            "id": 1,
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "year": 2019,
            "status": "выдана",
        }
        self.assertEqual(book.to_dict(), expected_dict)

    def test_book_from_dict(self):
        """Тестирует создание объекта Book из словаря."""
        data = {
            "id": 1,
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "year": 2019,
            "status": "в наличии",
        }
        book = Book.from_dict(data)
        self.assertEqual(book.id, 1)
        self.assertEqual(book.title, "Python Crash Course")
        self.assertEqual(book.author, "Eric Matthes")
        self.assertEqual(book.year, 2019)
        self.assertEqual(book.status, BookStatus.AVAILABLE)

        data_issued = {
            "id": 2,
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "year": 2008,
            "status": "выдана",
        }
        book_issued = Book.from_dict(data_issued)
        self.assertEqual(book_issued.status, BookStatus.ISSUED)

    def test_book_from_dict_missing_key(self):
        """Тестирует создание объекта Book из словаря с отсутствующим ключом."""
        data = {
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "year": 2019,
            "status": "в наличии",
        }
        with self.assertRaises(KeyError):
            Book.from_dict(data)

    def test_book_from_dict_invalid_id_type(self):
        """Тестирует создание объекта Book из словаря с некорректным типом ID."""
        data = {
            "id": "invalid",
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "year": 2019,
            "status": "в наличии",
        }
        with self.assertRaises(ValueError) as context:
            Book.from_dict(data)
        self.assertEqual(str(context.exception),
                         "ID книги должен быть целым числом: invalid literal for int() with base 10: 'invalid'")

    def test_book_from_dict_invalid_year_type(self):
        """Тестирует создание объекта Book из словаря с некорректным типом года."""
        data = {
            "id": 1,
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "year": "invalid",
            "status": "в наличии",
        }
        with self.assertRaises(ValueError) as context:
            Book.from_dict(data)
        self.assertEqual(str(context.exception),
                         "Год издания книги должен быть целым числом: invalid literal for int() with base 10: 'invalid'")

    def test_book_from_dict_invalid_status(self):
        """Тестирует создание объекта Book из словаря с некорректным значением статуса."""
        data = {
            "id": 1,
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "year": 2019,
            "status": "invalid_status",
        }
        with self.assertRaises(ValueError) as context:
            Book.from_dict(data)
        self.assertIn("Недопустимый статус книги", str(context.exception))



if __name__ == "__main__":
    unittest.main()