class Splitted:
    relative_path = str
    duration = int

    def __init__(self, **kwargs):
        self.relative_path = kwargs.get("relative_path")
        self.duration = kwargs.get("duration")

    def __str__(self):
        return f"({self.relative_path}, duration={self.duration})"