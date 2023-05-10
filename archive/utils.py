class Alias:
    """Descriptor to add aliases to class variables.

    Usage:
    ```py
    class Foo:
        x: int
        y = Alias("x") # y is now an alias of x.
    ```

    """

    def __init__(self, name: str):
        self.name = name

    def __get__(self, obj, _=None):
        return getattr(obj, self.name)
