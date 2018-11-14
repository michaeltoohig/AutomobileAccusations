# -*- coding: utf-8 -*-

# Import standard library modules

# Import installed modules

# # Import installed packages
from flask import abort
from webargs import fields
from flask_apispec import doc, use_kwargs, marshal_with
from flask_jwt_extended import get_current_user, jwt_required

# Import app code
from app.api.api_v1.api_docs import docs, security_params
from app.core import config
from app.db.flask_session import db_session
from app.core.celery_app import celery_app
from app.db.utils import (
    get_acc_types,
    create_acc_type,
    get_acc_type_by_name,
    get_acc_type_by_id,
    check_if_user_is_active,
    check_if_user_is_superuser,
)


from app.main import app

# Import Schemas
from app.schemas.accusation import AccusationTypeSchema

# Import models


@docs.register
@doc(
    description="Retrieve the accusation types",
    security=security_params,
    tags=["accusation types"],
)
@app.route(f"{config.API_V1_STR}/accusation_types/", methods=["GET"])
@marshal_with(AccusationTypeSchema(many=True))
@jwt_required
def route_accusation_type_get():
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    
    acc_types = get_acc_types(db_session)
    app.logger.info(acc_types)
    return acc_types


@docs.register
@doc(description="Create new vehicle", security=security_params, tags=["accusation types"])
@app.route(f"{config.API_V1_STR}/accusation_types/", methods=["POST"])
@use_kwargs(
    {
        "name": fields.Str(required=True),
        "desc": fields.Str(required=True),
    }
)
@marshal_with(AccusationTypeSchema())
@jwt_required
def route_acc_type_post(name, desc):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_superuser(current_user):
        abort(400, "Only a superuser can execute this action")

    acc_type = get_acc_type_by_name(name, db_session)

    if acc_type:
        return abort(
            400, f"The accusation type with this name already exists in the system: {name}"
        )

    acc_type = create_acc_type(db_session, name, desc)
    return acc_type


@docs.register
@doc(description="Get a specific accusation type by id", security=security_params, tags=["accusation types"])
@app.route(f"{config.API_V1_STR}/accusation_types/<int:acc_type_id>", methods=["GET"])
@marshal_with(AccusationTypeSchema())
@jwt_required
def route_acc_type_id_get(acc_type_id):
    current_user = get_current_user()  # type: User

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")

    acc_type = get_acc_type_by_id(acc_type_id, db_session)

    if not acc_type:
        return abort(400, f"The accusation type with id: {acc_type_id} does not exist")

    return acc_type


