

class UI:
    def __init__(self):
        self.window = None

    def create_window(self):
        self.window = "New Window Created"

    def display(self):
        if self.window:
            return self.window
        return "No Window Created"