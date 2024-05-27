class Person():
    name = 'lal'
    age = None
    height = None
    weight = None
    city = None
    country = None
    
# Check if all attributes are set or None
if any([getattr(Person, attr) for attr in dir(Person) if not attr.startswith('__')]):    
    print('Any of the attributes are not None')
else:
    print('All attributes are None')
    