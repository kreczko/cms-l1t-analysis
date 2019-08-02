

class DummyEvent(dict):

    def __init__(self, **kwargs):
        super(DummyEvent, self).update(kwargs)

    def __getattribute__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value
