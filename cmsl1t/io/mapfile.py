

def full_path_alias(path, objName):
    # path includes treeName
    tokens = path.split('/')
    tokens += objName.split('.')
    return 'event.' + '_'.join(tokens)


def default_alias(path, treeName, objName):
    tokens = []
    if 'emu' in path.lower():
        tokens.append('emu')
    tokens.append(treeName)
    tokens += objName.split('.')
    return 'event.' + '_'.join(tokens)


def shorthand_alias(path, treeName, objName):
    tokens = []
    if 'emu' in path.lower():
        tokens.append('emu')

    search_for = ['bmt', 'emt', 'omt']
    obj_lower = objName.lower()
    for s in search_for:
        if s in obj_lower:
            tokens.append(s)
    if 'event' in obj_lower:
        tokens.append(objName.split('.')[-1])
    else:
        tokens += objName.split('.')[-2:]

    return 'event.' + '_'.join(tokens)
