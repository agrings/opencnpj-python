"""
Modelos de dados para o cliente OpenCNPJ
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class Endereco:
    """Representa o endereço de uma empresa"""
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cep: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    
    def formatar_completo(self) -> str:
        """Retorna o endereço formatado em uma linha"""
        partes = []
        if self.logradouro:
            partes.append(self.logradouro)
        if self.numero:
            partes.append(f", {self.numero}")
        if self.complemento:
            partes.append(f" - {self.complemento}")
        if self.bairro:
            partes.append(f" - {self.bairro}")
        if self.municipio and self.uf:
            partes.append(f" - {self.municipio}/{self.uf}")
        if self.cep:
            partes.append(f" - CEP: {self.cep}")
        return "".join(partes) if partes else "Endereço não disponível"


@dataclass
class CNAE:
    """Representa uma Classificação Nacional de Atividades Econômicas"""
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    
    def __str__(self) -> str:
        if self.codigo and self.descricao:
            return f"{self.codigo} - {self.descricao}"
        return self.codigo or self.descricao or "CNAE não disponível"


@dataclass
class Empresa:
    """Representa os dados completos de uma empresa a partir do CNPJ"""
    cnpj: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    data_abertura: Optional[datetime] = None
    situacao_cadastral: Optional[str] = None
    data_situacao: Optional[datetime] = None
    capital_social: Optional[float] = None
    porte: Optional[str] = None
    natureza_juridica: Optional[str] = None
    endereco: Endereco = field(default_factory=Endereco)
    atividade_principal: Optional[CNAE] = None
    atividades_secundarias: List[CNAE] = field(default_factory=list)
    telefone: Optional[str] = None
    email: Optional[str] = None
    socios: List[Dict[str, Any]] = field(default_factory=list)
    dados_brutos: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def cnpj_formatado(self) -> str:
        """Retorna o CNPJ formatado (XX.XXX.XXX/XXXX-XX)"""
        if not self.cnpj or len(self.cnpj) != 14:
            return self.cnpj or "CNPJ não informado"
        return f"{self.cnpj[:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:]}"
    
    @property
    def data_abertura_str(self) -> str:
        """Retorna a data de abertura formatada"""
        if self.data_abertura:
            return self.data_abertura.strftime("%d/%m/%Y")
        return "Data não disponível"
    
    @property
    def situacao_descricao(self) -> str:
        """Retorna a situação cadastral com data se disponível"""
        if self.situacao_cadastral and self.data_situacao:
            return f"{self.situacao_cadastral} desde {self.data_situacao.strftime('%d/%m/%Y')}"
        return self.situacao_cadastral or "Situação não disponível"
    
    @property
    def capital_social_formatado(self) -> str:
        """Retorna o capital social formatado como moeda"""
        if self.capital_social:
            return f"R$ {self.capital_social:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return "Capital social não disponível"
    
    def __post_init__(self):
        """Validação pós-inicialização"""
        # Garantir que natureza_juridica seja string
        if self.natureza_juridica is not None and not isinstance(self.natureza_juridica, str):
            self.natureza_juridica = str(self.natureza_juridica)
        
        # Garantir que porte seja string
        if self.porte is not None and not isinstance(self.porte, str):
            self.porte = str(self.porte)

