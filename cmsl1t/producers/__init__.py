

def _init_values(inputs, event):
    values = {}
    for name, attr in inputs.items():
        values[name] = event[attr]
    return values
