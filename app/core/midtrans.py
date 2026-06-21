import midtransclient
from app.core.config import settings

snap = midtransclient.Snap(
    is_production=False,
    server_key=settings.MIDTRANS_SERVER_KEY,
    client_key=settings.MIDTRANS_CLIENT_KEY,
)