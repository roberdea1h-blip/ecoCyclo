"""
Deprecated — import from module-specific exceptions instead.

Migration guide:
  from app.users.exceptions import UserNotFoundException, ...
  from app.report.exceptions import ReportNotFoundException, ...
  from app.reward.exceptions import RewardNotFoundException, ...
  from app.redemption.exceptions import RedemptionNotFoundException, ...
  from app.waste_type.exceptions import WasteTypeNotFoundException, ...
  from app.point_transaction.exceptions import InsufficientPointsException, ...
  from app.core.exceptions import ForbiddenException
"""

import warnings

from app.core.exceptions import ForbiddenException
from app.point_transaction.exceptions import InsufficientPointsException
from app.redemption.exceptions import RedemptionNotFoundException, RewardOutOfStockException
from app.report.exceptions import (
    CannotClaimOwnReportException,
    NotAssignedCleanerException,
    NotOriginalReporterException,
    ReportNotFoundException,
    ReportNotInProgressException,
    ReportNotPendingException,
    ReportNotPendingReviewException,
)
from app.reward.exceptions import RewardNotFoundException
from app.users.exceptions import (
    EmailAlreadyExistsException as EmailAlreadyRegistered,
    InvalidCredentialsException as CredentialsException,
    UserNotFoundException,
    VerificationTokenExpiredException as InvalidToken,
)
from app.waste_type.exceptions import WasteTypeNotFoundException

__all__ = [
    "CannotClaimOwnReportException",
    "CannotDeleteSelfException",
    "CredentialsException",
    "EmailAlreadyRegistered",
    "ForbiddenException",
    "InsufficientPointsException",
    "InvalidToken",
    "NotAssignedCleanerException",
    "NotOriginalReporterException",
    "RedemptionNotFoundException",
    "ReportNotFoundException",
    "ReportNotInProgressException",
    "ReportNotPendingException",
    "ReportNotPendingReviewException",
    "RewardNotFoundException",
    "RewardOutOfStockException",
    "UserNotFoundException",
    "UsernameAlreadyRegistered",
    "WasteTypeNotFoundException",
]


class UsernameAlreadyRegistered(ForbiddenException):
    def __init__(self) -> None:
        warnings.warn("UsernameAlreadyRegistered moved to app.users.exceptions", DeprecationWarning, stacklevel=2)
        super().__init__(message="Username already taken")


class CannotDeleteSelfException(ForbiddenException):
    def __init__(self) -> None:
        warnings.warn("CannotDeleteSelfException moved to app.users.exceptions", DeprecationWarning, stacklevel=2)
        super().__init__(message="Cannot delete yourself")
