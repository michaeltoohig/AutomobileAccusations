from uuid import uuid4
from datetime import datetime, timedelta

from app.models.user import User
from app.models.role import Role
from app.models.vehicle import Vehicle
from app.models.accusation import Accusation, AccusationType
from app.core.security import get_password_hash

def get_user(username, db_session):
    return db_session.query(User).filter(User.id == username).first()

def check_if_user_is_active(user):
    return user.is_active

def check_if_user_is_superuser(user):
    return user.is_superuser

def check_if_username_is_active(username, db_session):
    user = get_user(username, db_session)
    return check_if_user_is_active(user)

def get_role_by_name(name, db_session):
    role = db_session.query(Role).filter(Role.name == name).first()
    return role

def get_role_by_id(role_id, db_session):
    role = db_session.query(Role).filter(Role.id == role_id).first()
    return role

def create_role(name, db_session):
    role = Role(name=name)
    db_session.add(role)
    db_session.commit()
    return role

def get_roles(db_session):
    return db_session.query(Role).all()

def get_user_roles(user):
    return user.roles


def get_user_by_username(username, db_session) -> User:
    user = db_session.query(User).filter(User.email == username).first()  # type: User
    return user

def get_user_by_id(user_id, db_session):
    user = db_session.query(User).filter(User.id == user_id).first()  # type: User
    return user

def get_user_hashed_password(user):
    return user.password


def get_user_id(user):
    return user.id

def get_users(db_session):
    return db_session.query(User).all()


def create_user(db_session, username, password, first_name=None, last_name=None, is_superuser=False):
    user = User(
        email=username,
        password=get_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        is_superuser=is_superuser,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

def assign_role_to_user(role: Role, user: User, db_session):
    user.roles.append(role)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_vehicles(db_session):
    return db_session.query(Vehicle).all()


def get_vehicle_by_plate(plate, db_session) -> Vehicle:
    vehicle = db_session.query(Vehicle).filter(Vehicle.plate == plate).first()  # type: Vehicle
    return vehicle


def create_vehicle(db_session, plate):
    vehicle = Vehicle(
        plate=plate
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


def check_if_user_has_accused_vehicle_today(user, vehicle, db_session):
    yesterday = datetime.utcnow() - timedelta(hours=24)
    accusation = db_session.query(Accusation) \
        .filter(Accusation.user_id == user.id) \
        .filter(Accusation.vehicle_id == vehicle.id) \
        .filter(Accusation.created_at > yesterday) \
        .first()
    return accusation


def get_accusations(db_session):
    return db_session.query(Accusation).all()

def get_user_accusations(user):
    return user.accusations

def get_accusation_by_public_id(public_id, db_session):
    accusation = db_session.query(Accusation).filter(Accusation.public_id == public_id).first()
    return accusation

def create_accusation(db_session, occured_at, vehicle_id, acc_type_id, user_id, comment=None):
    accusation = Accusation(
        public_id=str(uuid4()),
        occured_at=occured_at,
        vehicle_id=vehicle_id,
        acc_type_id=acc_type_id,
        user_id=user_id,
        comment=comment
    )
    db_session.add(accusation)
    db_session.commit()
    db_session.refresh(accusation)
    return accusation


def get_acc_types(db_session):
    return db_session.query(AccusationType).all()

def get_acc_type_by_name(name, db_session):
    acc_type = db_session.query(AccusationType).filter(AccusationType.name == name).first()
    return acc_type

def get_acc_type_by_id(acc_type_id, db_session):
    acc_type = db_session.query(AccusationType).filter(AccusationType.id == acc_type_id).first()
    return acc_type

def create_acc_type(db_session, name, desc):
    acc_type = AccusationType(
        name=name,
        desc=desc,
    )
    db_session.add(acc_type)
    db_session.commit()
    db_session.refresh(acc_type)
    return acc_type