from threading import Event


class OrEvent:
    def __init__(self):
        self.or_event = Event()
        self.events = self.initialize_events()
        for e in self.events:
            self.add_event_to_disjunction(e)
        self.update_on_change()

    def initialize_events(self) -> list:
        pass

    def get_events(self):
        return self.events

    def wait(self, timeout=None):
        self.or_event.wait(timeout=timeout)

    def update_on_change(self):
        is_sets = [e.is_set() for e in self.events]
        if any(is_sets):
            self.or_event.set()
        else:
            self.or_event.clear()

    def or_set(self, e):
        e._set()
        self.update_on_change()

    def or_clear(self, e):
        e._clear()
        self.update_on_change()

    def add_event_to_disjunction(self, e):
        e._set = e.set
        e._clear = e.clear
        e.changed = self.update_on_change
        e.set = lambda: OrEvent.or_set(self, e)
        e.clear = lambda: OrEvent.or_clear(self, e)


class OrEventPair(OrEvent):
    def initialize_events(self) -> list:
        return [Event(), Event()]