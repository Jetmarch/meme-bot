class Stat:
    def __init__(self, max_amount, current_amount = 0) -> None:
        self.max = max_amount
        if current_amount == 0:
            self.current = max_amount
        else:
            self.current = current_amount

    def change(self, value) -> None:
        if self.current == self.max and value > 0:
            return
        
        self.current += value

    def restore(self) -> None:
        self.current = self.max