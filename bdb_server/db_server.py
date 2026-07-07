import Pyro5.api
from bdb_server.database import Database

# Defaults
OBJECT_ID = "bdb"
HOST = "localhost"
PORT = 9001

DB_PATH = "bdb_server/data/bank.db"

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class BDBServer:
    def __init__(self):
        self.db = Database(DB_PATH)
        self.db.seed()


    def balance(self, account_id):
        return self.db.balance(account_id)

    def status(self, transfer_id):
        return self.db.status(transfer_id)

    def transfer(self, transfer_id, sender_id, recipient_id, amount_cents, fee_cents, reference=None):
        return self.db.transfer(transfer_id, sender_id, recipient_id, amount_cents, fee_cents, reference)

    def get_user(self, username):
        return self.db.get_user(username)


def main():
    daemon = Pyro5.api.Daemon(host=HOST, port=PORT)
    uri = daemon.register(BDBServer(), objectId=OBJECT_ID)
    print(f"Database server running on {uri}")
    daemon.requestLoop()


if __name__ == "__main__":
    main()
