from flask import Flask

def create_app(config_filename='config.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)

    # LOGGING
    from .custom_logger import get_logger

    fileHandler, streamHandler = get_logger()

    app.logger.addHandler(fileHandler)
    app.logger.addHandler(streamHandler)

    # BLUEPRINTS
    from .movies_summary import movies_summary
    from .authentication import authentication

    app.register_blueprint(movies_summary)
    app.register_blueprint(authentication)

    app.logger.info("APP RUNNING")
    return app