
class BaseFilter:
    def pop(self, key, default=None):
        return self.__dict__.pop(key, default)
