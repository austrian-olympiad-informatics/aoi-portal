import functools
from typing import Optional, Union

import voluptuous as vol  # type: ignore
from flask import Response, jsonify, request
from voluptuous.humanize import humanize_error  # type: ignore

from aoiportal.error import ERROR_VALIDATION_ERROR, AOIBadRequest

SchemaType = Union[vol.Schema, list, dict]


def json_api(schema: Optional[SchemaType] = None):
    if schema is not None:
        a = _json_request(schema)
        b = _json_response()
        return lambda fn: a(b(fn))
    return _json_response()


def _json_request(schema: SchemaType):
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
                raise AOIBadRequest(msg, error_code=ERROR_VALIDATION_ERROR)
            return fn(*args, data, **kwargs)

        return patched

    return decorator


def _json_response():
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
