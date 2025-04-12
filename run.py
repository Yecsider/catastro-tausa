from app import create_app
from app.models import db, User, Predio
import os

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Initialize the database with admin user and sample data"""
    db.drop_all()
    db.create_all()
    
    # Crear usuario admin
    admin = User(username="Admin", is_admin=True)
    admin.set_password("admin123")
    db.session.add(admin)
    
    # Crear algunos predios de ejemplo
    predios = [
        Predio(
            codigo="PRD001",
            direccion="Calle 5 # 3-45, Tausa",
            area=350.5,
            latitud=5.1978,
            longitud=-73.8878,
            propietario="Municipio de Tausa"
        ),
        Predio(
            codigo="PRD002",
            direccion="Carrera 7 # 10-20, Tausa",
            area=420.0,
            latitud=5.1985,
            longitud=-73.8890,
            propietario="Juan Pérez"
        ),
        Predio(
            codigo="PRD003",
            direccion="Vereda El Carmen, Tausa",
            area=1250.75,
            latitud=5.1920,
            longitud=-73.8800,
            propietario="María Gómez"
        )
    ]
    
    db.session.add_all(predios)
    db.session.commit()
    print("Base de datos inicializada con usuario admin (Admin/admin123) y predios de ejemplo.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))