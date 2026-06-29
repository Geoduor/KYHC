from fastapi import FastAPI

app = FastAPI(
    title="KYHC API",
    description="Kisumu Youngsters Hockey Club Management System API",
    version="1.0.0",
)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "application": "KYHC API",
        "version": "1.0.0",
    }