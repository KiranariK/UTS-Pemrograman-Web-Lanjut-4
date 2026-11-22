from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
db=SQLAlchemy()
migrate=Migrate()
def create_app(test_config=None):
    app=Flask(__name__); app.config.from_object(Config)
    if test_config: app.config.update(test_config)
    db.init_app(app); migrate.init_app(app,db)
    from app import models
    from app.controllers.api import api
    app.register_blueprint(api,url_prefix="/api/v1")
    @app.get("/")
    def home(): return jsonify({"name":"Cyber Incident Management API","version":"1.0.0","health":"/api/v1/health"})
    @app.errorhandler(404)
    def nf(e): return jsonify({"success":False,"error":{"code":"NOT_FOUND","message":"Resource tidak ditemukan"}}),404
    return app
