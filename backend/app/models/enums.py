import enum


class UserRole(enum.StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class GoalType(enum.StrEnum):
    PREDEFINED = "predefined"
    CUSTOM = "custom"


class JourneyStatus(enum.StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class DimensionType(enum.StrEnum):
    ARCHITECTURE = "architecture"
    DESIGN = "design"
    ENGINEERING = "engineering"


class PhaseType(enum.StrEnum):
    GENERATE = "generate"
    REVIEW = "review"
    VALIDATE = "validate"
    SUMMARIZE = "summarize"


class PerspectiveStatus(enum.StrEnum):
    LOCKED = "locked"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ChallengeSeverity(enum.StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ChallengeResolution(enum.StrEnum):
    RESOLVED = "resolved"
    ACCEPTED_RISK = "accepted_risk"
    ACTION_REQUIRED = "action_required"


class BankType(enum.StrEnum):
    BANKABLE = "bankable"
    FILM = "film"
    FILM_REEL = "film_reel"
    PUBLISHED = "published"


class ApiService(enum.StrEnum):
    CLAUDE = "claude"
    WHISPER = "whisper"
    RESEND = "resend"


class EmailTemplate(enum.StrEnum):
    STAKEHOLDER_INVITE = "stakeholder_invite"
    VIBE_SUMMARY = "vibe_summary"
    JOURNEY_COMPLETE = "journey_complete"
    VDBA_PUBLISHED = "vdba_published"
    BUDGET_ALERT = "budget_alert"


class NotificationChannel(enum.StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    BOTH = "both"
