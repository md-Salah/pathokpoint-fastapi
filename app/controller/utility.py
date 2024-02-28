import slugify as slg

def slugify(text):
    """_summary_

    Args:
        text (str): any text (e.g. 'Hello World', 'আমার সোনার বাংলা')

    Returns:
        str: Lower case english slug (e.g. 'hello-world', 'amar-sonar-bangla')
    """    
    return slg.slugify(text).replace('aa', 'a').replace('ii', 'i').replace('ea', 'o')

