import json
from datetime import datetime

import pytest

from library import show_balance, read_int, read_date, read_rental, add_rental, init_books
from rental import Rental


def test_show_balance(sample_books_filled, capsys):
    show_balance(sample_books_filled)
    captured = capsys.readouterr()

    expected_output = """Statement for LOTR 1
  - 05.01.2023: CHF 188.75
Total: CHF 188.75
Statement for LOTR 2
  - 06.01.2023: CHF 131.8
Total: CHF 131.8
Statement for LOTR 3
  - 06.01.2023: CHF 131.8
  - 06.01.2023: CHF 131.8
Total: CHF 263.6
"""
    assert captured.out == expected_output


def test_init_books(empty_books):
    books = init_books()
    assert books == empty_books


def test_read_rental(monkeypatch):
    inputs = iter(['05.01.2023', '60', '06.03.2023'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    rental = read_rental()
    assert rental.rental_date == datetime(2023, 1, 5)
    assert rental.num_rental_days == 60
    assert rental.return_date == datetime(2023, 3, 6)


def test_add_rental_empty_books(empty_books, monkeypatch):
    inputs = iter(['LOTR 1', '05.01.2023', '60', '06.03.2023', 'n'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    add_rental(empty_books)
    assert len(empty_books['LOTR 1']) == 1
    assert len(empty_books['LOTR 2']) == 0


def test_add_rental_existing_books(sample_books_filled, monkeypatch):
    inputs = iter(['LOTR 1', '05.01.2023', '60', '06.03.2023', 'n'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    add_rental(sample_books_filled)
    assert len(sample_books_filled['LOTR 1']) == 2
    assert len(sample_books_filled['LOTR 2']) == 1
    assert len(sample_books_filled['LOTR 3']) == 2


def test_add_rental_invalid_book_name(sample_books_filled, monkeypatch):
    # Simulating user inputs: first an invalid book, then a valid one with rental details
    inputs = iter(['Invalid Book', 'LOTR 1', '07.01.2023', '30', '08.03.2023', 'n'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    add_rental(sample_books_filled)
    # Asserting that the rental was added to the valid book
    assert len(sample_books_filled['LOTR 1']) == 2


def test_add_rental_multiple_rentals(sample_books_filled, monkeypatch):
    # Simulating user inputs for adding multiple rentals to the same book
    inputs = iter(['LOTR 1', '08.01.2023', '20', '28.01.2023', 'y', 'LOTR 1', '09.01.2023', '15', '24.01.2023', 'n'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    add_rental(sample_books_filled)
    # Asserting that multiple rentals have been added to the same book
    assert len(sample_books_filled['LOTR 1']) == 3


def test_read_int_valid_input(monkeypatch):
    inputs = iter(['5'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    value = read_int('Enter a number: ', 1, 9)
    assert value == 5


def test_read_int_invalid_input(monkeypatch, capsys):
    inputs = iter(['abs', '-5', '2', '1'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    value = read_int('Enter a number: ', 0, 1)
    captured = capsys.readouterr()
    assert value == 1
    assert captured.out == 'Please, enter a whole number!\nPlease, enter a number greater than or equal to 0\nPlease, enter a number less than or equal to 1\n'


def test_read_date_valid_input(monkeypatch, capsys):
    # Mocking user input with valid date format
    inputs = iter(['05.01.2023'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    date = read_date('Enter a date (dd.mm.yyyy): ')
    captured = capsys.readouterr()
    assert date == datetime(2023, 1, 5)  # Should return the valid date
    assert captured.out == ''  # No error message should be printed


def test_read_date_invalid_input(monkeypatch, capsys):
    # Mocking user input with invalid date format
    inputs = iter(['abc', '01/05/2023', '05.01.2023'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    date = read_date('Enter a date (dd.mm.yyyy): ')
    captured = capsys.readouterr()
    assert date == datetime(2023, 1, 5)  # Should return the valid date
    assert captured.out == 'Please enter a valid date.\nPlease enter a valid date.\n'  # Error messages should be printed


@pytest.fixture
def sample_books_filled():
    books = {
        'LOTR 1': [
            Rental(datetime(2023, 1, 5), datetime(2023, 3, 6), 5),
        ],
        'LOTR 2': [
            Rental(datetime(2023, 1, 6), datetime(2023, 2, 23), 10),
        ],
        'LOTR 3': [
            Rental(datetime(2023, 1, 6), datetime(2023, 2, 23), 10),
            Rental(datetime(2023, 1, 6), datetime(2023, 2, 23), 10),
        ],
    }
    return books


@pytest.fixture
def empty_books():
    with open('books.json', 'r') as file:
        return json.load(file)
