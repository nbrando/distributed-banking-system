class Menu:
    def __init__(self, title="Menu"):
        self.title = title
        self.options = []   # list of (label, callback)

    def add(self, label, callback):
        self.options.append((label, callback))

    def run(self):
        while True:
            print(f"\n--- {self.title} ---")
            for i, (label, _) in enumerate(self.options, 1):
                print(f"  {i}. {label}")
            print(f"  0. Exit")

            choice = input("> ").strip()

            if choice == "0":
                print("Goodbye.")
                break

            try:
                index = int(choice) - 1
                if 0 <= index < len(self.options):
                    self.options[index][1]()  # call the callback
                else:
                    print("Invalid option.")
            except ValueError:
                print("Invalid option.")