class AvgRenderTimer:
    def __init__(self, size: int) -> None:
        self.__list = []
        self.__size = size
        self.__idx = 0
        self.__avg = -1.0

    def add(self, item: float):
        if len(self.__list) < self.__size:
            self.__list.append(item)
        else:
            self.__list[self.__idx] = item
        self.__avg = sum(self.__list) / len(self.__list)
        self.__idx += 1
        self.__idx %= self.__size

    def avg(self) -> float:
        return self.__avg

    def __repr__(self) -> str:
        return str(self.__list)