class FooError(Exception):
    def __init__(self, source, message, junk=None, mojunk=None, sumting=None):
        self.source = source
        self.message = message

        if sumting is not None:
            if not junk and not mojunk:
                print(sumting.test)


class Foo:
    def __init__(self):
        self.test = self.bar()
        self.connect()

    def bar(self):
        print('worked')

    def connect(self):
        try:
            False
        except FooError:
            raise FooError('Foo->connect()', 'Failed to connect', sumting=self)


if __name__ == '__main__':
    x = Foo()
