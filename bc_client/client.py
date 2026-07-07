import uuid
from bc_client.inputter import input_amount, input_notempty
import Pyro5.client


# BAS Server Defaults
OBJECT_ID = "bas"
HOST = "localhost"
PORT = 9000

URI = f"PYRO:{OBJECT_ID}@{HOST}:{PORT}"

HEADER = ("\n============================================"
         +"\n===============  THE BANK!!  ==============="
         +"\n============================================")


def connect():
    uri = f"PYRO:{OBJECT_ID}@{HOST}:{PORT}"
    return Pyro5.client.Proxy(uri)


def format_cents(amount):
    dollars = amount // 100
    cents = amount % 100
    return f"${dollars:,}.{cents:02d}"


def ping(server):
    if server.ping():
        print("Pinged.")


def login(server):
    while True:
        print(HEADER)
        print("Enter username and password below")
        username = input("  Username: ")
        password = input("  Password: ")
        result = server.login(username, password)

        if result["success"]:
            return result["session_id"], username
        print(f"{result['error']}")


def make_transfer(server, session_id):
    recipient = input_notempty("Enter recipients account ID")
    amount_cents= input_amount("Amount: $")
    reference = input("  Reference (optional)").strip()

    transfer_id = str(uuid.uuid4())

    result = server.transfer(session_id, transfer_id, recipient, amount_cents, reference)

    transfer = result["transfer"]
    if transfer["status"] == "COMPLETED":
        print("  Transfer COMPLETED")
        print(f"  Sent: {format_cents(transfer['amount_cents'])}")
        print(f"  Fee:  {format_cents(transfer['fee_cents'])}")
        print(f"  Transfer ID: {transfer_id}")
    else:
        print(f"\n  Transfer ({transfer['status']})")

    input("Press Enter to continue.")


def check_status(server, session_id):
    transfer_id = input_notempty("  Transfer ID: ")
    result = server.status(session_id, transfer_id)

    if not result["success"]:
        print(f"\n  {result['error']}")
        return

    trans_result = result["transfer"]
    print(f"\n  Status:    {trans_result['status']}")
    print(f"  Amount:    {format_cents(trans_result['amount_cents'])}")
    print(f"  Fee:       {format_cents(trans_result['fee_cents'])}")
    if trans_result["reference"]:
        print(f"  Reference: {trans_result['reference']}")
    else:
        print("  Reference: (none)")

    input("Press Enter to continue.")


def main():
    basserver = connect()

    # Log in
    while True:
        session_id, username = login(basserver)

        # Menu Loop
        while True:
            print(HEADER)
            print(f"Welcome, {username}! How can we help you today? \n")
            print("   1. Check Balance")
            print("   2. Transfer Funds")
            print("   3. Transfer Status")
            print("   0. Logout")

            choice = input("\n > ").strip()

            if choice == "0":
                # Log out
                basserver.logout(session_id)
                break
            elif choice == "1":
                # Balance
                result = basserver.balance(session_id)
                print(f"\n  Balance: {format_cents(result['balance_cents'])}")
                input("Press Enter to continue.")

            elif choice == "2":
                # Transfer
                make_transfer(basserver, session_id)
            elif choice == "3":
                # Status
                check_status(basserver, session_id)
            else:
                print("  Ooops, please try again")

            if not basserver.validate_session(session_id):
                print("\n  Session expired. Please login again.")
                break

        print("  Logged out.\n")


if __name__ == "__main__":
    main()
