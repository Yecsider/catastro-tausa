from app import create_app, db
from app.models import User, Predio
import click

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Crea las tablas y usuario admin"""
    db.create_all()
    
    # Crear usuario admin si no existe
    if not User.query.filter_by(username="Admin").first():
        admin = User(username="Admin", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Base de datos inicializada con usuario admin (Admin/admin123)")
    else:
        print("La base de datos ya estaba inicializada")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))