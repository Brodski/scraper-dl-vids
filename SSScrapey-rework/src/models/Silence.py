class Silence:
    def __init__(self):
        
        self.start = None
        self.end = None
        self.duration = None
    
    def __str__(self):
        return f"(start={self.start}, end={self.end}, duration={self.duration})"
    
    # "<" is all that is needed by bisect, consider @total_ordering for <, <=, >, >=, ==, and !=
    def __lt__(self, other):
        return self.start < other.start
