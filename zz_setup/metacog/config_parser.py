from types import SimpleNamespace


def get_config():
    from meg1 import config
    res_config = SimpleNamespace()
    res_config.__annotations__ = config.__annotations__
    try:
        from meg1 import config_user
    except ImportError:
        raise ImportError("Please create config_user.py")
    for key in config.__annotations__:
        try:
            setattr(res_config, key, getattr(config_user, key))
        except AttributeError:
            try:
                setattr(res_config, key, getattr(config, key))
            except AttributeError:
                raise AttributeError(f"{key} must be set in config_user.py")
    return res_config


cfg = get_config()
