def with_properties(properties):
    return {
        'type': 'object',
        'inclusion': 'available',
        'selected-by-default': False,
        'properties': properties
    }
