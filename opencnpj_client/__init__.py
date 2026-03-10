"""
Módulo para consulta de CNPJs na API do OpenCNPJ
"""

from .client import OpenCNPJClient, consultar_cnpj
from .models import Empresa, Endereco, CNAE

__version__ = "1.0.0"
__all__ = [
    "OpenCNPJClient",
    "consultar_cnpj",
    "Empresa",
    "Endereco",
    "CNAE"
]
