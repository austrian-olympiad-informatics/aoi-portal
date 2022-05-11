import functools
from typing import Union

import voluptuous as vol  # type: ignore
from flask import Response, jsonify, request
from voluptuous.humanize import humanize_error  # type: ignore
from werkzeug.exceptions import BadRequest

SchemaType = Union[vol.Schema, list, dict]


def json_request(schema: SchemaType):
    if not isinstance(schema, vol.Schema):
        schema = vol.Schema(schema)

    def decorator(fn):
        @functools.wraps(fn)
        def patched(*args, **kwargs):
            request_data = request.json
            try:
                data = schema(request_data)
            except vol.Invalid as err:
                msg = humanize_error(request_data, err)
                raise BadRequest(msg) from err
            return fn(*args, data, **kwargs)

        return patched

    return decorator


def json_response():
    def decorator(fn):
        @functools.wraps(fn)
        def patched(*args, **kwargs):
            ret = fn(*args, **kwargs)
            # match `return jsonify(...)` and `return jsonify(...), 404`
            is_already_response = isinstance(ret, Response) or (
                isinstance(ret, tuple) and isinstance(ret[0], Response)
            )
            if not is_already_response:
                ret = jsonify(ret)
            return ret

        return patched

    return decorator


# TODO: error responses in json
