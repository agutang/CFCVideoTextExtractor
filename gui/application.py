def configure_app(app):
    from services.i18n import set_language
    from services.configuration import load_language
    set_language(load_language())
