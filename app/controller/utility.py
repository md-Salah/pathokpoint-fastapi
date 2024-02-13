import slugify as slg

def slugify(name):
    return slg.slugify(name).replace('aa', 'a').replace('ii', 'i')

