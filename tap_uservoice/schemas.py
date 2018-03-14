from funcy import merge


def with_properties(properties, additional=False):
    return {
        'type': 'object',
        'inclusion': 'available',
        'selected-by-default': False,
        'properties': properties,
        'additionalProperties': additional
    }


def make_date_field(name):
    return {
        name: {
            "type": ["null", "string"],
            "format": "date-time"
        }
    }


DEFAULT_DATE_FIELDS = merge(
    make_date_field('created_at'),
    make_date_field('updated_at'))
