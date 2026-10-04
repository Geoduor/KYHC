"""
Role groups used to guard write operations.

Reads only require an authenticated user; writes use these groups.
"""

from app.models.user import UserRole

# Super admin and club admin: full management.
ADMIN_ROLES = (
    UserRole.SUPER_ADMIN,
    UserRole.CLUB_ADMIN,
)

# Admins plus the team manager.
MANAGEMENT_ROLES = ADMIN_ROLES + (
    UserRole.TEAM_MANAGER,
)

# Admins plus coaching staff.
COACHING_ROLES = ADMIN_ROLES + (
    UserRole.COACH,
    UserRole.ASSISTANT_COACH,
)

# Everyone who can manage team data, training and match records.
STAFF_ROLES = MANAGEMENT_ROLES + (
    UserRole.COACH,
    UserRole.ASSISTANT_COACH,
)
