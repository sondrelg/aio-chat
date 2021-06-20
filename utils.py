class FixedLengthList(list):
    """
    List that pops the oldest input if it gets above a certain max length.
    """
    def __init__(self, seq=(), *, max_length: int) -> None:
        self._max_length = max_length
        super().__init__(seq)

    def append(self, *args, **kwargs):
        if len(self) == self._max_length - 1:
            del self[0]
        super().append(*args, **kwargs)

