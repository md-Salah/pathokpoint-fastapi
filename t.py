class User():
    name = 'salah uddin'

    @classmethod
    def get_user(cls, name):
        return name
    
    @property
    def get_name(self):
        return self.name
    
print(User.get_name) # salah