"""Generic mock data generator for Singer tap integration tests.

Generates mock API response data from inline schema definitions with
deterministic, type-conformant values.
"""
from datetime import datetime, timedelta


class MockDataGenerator:
    """Generates mock records from stream class schemas.

    Usage::

        gen = MockDataGenerator()
        record = gen.generate_record(stream_cls, seed=0)
        records = gen.generate_records(stream_cls, count=3)
    """

    BASE_DATE = datetime(2024, 6, 15, 10, 0, 0)

    @staticmethod
    def resolve_type(type_spec):
        """Return the first non-null type from a JSON-Schema *type* field."""
        if isinstance(type_spec, list):
            for t in type_spec:
                if t != 'null':
                    return t
            return 'string'
        return type_spec

    @classmethod
    def generate_value(cls, field_name, field_schema, seed=0):
        """Return a deterministic value that conforms to *field_schema*."""
        type_str = cls.resolve_type(field_schema.get('type', 'string'))
        fmt = field_schema.get('format')

        if fmt == 'date-time':
            dt = cls.BASE_DATE + timedelta(days=seed)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        if type_str == 'string':
            return f"mock-{field_name.lower()}-{seed}"
        if type_str == 'number':
            return round(42.5 + seed * 1.1, 2)
        if type_str == 'integer':
            return 100 + seed
        if type_str == 'boolean':
            return seed % 2 == 0
        if type_str == 'array':
            return []
        if type_str == 'object':
            props = field_schema.get('properties', {})
            if props:
                obj = {}
                for k, v in props.items():
                    obj[k] = cls.generate_value(k, v, seed)
                return obj
            return {}
        return f"mock-{seed}"

    @classmethod
    def generate_record(cls, stream_cls, seed=0, exclude_fields=None):
        """Generate one mock record for a stream class from its SCHEMA."""
        schema = stream_cls.SCHEMA
        record = {}
        exclude = exclude_fields or set()
        for field_name, field_schema in schema.get('properties', {}).items():
            if field_name in exclude:
                continue
            record[field_name] = cls.generate_value(field_name, field_schema, seed)
        return record

    @classmethod
    def generate_records(cls, stream_cls, count=1, base_seed=0,
                         exclude_fields=None):
        """Generate *count* mock records with incrementing seeds."""
        return [
            cls.generate_record(stream_cls, seed=base_seed + i,
                                exclude_fields=exclude_fields)
            for i in range(count)
        ]

    @staticmethod
    def wrap_paginated(records, table_name, cursor=None, total_pages=1):
        """Wrap *records* in a Uservoice-style paginated response.

        Matches the format::

            {<table>: [...], pagination: {cursor: ..., total_pages: N}}
        """
        return {
            table_name: records,
            "pagination": {
                "cursor": cursor,
                "total_pages": total_pages,
            },
        }
