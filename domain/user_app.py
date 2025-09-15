from passlib.hash import argon2

from db_config.connexion import session
from models.models import (DepartmentEnum, PermissionTypeEnum,
                           ResourceTypeEnum, Users)
from repositories.users.user_repository import UserRepository

user_repo = UserRepository(session)


class UserApp:
    def get_by_id(self, id):
        return user_repo.get_by_id(id)

    def get_by_username(self, username):
        return user_repo.get_by_username(username)

    def get_by_id_and_username(self, id, username):
        return user_repo.get_by_id_and_username(id, username)

    def create(self, **kwargs):
        if "password" in kwargs:
            kwargs["password"] = argon2.hash(kwargs["password"])
        user = user_repo.create_user(**kwargs)
        if "department" in kwargs:
            self.set_permission(user=user)
        return user

    def update(self, id, **kwargs):
        user = user_repo.get_by_id(id)
        if not user:
            return None

        forbidden_fields = ["permissions"]

        for key, value in kwargs.items():
            if key not in forbidden_fields:
                if hasattr(user, key):
                    setattr(user, key, value)

        user_repo.save_to_db()
        return user

    def delete(self, id):
        return user_repo.delete(id)

    @staticmethod
    def authentification(username, password):
        user = user_repo.get_by_username(username)
        if user:
            if argon2.verify(password, user.password):
                return user

    @staticmethod
    def jwt_authentification(id, username):
        return user_repo.get_by_id_and_username(id, username)

    def set_permission(self, user):
        if user.department.value == DepartmentEnum.GESTION.value:
            perms_list = [
                (PermissionTypeEnum.CREATE, ResourceTypeEnum.USER),
                (PermissionTypeEnum.CREATE, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.EVENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.USER),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.USER),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.EVENT),
                (PermissionTypeEnum.DELETE, ResourceTypeEnum.USER),
            ]
            user_repo.bulk_update_permissions(user, perms_list)
        elif user.department.value == DepartmentEnum.COMMERCIAL.value:
            perms_list = [
                (PermissionTypeEnum.CREATE, ResourceTypeEnum.CLIENT),
                (PermissionTypeEnum.CREATE, ResourceTypeEnum.EVENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.EVENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CLIENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.CLIENT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.CONTRACT),
            ]
            user_repo.bulk_update_permissions(user, perms_list)
        elif user.department.value == DepartmentEnum.SUPPORT.value:
            perms_list = [
                (PermissionTypeEnum.READ, ResourceTypeEnum.EVENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CLIENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.EVENT),
            ]
            user_repo.bulk_update_permissions(user, perms_list)

    def has_permission(self, user: Users, resource_type: str, permission_type: str) -> bool:
        return any(
            p.resource_type == ResourceTypeEnum(
                resource_type) and p.permission_type == PermissionTypeEnum(permission_type)
            for p in user.permissions
        )
