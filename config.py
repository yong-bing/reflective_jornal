class Config:
    def __init__(self):
        from django.conf import settings
        self.__dict__.update({k: v for k, v in settings.__dict__.items() if not k.startswith('__')})

        try:
            import deploy_settings
            self.__dict__.update({k: v for k, v in deploy_settings.__dict__.items() if not k.startswith('__')})
        except ImportError:
            pass

    def __getattr__(self, name):
        raise AttributeError(f"Config has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
        else:
            raise AttributeError(f"Cannot add new attribute '{name}'")


config = Config()
