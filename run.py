from app import create_app
from app.models import db, User, Predio
import os

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))