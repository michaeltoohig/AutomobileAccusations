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
    check_if_user_is_active,
    check_if_user_is_superuser,
    get_vehicles,
    get_users,
    get_user_by_username,
    create_user,
    get_user_by_id,
    get_role_by_id,
    assign_role_to_user,
    get_vehicle_by_plate,
    create_vehicle,
    create_accusation,
)


from app.main import app

# Import Schemas
from app.schemas.vehicle import VehicleSchema
from app.schemas.accusation import AccusationSchema

# Import models
from app.models.vehicle import Vehicle


@docs.register
@doc(
    description="Retrieve the vehicles",
    security=security_params,
    tags=["vehicles"],
)
@app.route(f"{config.API_V1_STR}/vehicles/", methods=["GET"])
@marshal_with(VehicleSchema(many=True))
@jwt_required
def route_vehicles_get():
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    if check_if_user_is_superuser(current_user):
        return get_vehicles(db_session)
    else:
        # return the current user's data, but in a list
        return [current_user]


@docs.register
@doc(description="Create new vehicle", security=security_params, tags=["vehicles"])
@app.route(f"{config.API_V1_STR}/vehicles/", methods=["POST"])
@use_kwargs(
    {
        "plate": fields.Str(required=True),
    }
)
@marshal_with(VehicleSchema())
@jwt_required
def route_vehicles_post(
    plate=None,
):
    current_user = get_current_user()

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_superuser(current_user):
        abort(400, "Only a superuser can execute this action")

    vehicle = get_vehicle_by_plate(plate, db_session)

    if vehicle:
        return abort(
            400, f"The vehicle with this plate already exists in the system: {plate}"
        )
    vehicle = create_vehicle(db_session, plate)
    return vehicle


@docs.register
@doc(description="Get a specific vehicle by plate", security=security_params, tags=["vehicles"])
@app.route(f"{config.API_V1_STR}/vehicles/<string:plate>", methods=["GET"])
@marshal_with(VehicleSchema())
@jwt_required
def route_vehicles_plate_get(plate):
    current_user = get_current_user()  # type: User

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")

    vehicle = get_vehicle_by_plate(plate, db_session)

    if not vehicle:
        return abort(400, f"The vehicle with plate: {plate} does not exist")

    return vehicle


@docs.register
@doc(description="Create an accusation for a specific vehicle by plate", security=security_params, tags=["vehicles"])
@app.route(f"{config.API_V1_STR}/vehicles/<string:plate>/accusations", methods=["POST"])
@use_kwargs(
    {
        "acc_type_id": fields.Int(required=True),
        "plate": fields.Str(required=True),
        "comment": fields.Str(),
        "occured_at": fields.DateTime(),
    }
)
@marshal_with(AccusationSchema())
@jwt_required
def route_vehicle_accusation_post(plate):
    current_user = get_current_user()  # type: User

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")

    vehicle = get_vehicle_by_plate(plate, db_session)

    if not vehicle:
        return abort(400, f"The vehicle with plate: {plate} does not exist")

    '''
    accusations = get_accusations_by_user_in_last_24_hours(user_id)
    if len(accusations) >= 5:
        return abort(400, f"Too many accusations today")

    if vehicle_id in [a.vehicle_id for a in accusations]:
        return abort(400, f"You may only accuse vehicle with plate: {plate} once per day")
    '''

    #accusation = get_recent_vehicle_accusation_by_user(user_id, vehicle_id, db_session)
    #if accusation:

    accusation = create_accusation(
        db_session,
        occured_at,
        vehicle.id,
        acc_type_id,
        user_id,
        comment,
        )

    return accusation

"""
@docs.register
@doc(description="Create new vehicle without the need to be logged in", tags=["vehicles"])
@app.route(f"{config.API_V1_STR}/vehicles/open", methods=["POST"])
@use_kwargs(
    {
        "plate": fields.Str(required=True),
    }
)
@marshal_with(VehicleSchema())
def route_vehicles_post_open(
    plate=None,
):
    if not config.USERS_OPEN_REGISTRATION:
        abort(403, "Open vehicle resgistration is forbidden on this server")
    
    vehicle = get_vehicle_by_plate(plate, db_session)

    if vehicle:
        return abort(
            400, f"The vehicle with this plate already exists in the system: {plate}"
        )

    vehicle = create_vehicle(db_session, plate)
    return vehicle


@docs.register
@doc(description="Get current user's vehicles", security=security_params, tags=["vehicles"])
@app.route(f"{config.API_V1_STR}/vehicles/me", methods=["GET"])
@marshal_with(VehicleSchema())
@jwt_required
def route_vehicles_me_get():
    current_user = get_current_user()
    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    return current_user


@docs.register
@doc(description="Assign a role to a user by ID", security=security_params, tags=["users"])
@app.route(f"{config.API_V1_STR}/users/<int:user_id>/roles/", methods=["POST"])
@use_kwargs({
    "role_id": fields.Int(required=True),
})
@marshal_with(VehicleSchema())
@jwt_required
def route_users_assign_role_post(user_id, role_id):
    current_user = get_current_user()  # type: User

    if not current_user:
        abort(400, "Could not authenticate user with provided token")
    elif not check_if_user_is_active(current_user):
        abort(400, "Inactive user")
    elif not check_if_user_is_superuser(current_user):
        abort(404, "Not authorized")

    user = get_user_by_id(user_id, db_session)
    if not user:
        return abort(400, f"The user with id: {user_id} does not exists")
    
    role = get_role_by_id(role_id, db_session)
    if not role:
        return abort(400, f"The role does not exist")
    
    updated_user = assign_role_to_user(role, user, db_session)
    return updated_user
"""