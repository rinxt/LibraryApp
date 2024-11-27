from library_app.library import Library


def main() -> None:
    """
    Главная функция приложения.
    Запускает основной цикл программы и обрабатывает ввод пользователя.
    """
    library: Library = Library()

    while True:
        print("\nМеню:")
        print("1. Добавить книгу")
        print("2. Удалить книгу")
        print("3. Поиск книги")
        print("4. Вывести все книги")
        print("5. Изменить статус книги")
        print("6. Выход")

        choice: str = input("Выберите пункт меню: ")

        if choice == "1":
            library.add_book()
        elif choice == "2":
            library.delete_book()
        elif choice == "3":
            library.search_book()
        elif choice == "4":
            library.display_all_books()
        elif choice == "5":
            library.change_book_status()
        elif choice == "6":
            break
        else:
            print("Некорректный выбор.")


if __name__ == "__main__":
    main()