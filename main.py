import uvicorn

from app.core.config import get_settings
from app.factory import create_app


settings = get_settings()
app = create_app(settings)


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.reload)
