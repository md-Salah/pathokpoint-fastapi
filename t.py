def detach_image(*kwargs):
    _list = [x for x in kwargs if x is not None]
    
    print(_list)
    
detach_image('valid-uuid4', 'valid-uuid4')
detach_image(None, 'valid-uuid4')
detach_image(None, None)