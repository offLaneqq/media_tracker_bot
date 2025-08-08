from fastapi import FastAPI
from .api_router import router

app = FastAPI(title="Media Tracker API")  # створюємо екземпляр ASGI-додатку

# Підключаємо маршрути
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}