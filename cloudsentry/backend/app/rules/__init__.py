"""
CloudSentry AI — Rules Package
===============================
All security rules live here. The registry below lists every active rule.
"""

from app.rules.public_s3 import PublicS3Rule
from app.rules.excessive_iam import ExcessiveIAMRule
from app.rules.ssh_exposed import SSHExposedRule
from app.rules.root_mfa import RootMFARule
from app.rules.stale_key import StaleAccessKeyRule
from app.rules.unused_user import UnusedUserRule
from app.rules.cloudtrail_disabled import CloudTrailDisabledRule
from app.rules.unencrypted_storage import UnencryptedStorageRule


# Registry: order matters for output readability
ALL_RULES = [
    PublicS3Rule,
    ExcessiveIAMRule,
    SSHExposedRule,
    RootMFARule,
    StaleAccessKeyRule,
    UnusedUserRule,
    CloudTrailDisabledRule,
    UnencryptedStorageRule,
]