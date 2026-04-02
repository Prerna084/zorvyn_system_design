from fastapi import APIRouter
from src.controllers import auth_controller
from src.validations.auth import Token
from src.validations.user import UserOut
from src.middlewares.rate_limit import limiter

router = APIRouter()

# Decorator must be applied directly to the handler or wrapped here.
# FastAPI limiter can take the path, so we use limit on the actual function route.
# Alternatively, wrap it.
_login = limiter.limit("5/minute")(auth_controller.login)
router.post("/token", response_model=Token)(_login)

router.get("/me", response_model=UserOut)(auth_controller.me)
