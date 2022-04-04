class Column:
    def __init__(self, data_type: type, nullable: bool = False, primary_key: bool = False, value=None, default=None):
        self.data_type = data_type
        self.nullable = nullable
        self.primary_key = primary_key
        self.default = default
        if default is not None and value is None:
            self.value = default
        else:
            self.value = value

    def set(self, value):
        if self.default is not None and value is None:
            self.value = self.default
        else:
            self.value = value