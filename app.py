from fastapi import FastAPI
from api import router as api_router
from middlewares import AuthMiddleware

app = FastAPI()
app.include_router(api_router)
app.add_middleware(AuthMiddleware)
