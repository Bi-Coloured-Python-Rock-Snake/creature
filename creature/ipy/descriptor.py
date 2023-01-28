from dataclasses import dataclass


@dataclass
class Overridable:
    name: str
    value: object = None

    def __get__(self, instance, owner):
        if not instance:
            return self
        if self.value is not None:
            return self.value
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value



if __name__ == '__main__':
    @dataclass
    class C:
        x: int = 1

    C.x = Overridable(name='x')

    ob = C()

    assert ob.x == 1
    C.x.value = 5
    assert ob.x == 5