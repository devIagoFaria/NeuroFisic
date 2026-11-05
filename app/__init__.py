from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect



db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "chave-dev-neuropsico"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///neuropsico.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    csrf.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."

    from app import models
    from app.models.profissional import Profissional

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Profissional, int(user_id))

    from app.routes.auth import auth_bp
    from app.routes.pacientes import pacientes_bp
    from app.routes.avaliacoes import avaliacoes_bp
    from app.routes.ravlt import ravlt_bp
    from app.routes.tmt import tmt_bp
    from app.routes.fluencia_verbal import fluencia_bp
    from app.routes.analises import analises_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(pacientes_bp)
    app.register_blueprint(avaliacoes_bp)
    app.register_blueprint(ravlt_bp)
    app.register_blueprint(tmt_bp)
    app.register_blueprint(fluencia_bp)
    app.register_blueprint(analises_bp)

    @app.route("/")
    def home():
        return "<h1>NeuroPsico</h1><p>Sistema funcionando.</p>"


    with app.app_context():
        db.create_all()
        
        from app.seeds import criar_profissional_padrao
        criar_profissional_padrao()

    return app