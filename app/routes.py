from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Predio
from app.forms import LoginForm, RegistrationForm, PredioForm
import folium
from folium.plugins import Draw
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
import json

bp = Blueprint('routes', __name__)

@bp.route('/')
@login_required
def index():
    # Crear mapa base centrado en Tausa, Cundinamarca
    mapa = folium.Map(location=[5.1968, -73.8868], zoom_start=14)
    
    # Añadir control de dibujo con opción de polígonos
    Draw(
        export=True,
        draw_options={
            'polygon': True,
            'rectangle': True,
            'circle': False,
            'polyline': False,
            'marker': False
        }
    ).add_to(mapa)
    
    # Obtener todos los predios y añadirlos al mapa como polígonos
    predios = Predio.query.all()
    for predio in predios:
        geo_data = predio.to_dict()
        folium.GeoJson(
            geo_data['geometria'],
            name=f"Predio {predio.codigo}",
            tooltip=f"Predio {predio.codigo}",
            popup=folium.Popup(
                f"<b>Código:</b> {predio.codigo}<br>"
                f"<b>Dirección:</b> {predio.direccion}<br>"
                f"<b>Área:</b> {predio.area} m²<br>"
                f"<b>Propietario:</b> {predio.propietario}",
                max_width=300
            ),
            style_function=lambda x: {
                'fillColor': '#3388ff',
                'color': '#3388ff',
                'weight': 2,
                'fillOpacity': 0.5
            }
        ).add_to(mapa)
    
    # Añadir control de capas
    folium.LayerControl().add_to(mapa)
    
    return render_template('index.html', mapa=mapa._repr_html_())
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('routes.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

@bp.route('/predios')
@login_required
def list_predios():
    predios = Predio.query.all()
    return render_template('predios.html', predios=predios)

@bp.route('/predios/add', methods=['GET', 'POST'])
@login_required
def add_predio():
    if not current_user.is_admin:
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('routes.index'))
    
    form = PredioForm()
    if form.validate_on_submit():
        try:
            # Parsear GeoJSON y convertir a polígono
            geojson = json.loads(form.geometria.data)
            polygon = shape(geojson['geometry'])
            
            predio = Predio(
                codigo=form.codigo.data,
                direccion=form.direccion.data,
                area=form.area.data,
                geometria=from_shape(polygon, srid=4326),
                propietario=form.propietario.data
            )
            db.session.add(predio)
            db.session.commit()
            flash('Predio agregado exitosamente', 'success')
            return redirect(url_for('routes.list_predios'))
        except Exception as e:
            flash(f'Error al procesar la geometría: {str(e)}', 'danger')
    
    return render_template('add_predio.html', form=form)

@bp.route('/predios/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_predio(id):
    if not current_user.is_admin:
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('routes.index'))
    
    predio = Predio.query.get_or_404(id)
    form = PredioForm(obj=predio)
    
    if form.validate_on_submit():
        try:
            # Parsear GeoJSON y convertir a polígono
            geojson = json.loads(form.geometria.data)
            polygon = shape(geojson['geometry'])
            
            predio.codigo = form.codigo.data
            predio.direccion = form.direccion.data
            predio.area = form.area.data
            predio.geometria = from_shape(polygon, srid=4326)
            predio.propietario = form.propietario.data
            db.session.commit()
            flash('Predio actualizado exitosamente', 'success')
            return redirect(url_for('routes.list_predios'))
        except Exception as e:
            flash(f'Error al procesar la geometría: {str(e)}', 'danger')
    
    # Convertir geometría a GeoJSON para el formulario
    if predio.geometria:
        form.geometria.data = json.dumps({
            "type": "Feature",
            "geometry": predio.to_dict()['geometria']
        })
    
    return render_template('edit_predio.html', form=form, predio=predio)

@bp.route('/predios/delete/<int:id>', methods=['POST'])
@login_required
def delete_predio(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    predio = Predio.query.get_or_404(id)
    db.session.delete(predio)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Predio eliminado'})

@bp.route('/manage_users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('routes.index'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.is_admin:
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('routes.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('routes.manage_users'))
    return render_template('register.html', form=form)

@bp.route('/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    if current_user.id == id:
        return jsonify({'success': False, 'message': 'No puedes eliminarte a ti mismo'}), 400
    
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuario eliminado'})

# API REST para predios
@bp.route('/api/predios', methods=['GET'])
def api_get_predios():
    predios = Predio.query.all()
    return jsonify([predio.to_dict() for predio in predios])

@bp.route('/api/predios', methods=['POST'])
@login_required
def api_add_predio():
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    data = request.get_json()
    predio = Predio(
        codigo=data['codigo'],
        direccion=data['direccion'],
        area=data['area'],
        latitud=data['latitud'],
        longitud=data['longitud'],
        propietario=data['propietario']
    )
    db.session.add(predio)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Predio agregado', 'predio': predio.to_dict()})

@bp.route('/api/predios/<int:id>', methods=['PUT'])
@login_required
def api_update_predio(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    predio = Predio.query.get_or_404(id)
    data = request.get_json()
    
    predio.codigo = data.get('codigo', predio.codigo)
    predio.direccion = data.get('direccion', predio.direccion)
    predio.area = data.get('area', predio.area)
    predio.latitud = data.get('latitud', predio.latitud)
    predio.longitud = data.get('longitud', predio.longitud)
    predio.propietario = data.get('propietario', predio.propietario)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Predio actualizado', 'predio': predio.to_dict()})

@bp.route('/api/predios/<int:id>', methods=['DELETE'])
@login_required
def api_delete_predio(id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    predio = Predio.query.get_or_404(id)
    db.session.delete(predio)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Predio eliminado'})