from app import db
from geoalchemy2 import Geometry
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Predio(db.Model):
    __tablename__ = 'predios'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    area = db.Column(db.Float, nullable=False)
    # Cambiamos latitud/longitud por geometría de polígono
    geometria = db.Column(Geometry(geometry_type='POLYGON', srid=4326))
    propietario = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        from shapely.wkb import loads
        # Convertir WKB a GeoJSON
        polygon = loads(bytes(self.geometria.data))
        return {
            'id': self.id,
            'codigo': self.codigo,
            'direccion': self.direccion,
            'area': self.area,
            'geometria': polygon.__geo_interface__,
            'propietario': self.propietario
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))