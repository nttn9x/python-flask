from flask import abort


def format_respond(fn, *args, **kwargs):
    res = None
    try:
        res = fn(*args, *kwargs)
    except OSError as err:
        abort(500, str(err))
    except ValueError as err:
        abort(400, str(err))

    return res
