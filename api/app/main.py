from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.domain.exceptions import DomainException

from app.api.controllers.health_controller import router as health_router
from app.infrastructure.config.settings import get_settings


#Schema (DTO) do erro padronizado
class ErrorResponse(BaseModel):
    code: str
    message: str
    fields: dict[str, str] | None = None


settings = get_settings()
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#Erro de validação (422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    fields = {}
    for error in exc.errors():
        field_name = str(error["loc"][-1])
        fields[field_name] = error["msg"]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "validation_error",
            "message": "Não foi possível salvar o registro.",
            "fields": fields
        }
    )


#Erros comuns HTTP (400, 401, 403, 404, 409)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Traduz o status numérico para os códigos de texto exigidos
    codes = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict"
    }
    code = codes.get(exc.status_code, "error")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": code,
            "message": str(exc.detail)
        }
    )

#Erro Interno 500
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "internal_error",
            "message": "Ocorreu um erro interno no servidor."
        }
    )

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message}
    )


app.include_router(health_router)
