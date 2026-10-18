from utils.singleton_meta import SingletonMeta


class _Counter(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.value: int = 0


class _OtherCounter(metaclass=SingletonMeta):
    pass


class TestSingletonMeta:
    def test_returns_the_same_instance(self) -> None:
        first = _Counter()
        first.value += 1

        assert _Counter() is first
        assert _Counter().value == 1

    def test_keeps_one_instance_per_class(self) -> None:
        assert _Counter() is not _OtherCounter()
