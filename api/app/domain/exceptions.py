class DomainException(Exception):
    """Exceção base para regras de negócio e validações de domínio."""
    def __init__(self, message: str, code: str = "domain_error", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code