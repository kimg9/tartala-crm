from passlib.hash import argon2

from db_config.connexion import session
from models.models import (DepartmentEnum, PermissionTypeEnum,
                           ResourceTypeEnum, Users)
from repositories.users.user_repository import UserRepository

user_repo = UserRepository(session)


class UserApp:
    def create(self, **kwargs):
        if "password" in kwargs:
            kwargs["password"] = argon2.hash(kwargs["password"])
        user = user_repo.create_user(**kwargs)
        if "department" in kwargs:
            self.set_permission(user=user)

    @staticmethod
    def authentification(username, password):
        user = user_repo.get_by_username(username)
        if user:
            if argon2.verify(password, user.password):
                return user

    @staticmethod
    def jwt_authentification(id, username):
        user = user_repo.get_by_id_and_username(id, username)
        if user:
            return True
        return False

    def set_permission(self, user):
        if user.department.value == DepartmentEnum.GESTION:
            perms_list = [
                (PermissionTypeEnum.CREATE, ResourceTypeEnum.CLIENT),
                (PermissionTypeEnum.CREATE, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.EVENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CLIENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.CLIENT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.EVENT),
                (PermissionTypeEnum.DELETE, ResourceTypeEnum.CLIENT),
            ]
            user_repo.bulk_update_permissions(user, perms_list)
        elif user.department.value == DepartmentEnum.COMMERCIAL:
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
        elif user.department.value == DepartmentEnum.SUPPORT:
            perms_list = [
                (PermissionTypeEnum.READ, ResourceTypeEnum.EVENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CLIENT),
                (PermissionTypeEnum.READ, ResourceTypeEnum.CONTRACT),
                (PermissionTypeEnum.UPDATE, ResourceTypeEnum.EVENT),
            ]
            user_repo.bulk_update_permissions(user, perms_list)

    def has_permission(self, user: Users, resource_type: str, permission_type: str) -> bool:
        return any(
            p.resource_type == resource_type and p.permission_type == permission_type
            for p in user.permissions
        )
