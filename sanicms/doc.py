from collections import defaultdict
from datetime import date, datetime
from peewee import ModelBase
from playhouse.postgres_ext import ArrayField
import logging

logger = logging.getLogger('sanic')

class Field:
    def __init__(self, description=None, required=None, name=None):
        self.name = name
        self.description = description
        self.required = required

    def serialize(self):
        output = {}
        if self.name:
            output['name'] = self.name
        if self.description:
            output['description'] = self.description
        if self.required is not None:
            output['required'] = self.required
        return output


class Integer(Field):
    def serialize(self):
        return {
            "type": "integer",
            "format": "int64",
            **super().serialize()
        }


class String(Field):
    def serialize(self):
        return {
            "type": "string",
            **super().serialize()
        }


class Boolean(Field):
    def serialize(self):
        return {
            "type": "boolean",
            **super().serialize()
        }


class Tuple(Field):
    pass


class Date(Field):
    def serialize(self):
        return {
            "type": "date",
            **super().serialize()
        }


class DateTime(Field):
    def serialize(self):
        return {
            "type": "dateTime",
            **super().serialize()
        }


class Dictionary(Field):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields or {}
        super().__init__(**kwargs)

    def serialize(self):
        return {
            "type": "object",
            "properties": {key: serialize_schema(schema) for key, schema in self.fields.items()},
            **super().serialize()
        }


class List(Field):
    def __init__(self, items=None, *args, **kwargs):
        self.items = items or []
        if type(self.items) is not list:
            self.items = [self.items]
        super().__init__(*args, **kwargs)

    def serialize(self):
        if len(self.items) > 1:
            items = Tuple(self.items).serialize()
        elif self.items:
            items = serialize_schema(self.items[0])
        return {
            "type": "array",
            "items": items
        }


definitions = {}


class Object(Field):
    def __init__(self, cls, *args, object_name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.cls = cls
        self.object_name = object_name or cls.__name__

        if self.cls not in definitions:
            definitions[self.cls] = (self, self.definition)

    @property
    def definition(self):
        return {
            "type": "object",
            "properties": {
                key: serialize_schema(schema)
                for key, schema in self.cls.__dict__.items()
                if not key.startswith("_")
                },
            **super().serialize()
        }

    def serialize(self):
        return {
            #"type": "object",
            #"schema": {
            #    "$ref": "#/definitions/{}".format(self.object_name)
            #},
            "$ref": "#/definitions/{}".format(self.object_name),
            **super().serialize()
        }

class PeeweeObject(Field):
    def __init__(self, cls, *args, object_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cls = cls
        self.object_name = object_name or cls.__name__

        if self.cls not in definitions:
            definitions[self, cls] = (self, self.definition)

    @property
    def definition(self):
        return {
            'type': 'object',
            'properties': {
                value.field.column_name if value.field.column_name else key: self.field_serialize(value)
                for key, value in self.cls.__dict__.items()
                if not key.startswith('_') and key != 'DoesNotExist'
            },
            **super().serialize()
        }

    def db_field_serialize(self, ttype, desc=None, format=None, related=None):
        if related:
            schema_type = type(related)
            if issubclass(schema_type, ModelBase):
                return PeeweeObject(related).serialize()
            if schema_type is type:
                if ttype == 'array': return List(related).serialize()
                if ttype == 'json': return Dictionary(related).serialize()
                return Object(related).serialize()
        else:
            value = {'type': ttype}
            if desc: value.update({'description': desc})
            if format: value.update({'format': format})
            return value

    def field_serialize(self, schema):
        print(schema)
        field = schema.field
        db_field = field.field_type
        print(field)
        if isinstance(field, ArrayField):
            return self.db_field_serialize('array', field.verbose_name, None,
                                           field.help_text)
        elif db_field == 'DEFAULT':
            return self.db_field_serialize('string', field.verbose_name, None,
                                           field.help_text)
        elif db_field == 'INT':
            if hasattr(field, 'rel_model'):
                return self.db_field_serialize('integer', field.verbose_name,
                                               None, field.rel_model)
            return self.db_field_serialize('integer', field.verbose_name, None,
                                           field.help_text)
        elif db_field == 'BIGINT':
            return self.db_field_serialize('integer', field.verbose_name,
                                           'int64', field.help_text)
        elif db_field == 'SMALLINT':
            return self.db_field_serialize('integer', field.verbose_name,
                                           'int', field.help_text)
        elif db_field == 'AUTO':
            return self.db_field_serialize('integer', field.verbose_name,
                                           'int', field.help_text)
        elif db_field == 'FLOAT':
            return self.db_field_serialize('number', field.verbose_name,
                                           'float', field.help_text)
        elif db_field == 'DOUBLE':
            return self.db_field_serialize('number', field.verbose_name,
                                           'double', field.help_text)
        elif db_field == 'DECIMAL':
            return self.db_field_serialize('number', field.verbose_name,
                                           None, field.help_text)
        elif db_field == 'VARCHAR' or db_field == 'CHAR' or db_field == "TEXT":
            return self.db_field_serialize('string', field.verbose_name,
                                           None, field.help_text)
        elif db_field == 'UUID':
            return self.db_field_serialize('string', field.verbose_name,
                                           'uuid', field.help_text)
        elif db_field == 'BLOB':
            return self.db_field_serialize('string', field.verbose_name,
                                           'binary', field.help_text)
        elif db_field == 'DATETIME':
            return self.db_field_serialize('string', field.verbose_name,
                                           'date-time', field.help_text)
        elif db_field == 'DATE':
            return self.db_field_serialize('string', field.verbose_name,
                                           'date', field.help_text)
        elif db_field == 'TIME':
            return self.db_field_serialize('string', field.verbose_name,
                                           'date-time', field.help_text)
        elif db_field == 'BOOL':
            return self.db_field_serialize('boolean', field.verbose_name, None,
                                           field.help_text)
        elif db_field == 'JSON' or db_field == 'JSONB':
            return self.db_field_serialize('object', field.verbose_name, None,
                                           field.help_text)

    def serialize(self):
        return {
            "$ref": "#/definitions/{}".format(self.object_name),
            **super().serialize()
        }

def serialize_schema(schema):
    schema_type = type(schema)
    print(schema_type)
    # --------------------------------------------------------------- #
    # Class
    # --------------------------------------------------------------- #
    if schema_type is type:
        if issubclass(schema, Field):
            return schema().serialize()
        elif schema is dict:
            return Dictionary().serialize()
        elif schema is list:
            return List().serialize()
        elif schema is int:
            return Integer().serialize()
        elif schema is str:
            return String().serialize()
        elif schema is bool:
            return Boolean().serialize()
        elif schema is date:
            return Date().serialize()
        elif schema is datetime:
            return DateTime().serialize()
        else:
            return Object(schema).serialize()

    # --------------------------------------------------------------- #
    # Object
    # --------------------------------------------------------------- #
    else:
        if issubclass(schema_type, ModelBase):
            return PeeweeObject(schema).serialize()
        elif issubclass(schema_type, Field):
            return schema.serialize()
        elif schema_type is dict:
            return Dictionary(schema).serialize()
        elif schema_type is list:
            return List(schema).serialize()

    return {}


# --------------------------------------------------------------- #
# Route Documenters
# --------------------------------------------------------------- #


class RouteSpec:
    consumes = None
    consumes_content_type = None
    produces = None
    produces_content_type = None
    summary = None
    description = None
    operation = None
    blueprint = None
    tags = None

    def __init__(self):
        self.tags = []
        super().__init__()


route_specs = defaultdict(RouteSpec)


def route(summary=None, description=None, consumes=None, produces=None,
          consumes_content_type=None, produces_content_type=None):
    def inner(func):
        route_spec = route_specs[func]

        if summary is not None:
            route_spec.summary = summary
        if description is not None:
            route_spec.description = description
        if consumes is not None:
            route_spec.consumes = consumes
        if produces is not None:
            route_spec.produces = produces
        if consumes_content_type is not None:
            route_spec.consumes_content_type = consumes_content_type
        if produces_content_type is not None:
            route_spec.produces_content_type = produces_content_type

        return func
    return inner


def summary(text):
    def inner(func):
        route_specs[func].summary = text
        return func
    return inner


def description(text):
    def inner(func):
        route_specs[func].description = text
        return func
    return inner


def consumes(*args, content_type=None):
    def inner(func):
        if args:
            route_specs[func].consumes = args[0] if len(args) == 1 else args
            route_specs[func].consumes_content_type = content_type
        return func
    return inner


def produces(*args, content_type=None):
    def inner(func):
        if args:
            route_specs[func].produces = args[0] if len(args) == 1 else args
            route_specs[func].produces_content_type = content_type
        return func
    return inner


def tag(name):
    def inner(func):
        route_specs[func].tags.append(name)
        return func
    return inner
