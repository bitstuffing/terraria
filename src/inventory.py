
class Inventory:

    def __init__(self, slots):
        self.slots = slots
        self.items = [None] * slots
        self.selected_slot = 0
