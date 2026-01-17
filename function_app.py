import azure.functions as func

from blueprints.lessons import lessons_bp

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_blueprint(lessons_bp)