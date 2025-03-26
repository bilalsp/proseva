import uvicorn
from iam.app import settings


def runserver():
    uvicorn.run(
        app="iam.app:app", 
        host="localhost", 
        port=settings.ms.port, 
        reload=settings.ms.reloading,
        reload_dirs=["src"],
    )


if __name__ == "__main__":
    runserver()
