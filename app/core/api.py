from ninja import NinjaAPI
from core.routers import accounts_router

api = NinjaAPI()

api.add_router("accounts", accounts_router)
