class Todo:
    channel: str
    id: str
    title: str
    link_s3: str

    def __init__(self, **kwargs):
        self.channel = kwargs.get("channel")
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.link_s3 = kwargs.get("link_s3")        