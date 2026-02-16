class DistractionBlocker:
    def __init__(self, shared_state):
        self.shared = shared_state

    def run(self):
        pass

    def get_active_window_title(self):
        pass

    def is_distraction(self, window_title):
        pass

    def handle_distraction(self, window_title):
        pass

    def block_app(self, window_title):
        pass
