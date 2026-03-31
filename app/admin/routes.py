from flask import request, jsonify
from flask_login import login_required
from . import admin_bp
from ..models import User
from ..decorators import role_required


@admin_bp.get('/users')
@login_required
@role_required('administrateur')
def list_users():
    type_filter = request.args.get('type', '').strip()
    search = request.args.get('search', '').strip()

    query = User.query

    if type_filter:
        query = query.filter(User.type == type_filter)

    if search:
        query = query.filter(
            (User.nom.ilike(f'%{search}%')) |
            (User.prenom.ilike(f'%{search}%')) |
            (User.username.ilike(f'%{search}%'))
        )

    users = query.order_by(User.nom, User.prenom).all()

    return jsonify([{
        'id': u.id,
        'nom': u.nom,
        'prenom': u.prenom,
        'username': u.username,
        'type': u.type,
        'is_active': u.is_active
    } for u in users]), 200
