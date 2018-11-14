
# Import all the models, so that Base has them before being
# imported by Alembic or used by Flask
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.role import Role  # noqa
from app.models.vehicle import Vehicle  # noqa
from app.models.accusation import Accusation, AccusationType  # noqa
