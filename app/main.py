from fastapi import FastAPI

from app.routers import admin, auth

app = FastAPI(title="Secure REST API", version="0.1.0")
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
