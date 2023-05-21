from dataclasses import dataclass
from typing import List


# NOT WORKING

class Todo_download:
    displayname : str
    url : str
    links : List[str]
    todos : List[str]

    def __init__(self):
        return