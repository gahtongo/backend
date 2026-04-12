from enum import Enum


class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    OPERATIONS_ADMIN = "operations_admin"
    CONTENT_ADMIN = "content_admin"
    CASE_MANAGER = "case_manager"


ROLE_HIERARCHY = {
    AdminRole.SUPER_ADMIN: 100,
    AdminRole.OPERATIONS_ADMIN: 80,
    AdminRole.CONTENT_ADMIN: 60,
    AdminRole.CASE_MANAGER: 40,
}


def has_role_or_above(current_role: str, required_role: AdminRole) -> bool:
    try:
        current_score = ROLE_HIERARCHY[AdminRole(current_role)]
        required_score = ROLE_HIERARCHY[required_role]
        return current_score >= required_score
    except Exception:
        return False