import uvicorn


def runserver():
    uvicorn.run(
        app="listing.app:app",
        host="localhost",
        # port=settings.ms.port,
        # reload=settings.ms.reloading,
        reload=True,
        reload_dirs=["src"],
    )


if __name__ == "__main__":
    runserver()
