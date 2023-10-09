import pickle
import itertools
from datetime import date, datetime

def input_error(func):
    def add_contact(self, name, phone):
        self.contacts[name] = phone
        return f"Added {name} with phone number {phone}"
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name"
        except (ValueError, IndexError):
            return "Give me name and phone please"

    return wrapper

    def add_contact(self, name, phone):
        self.contacts[name] = phone
        return f"Added {name} with phone number {phone}"

class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return str(self._value)

    @value.setter
    def value(self, value):
        self.validate(value)
        self._value = value

    def validate(self, value):
        pass

    def __str__(self):
        return str(self._value)


class Name(Field):
    pass


class Phone(Field):
    def validate(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Неверный формат номера телефона")


class Birthday(Field):
    def validate(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Неверный формат даты дня рождения")


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None

    def days_to_birthday(self):
        if self.birthday:
            today = date.today()
            next_birthday = date(
                today.year, self.birthday.value.month, self.birthday.value.day
            )
            if today > next_birthday:
                next_birthday = date(
                    today.year + 1, self.birthday.value.month, self.birthday.value.day
                )
            days_left = (next_birthday - today).days
            return days_left
        else:
            return None

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if old_phone in [p.value for p in self.phones]:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}"


class AddressBook:
    def __init__(self, file_name):
        self.file_name = file_name
        self.load_from_disk()

    def load_from_disk(self):
        try:
            with open(self.file_name, 'rb') as file:
                self.data = pickle.load(file)
        except (FileNotFoundError, EOFError):
            self.data = {}

    def save_to_disk(self):
        with open(self.file_name, 'wb') as file:
            pickle.dump(self.data, file)

    def add_record(self, record):
        self.data[record.name.value] = record
        self.save_to_disk()

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def search(self, query):
        results = []
        for name, record in self.data.items():
            if query in name or any(query in phone.value for phone in record.phones):
                results.append(record)
        return results


class AssistantBot:
    def __init__(self, address_book):
        self.address_book = address_book

    @input_error
    def add_contact(self, name, phone):
        record = self.address_book.find(name)
        if record:
            record.phones.append(Phone(phone))
            return f"Added {phone} to {name}'s contact"
        else:
            record = Record(name)
            record.phones.append(Phone(phone))
            self.address_book.add_record(record)
            return f"Added {name} with phone number {phone}"

    @input_error
    def change_contact(self, name, phone):
        record = self.address_book.find(name)
        if record:
            record.phones.append(Phone(phone))
            return f"Changed phone number for {name} to {phone}"
        else:
            return f"Contact {name} not found"

    @input_error
    def show_phone(self, name):
        record = self.address_book.find(name)
        if record:
            return f"{name}'s phone number is {', '.join(p.value for p in record.phones)}"
        else:
            return f"Contact {name} not found"

    def show_all(self):
        if not self.address_book.data:
            return "No contacts found"
        else:
            result = ""
            for name, record in self.address_book.data.items():
                result += f"{name}: {', '.join(p.value for p in record.phones)}\n"
            return result

    def handle_command(self, command):
        command = command.lower()
        if command == "hello":
            return "How can I help you?"
        elif command.startswith("add "):
            parts = command.split(" ", 2)
            if len(parts) != 3:
                return "Invalid input format"
            name, phone = parts[1], parts[2]
            return self.add_contact(name, phone)
        elif command.startswith("change "):
            parts = command.split(" ", 2)
            if len(parts) != 3:
                return "Invalid input format"
            name, phone = parts[1], parts[2]
            return self.change_contact(name, phone)
        elif command.startswith("phone "):
            name = command.split(" ", 1)[1]
            return self.show_phone(name)
        elif command == "show all":
            return self.show_all()
        elif command == "search":
            query = input("Enter search query: ")
            results = self.address_book.search(query)
            if results:
                for result in results:
                    print(result)
            else:
                return "No results found."
        elif command in ("good bye", "close", "exit"):
            self.address_book.save_to_disk()
            return "Good bye!"
        else:
            return "Unknown command"

    def run(self):
        while True:
            command = input("Enter a command: ")
            if command == ".":
                self.address_book.save_to_disk()
                break
            response = self.handle_command(command)
            print(response)


if __name__ == "__main__":
    file_name = "address_book.pickle"
    address_book = AddressBook(file_name)
    bot = AssistantBot(address_book)
    bot.run()
