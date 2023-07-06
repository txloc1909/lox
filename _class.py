from dataclasses import dataclass


@dataclass
class LoxClass:
    name: str

    def __repr__(self):
        return self.name
