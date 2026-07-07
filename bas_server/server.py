import Pyro5.api
from datetime import datetime, timedelta

from bas_server.fee_calculator import calculate_fee
from bas_server.auth import verify_password, SessionManager

# This Server Defaults
OBJECT_ID = "bas"
HOST = "localhost"
PORT = 9000

# Database Server Defaults
BDB_ID = "bdb"
BDB_HOST = "localhost"
BDB_PORT = 9001

BDB_URI = f"PYRO:{BDB_ID}@{BDB_HOST}:{BDB_PORT}"


def connect_bdb():
    return Pyro5.api.Proxy(BDB_URI)


@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class BASServer(object):
    def __init__(self):
        self.sessions = SessionManager()
        self.ping_count = 0

    def login(self, username, password):
        bdb = connect_bdb()
        user = bdb.get_user(username)

        if user and verify_password(password, user["pwhash"]):
            session_id = self.sessions.create(user["account_id"])
            little_log("AUTH", f"Login success: {username}")
            return {"success": True, "session_id": session_id}

        else:
            little_log("AUTH", f"Login failed: {username}")
            return {"success": False, "error": "Failed Login"}

    def logout(self, session_id):
        user_id = self.sessions.validate(session_id)
        self.sessions.terminate(session_id)
        little_log("AUTH", f"Logout: user {user_id}")
        return {"success": True}

    def validate_session(self, session_id):
        return self.sessions.validate(session_id) is not None

    def ping(self):
        self.ping_count += 1
        little_log("PING", f"Ping #{self.ping_count}")
        return True

    def balance(self, session_id):
        # Authenticate
        user_id = self.sessions.validate(session_id)
        if not user_id:
            little_log("AUTH", "Invalid session ID (balance)")
            return {"success": False, "error": "Invalid session"}

        bdb = connect_bdb()
        balance_cents = bdb.balance(user_id)
        little_log("BALN", f"Balance check: user{user_id}")
        return {"success": True, "balance_cents": balance_cents}

    def transfer(self, session_id, transfer_id, recipient_id, amount_cents, reference=None):
        # Authenticate
        user_id = self.sessions.validate(session_id)
        if not user_id:
            little_log("AUTH", "Invalid session ID (transfer)")
            return {"success": False, "error": "Invalid session"}

        # Validate
        if not isinstance(amount_cents, int) or amount_cents <= 0:
            little_log("TRAN", f"Fail: invalid amount user{user_id}")
            return {"success": False, "error": "Invalid amount. Must be positive number"}
        if recipient_id == user_id:
            little_log("TRAN", f"Fail: self transfer user{user_id}")
            return {"success": False, "error": "Can't send yourself money, silly goose."}

        # Calculate
        fee = calculate_fee(amount_cents)
        little_log("TRAN", f"Submitted: user{user_id} Transfer ID: XXXX-{transfer_id[-6:]}")

        # Communicate (Ha! All the -ates.)
        bdb = connect_bdb()
        result = bdb.transfer(transfer_id, user_id, recipient_id, amount_cents, fee, reference)
        little_log("TRAN", f"Result: {result['status']} Transfer ID: XXXX-{transfer_id[-6:]}")

        return {"success": True, "transfer": result}


    def status(self, session_id, transfer_id):
        # Authenticate
        user_id = self.sessions.validate(session_id)
        if not user_id:
            little_log("AUTH", "Invalid session ID (status)")
            return {"success": False, "error": "Invalid session"}

        bdb = connect_bdb()
        transfer = bdb.status(transfer_id)

        if not transfer:
            little_log("STAT", f" Transfer not found: XXXX-{transfer_id[-6:]}")
            return {"success": False, "error": "Transfer doesnt exist"}

        # Dont show transfers of other people
        if transfer["sender_id"] != user_id and transfer["recipient_id"] != user_id:
            little_log("STAT", f" Transfer not found (unauthorised): XXXX-{transfer_id[-6:]}")
            return {"success": False, "error": "Transfer doesnt exist"}


        little_log("STAT", f"user{user_id} Transfer: XXXX-{transfer_id[-6:]}")
        return {"success": True, "transfer": transfer}


def little_log(component, msg):
    tstamp = datetime.now() - timedelta(days=3, hours=2)
    print(f"{tstamp} [{component}] {msg}")


def main():
    daemon = Pyro5.api.Daemon(host=HOST, port=PORT)
    uri = daemon.register(BASServer(), objectId=OBJECT_ID)
    little_log("BAS", f"Server running on {uri}")
    daemon.requestLoop()


if __name__ == "__main__":
    main()
