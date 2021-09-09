import random
import sqlite3

CREATE_CARD_TABLE = """CREATE TABLE IF NOT EXISTS card (
id INTEGER PRIMARY KEY, 
number TEXT, 
pin TEXT, 
balance INTEGER DEFAULT 0
);"""
INSERT_CARD = "INSERT INTO card (number, pin) VALUES (?, ?)"
GET_CARD_BY_PIN = "SELECT number FROM card WHERE pin = ?;"
GET_PIN_BY_CARD = "SELECT pin FROM card WHERE number = ?;"
GET_BALANCE_BY_NUMBER = "SELECT balance FROM card WHERE number = ?;"
GET_ALL_CARD_NUMBERS = "SELECT number FROM card;"
DELETE_CARD = "DELETE FROM card WHERE number = ?;"
UPDATE_CARD_BALANCE = "UPDATE card SET balance = ? WHERE number = ?;"


class BankingSystem:

    def __init__(self):
        self.credit_card_number = None
        self.pin_number = None
        self.menu_selection = None
        self.connection = sqlite3.connect('card.s3db')
        self.connection.execute(CREATE_CARD_TABLE)

    MAIN_MENU_PROMPT = """1. Create an Account
2. Log into an Account
0. Exit \n"""

    ACCOUNT_MENU_PROMPT = """1. Balance
2. Add income
3. Do transfer
4. Close Account
5. Log out
0. Exit \n"""

    def get_card_from_pin(self, pin):
        return self.connection.execute(GET_CARD_BY_PIN, (pin,)).fetchone()

    def get_pin_from_card(self, number):
        return self.connection.execute(GET_PIN_BY_CARD, (number,)).fetchone()

    def get_balance_by_card_number(self, number):
        return self.connection.execute(GET_BALANCE_BY_NUMBER, (number,)).fetchone()

    def delete_card(self, number):
        return self.connection.execute(DELETE_CARD, (number,))

    def update_card_balance(self, amount, number):
        return self.connection.execute(UPDATE_CARD_BALANCE, (amount, number))

    def get_all_card_numbers(self):
        return self.connection.execute(GET_ALL_CARD_NUMBERS).fetchall()

    def create_new_account_info(self):
        issuer_identification_number = "400000"
        customer_account_number = format(random.randint(0000000000, 9999999999), '010d')
        self.credit_card_number = issuer_identification_number + str(customer_account_number)
        self.pin_number = format(random.randint(0000, 9999), '04d')

    def luhn_algorithm(self):
        control_number_list = [int(x) for x in self.credit_card_number]
        control_number_list.pop()
        control_number_list = [x * 2 if i % 2 == 0 else x for i, x in enumerate(control_number_list)]

        i = 0
        for x in control_number_list:
            if x > 9:
                control_number_list[i] = x - 9
                i += 1
            else:
                control_number_list[i] = x
                i += 1

        control_number = sum(control_number_list)
        control_number_remainder = control_number % 10

        if control_number_remainder != 0:
            credit_card_last_digit_checksum = str(10 - control_number_remainder)
        else:
            credit_card_last_digit_checksum = str(0)

        credit_card_number_list = list(self.credit_card_number)
        credit_card_number_list.pop()
        new_credit_card_number = ''.join(credit_card_number_list)
        self.credit_card_number = new_credit_card_number + credit_card_last_digit_checksum

    def create_account(self):
        self.create_new_account_info()
        self.luhn_algorithm()
        print(f"\n"
              f"Your card has been created\n"
              f"Your card number:\n"
              f"{self.credit_card_number}\n"
              f"Your card PIN:\n"
              f"{self.pin_number}\n")

        self.connection.execute(INSERT_CARD, (self.credit_card_number, self.pin_number))
        self.connection.commit()

    def log_into_account(self):
        credit_card_number_entered = str(input("\n""Enter your card number""\n"))
        pin_number_entered = str(input("Enter your PIN""\n"))
        self.check_user_account_login_info(credit_card_number_entered, pin_number_entered)

    def check_user_account_login_info(self, user_entered_credit_card_number, user_entered_pin_number):
        card_from_pin = self.get_card_from_pin(user_entered_pin_number)
        pin_from_card = self.get_pin_from_card(user_entered_credit_card_number)

        if card_from_pin is None or pin_from_card is None:
            print("\n""Wrong card number or PIN!""\n")
        elif card_from_pin[0] != user_entered_credit_card_number or pin_from_card[0] != user_entered_pin_number:
            print("\n""Wrong card number or PIN!""\n")
        else:
            accepted_credit_card_number = card_from_pin[0]
            print("\n""You have successfully logged in!""\n")
            self.account_menu(accepted_credit_card_number)

    def add_money_to_account(self, credit_card_number):
        print("\n""Enter income:")
        income_amount = int(input())
        credit_card_balance = self.get_balance_by_card_number(credit_card_number)[0]
        self.update_card_balance(income_amount + credit_card_balance, credit_card_number)
        self.connection.commit()
        print("Income was added!""\n")

    def transfer_money_to_another_account(self, credit_card_number):
        print("\n""Transfer")
        transfer_credit_card_number = str(input("Enter card number:""\n"))
        self.credit_card_number = transfer_credit_card_number
        all_card_numbers = self.get_all_card_numbers()

        all_card_list = []
        for card in all_card_numbers:
            all_card_list.append(card[0])

        self.luhn_algorithm()

        if transfer_credit_card_number != self.credit_card_number:
            print("Probably you made a mistake in the card number. Please try again!""\n")
        elif transfer_credit_card_number not in all_card_list:
            print("Such a card does not exist""\n")
        else:
            transfer_amount = int(input("Enter how much money you want to transfer:""\n"))
            credit_card_balance = self.get_balance_by_card_number(credit_card_number)[0]

            if credit_card_balance - transfer_amount < 0:
                print("Not enough money!""\n")

            else:
                transfer_credit_card_balance = self.get_balance_by_card_number(transfer_credit_card_number)[0]
                self.update_card_balance(transfer_amount + transfer_credit_card_balance,
                                         transfer_credit_card_number)
                self.update_card_balance(credit_card_balance - transfer_amount, credit_card_number)
                self.connection.commit()
                print("Success!""\n")

    def delete_account(self, credit_card_number):
        self.delete_card(credit_card_number)
        self.connection.commit()
        print("\n""The account has been closed!""\n")

    def main_menu(self):
        while True:
            self.menu_selection = input(self.MAIN_MENU_PROMPT)

            if self.menu_selection == '1':
                self.create_account()

            elif self.menu_selection == '2':
                self.log_into_account()

            elif self.menu_selection == '0':
                print("\n""Bye!")
                exit()

            else:
                print("\nUnknown option.\n")

    def account_menu(self, accepted_credit_card_number):
        while True:
            self.menu_selection = input(self.ACCOUNT_MENU_PROMPT)

            if self.menu_selection == '1':
                balance = self.get_balance_by_card_number(accepted_credit_card_number)[0]
                print(f"\nBalance: {balance}\n")

            elif self.menu_selection == '2':
                self.add_money_to_account(accepted_credit_card_number)

            elif self.menu_selection == '3':
                self.transfer_money_to_another_account(accepted_credit_card_number)

            elif self.menu_selection == '4':
                self.delete_account(accepted_credit_card_number)
                break

            elif self.menu_selection == '5':
                print("\n""You have successfully logged out!""\n")
                break

            elif self.menu_selection == '0':
                print("\n""Bye!")
                exit()

            else:
                print("\nUnknown option.\n")


BankingSystem().main_menu()
