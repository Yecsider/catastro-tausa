import os
import os

class Config:
    # Si usas una variable de entorno en Render
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://postgres:btItLfQEwiBLQVVAGBIxuAjLoVQTPAzf@crossover.proxy.rlwy.net:37626/railway"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "openssl rand -hex 24"
