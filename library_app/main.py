from library_app.library import Library

def main() -> None:
    library = Library()
    menu_options = [
        ("1", library.add_book, "Добавить книгу"),
        ("2", library.delete_book, "Удалить книгу"),
        ("3", library.search_book, "Поиск книги"),
        ("4", library.display_all_books, "Вывести все книги"),
        ("5", library.change_book_status, "Изменить статус книги"),
        ("6", exit, "Выход"),
    ]

    while True:
        print("\nМеню:")
        for key, action, description in menu_options:
            print(f"{key}. {description}")

        choice = input("Выберите пункт меню: ")

        for key, action, _ in menu_options:
            if choice == key:
                if action is exit:
                    action()
                else:
                    action()
                break
        else:
            print("Некорректный выбор.")


if __name__ == "__main__":
    main()