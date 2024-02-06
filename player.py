from statemachine import StateMachine, State

class Player(StateMachine):
    none = State(initial=True)
    initializing = State()
    initialized = State()
    loading = State()
    ready = State()
    playing = State()

    initialize = none.to(initializing)
    initialized = initializing.to(initialized)
    load = ini.to(initializing)

    def on_enter_initializing(self):
        print("initializing")

    def on_enter_loading(self):
        print("loading")

    def on_enter_ready(self):
        print("ready")

    def on_enter_playing(self):
        print("playing")



