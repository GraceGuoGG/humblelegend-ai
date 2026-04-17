class BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Field:
    def __init__(self, default=None, **kwargs):
        self.default = default