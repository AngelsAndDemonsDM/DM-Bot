from enum import auto, enum


class DiscordColorEnum(enum):
    """
        0 - тёмно серый
        1 - красный
        2 - зелёный
        3 - жёлтый
        4 - синий
        5 - розовый
        6 - бирюзовый
        7 - белый 
    """
    DARK_GREY = auto()
    RED = auto()
    GREEN = auto()
    YELLOW = auto()
    BLUE = auto()
    PINK = auto()
    TEAL = auto()
    WHITE = auto()

class DiscordColorManager:
    def __init__(self):
        pass

    def get_color(self, text: str, color: DiscordColorEnum):
        if color == DiscordColorEnum.DARK_GREY:
            return f"[2;30m{text}[0m"
        elif color == DiscordColorEnum.RED:
            return f"[2;31m{text}[0m"
        elif color == DiscordColorEnum.GREEN:
            return f"[2;32m{text}[0m"
        elif color == DiscordColorEnum.YELLOW:
            return f"[2;33m{text}[0m"
        elif color == DiscordColorEnum.BLUE:
            return f"[2;34m{text}[0m"
        elif color == DiscordColorEnum.PINK:
            return f"[2;35m{text}[0m"
        elif color == DiscordColorEnum.TEAL:
            return f"[2;36m{text}[0m"
        elif color == DiscordColorEnum.WHITE:
            return f"[2;37m{text}[0m"
