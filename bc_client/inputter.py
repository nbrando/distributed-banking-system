from decimal import Decimal, InvalidOperation


def input_amount(msg):
    while True:
        amt = input(f"  {msg}").strip()
        try:
            amount_cents = int(Decimal(amt) * 100)
        except (ValueError, InvalidOperation):
            print("  Please enter a valid number")
            continue
        if amount_cents <= 0:
            print("  Please enter a number greater than zero")
            continue
        return amount_cents


def input_notempty(msg):
    while True:
        value = input(f"  {msg}: ").strip()
        if value:
            return value
        print(f"  {msg} cannot be empty.")