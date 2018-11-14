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
    get_accusations,
    create_accusation,
    get_acc_type_by_id,
    get_vehicle_by_plate,    
    check_if_user_is_active,
    check_if_user_is_superuser,
    get_accusation_by_public_id,
    check_if_user_has_accused_vehicle_today,
)


from app.main import app

# Import Schemas
from app.schemas.accusation import AccusationSchema

# Import models


@docs.register
@doc(
    description="Retrieve the accusations",
    security=security_params,
    tags=["accusations"],
)
@app.route(f"{config.API_V1_STR}/accusations/", methods=["GET"])
@marshal_with(AccusationSchema(many=True))
@jwt_required
def route_accusationusation_get():
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    
    accusations = get_accusations(db_session)
    return accusations


@docs.register
@doc(description="Create new accusation", security=security_params, tags=["accusations"])
@app.route(f"{config.API_V1_STR}/accusations/", methods=["POST"])
@use_kwargs(
    {
        "occured_at": fields.DateTime(required=True),
        "comment": fields.Str(),
        "plate": fields.Str(required=True),
        "acc_type_id": fields.Int(required=True),
    }
)
@marshal_with(AccusationSchema())
@jwt_required
def route_accusation_post(occured_at, comment, plate, acc_type_id):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")

    vehicle = get_vehicle_by_plate(plate, db_session)
    if not vehicle:
        return abort(400, f"The vehicle with plate: {plate} does not exist")

    acc_type = get_acc_type_by_id(acc_type_id, db_session)
    if not acc_type:
        return abort(400, f"The accusation type with id: {acc_type_id} does not exist")

    accusation = check_if_user_has_accused_vehicle_today(current_user, vehicle, db_session)
    if accusation:
        return abort(
            400, f"You may not accuse the vehicle with plate: {plate} more than once per day"
        )

    accusation = create_accusation(
        db_session,
        occured_at,
        vehicle.id,
        acc_type.id,
        current_user.id,
        comment,
    )
    return accusation


@docs.register
@doc(description="Get a specific accusation by id", security=security_params, tags=["accusations"])
@app.route(f"{config.API_V1_STR}/accusations/<string:public_id>", methods=["GET"])
@marshal_with(AccusationSchema())
@jwt_required
def route_accusation_public_id_get(public_id):
    current_user = get_current_user()  # type: User

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")

    accusation = get_accusation_by_public_id(public_id, db_session)

    if not accusation:
        return abort(400, f"The accusation with id: {public_id} does not exist")

    return accusation


