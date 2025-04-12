from app import create_app, db
from app.models import User, Predio

app = create_app()

with app.app_context():
    # Crear todas las tablas
    db.create_all()
    
    # Crear usuario admin si no existe
    if not User.query.filter_by(username='Admin').first():
        admin = User(username='Admin', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado: Admin/admin123")