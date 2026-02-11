# Import all models so Alembic autogenerate detects them
from app.models.agent_session import AgentSession  # noqa: F401
from app.models.api_usage import ApiUsage  # noqa: F401
from app.models.auth_token import AuthToken  # noqa: F401
from app.models.axiom_challenge import AxiomChallenge  # noqa: F401
from app.models.bank_instance import BankInstance  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.email_log import EmailLog  # noqa: F401
from app.models.goal import Goal  # noqa: F401
from app.models.journey import Journey  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.perspective import Perspective  # noqa: F401
from app.models.setting import Setting  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.vdba import Vdba  # noqa: F401
from app.models.vibe_analysis import VibeAnalysis  # noqa: F401
from app.models.vibe_session import VibeSession  # noqa: F401
