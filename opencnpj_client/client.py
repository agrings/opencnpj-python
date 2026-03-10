"""
Cliente principal para API do OpenCNPJ
"""

import requests
import json
import re
from typing import Optional, Dict, Any, List
from datetime import datetime

from .models import Empresa, Endereco, CNAE


class OpenCNPJClient:
    """Cliente para consulta da API do OpenCNPJ"""
    
    BASE_URL = "https://api.opencnpj.org"
    
    def __init__(self, timeout: int = 15, user_agent: str = None):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or "OpenCNPJ-Python-Client/1.0",
            "Accept": "application/json",
            "Accept-Language": "pt-BR,pt;q=0.9"
        })
    
    def _limpar_cnpj(self, cnpj: str) -> str:
        """Remove caracteres não numéricos do CNPJ"""
        return re.sub(r'\D', '', cnpj)
    
    def _validar_cnpj(self, cnpj: str) -> bool:
        """Valida se o CNPJ tem 14 dígitos"""
        return len(cnpj) == 14 and cnpj.isdigit()
    
    def _parse_data(self, data_str: Optional[str]) -> Optional[datetime]:
        """Converte string de data para objeto datetime"""
        if not data_str:
            return None
        try:
            return datetime.strptime(data_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None
    
    def _parse_cnae(self, dados: Optional[Dict]) -> Optional[CNAE]:
        """Converte dados de CNAE para objeto CNAE"""
        if not dados:
            return None
        return CNAE(
            codigo=dados.get("codigo"),
            descricao=dados.get("descricao")
        )
    
    def _parse_endereco(self, dados: Optional[Dict]) -> Endereco:
        """Converte dados de endereço para objeto Endereco"""
        if not dados:
            return Endereco()
            
        return Endereco(
            logradouro=dados.get("logradouro"),
            numero=str(dados.get("numero")) if dados.get("numero") else None,
            complemento=dados.get("complemento"),
            bairro=dados.get("bairro"),
            cep=dados.get("cep"),
            municipio=dados.get("municipio"),
            uf=dados.get("uf")
        )
    
    def _safe_get_descricao(self, campo: Any) -> Optional[str]:
        """
        Extrai com segurança a descrição de um campo que pode ser:
        - Dicionário com chave 'descricao'
        - String direta
        - None
        """
        if not campo:
            return None
        if isinstance(campo, dict):
            return campo.get("descricao")
        if isinstance(campo, str):
            return campo
        return str(campo) if campo else None
    
    def _parse_empresa(self, dados: Dict) -> Empresa:
        """Converte dados da API para objeto Empresa"""
        
        # Processar porte com segurança
        porte = dados.get("porte")
        if isinstance(porte, dict):
            porte_descricao = porte.get("descricao")
        else:
            porte_descricao = str(porte) if porte else None
        
        # Processar natureza jurídica com segurança
        natureza_juridica = self._safe_get_descricao(dados.get("natureza_juridica"))
        
        empresa = Empresa(
            cnpj=self._limpar_cnpj(dados.get("cnpj", "")),
            razao_social=dados.get("razao_social"),
            nome_fantasia=dados.get("nome_fantasia"),
            data_abertura=self._parse_data(dados.get("data_inicio_atividade")),
            situacao_cadastral=dados.get("descricao_situacao_cadastral"),
            data_situacao=self._parse_data(dados.get("data_situacao_cadastral")),
            capital_social=dados.get("capital_social"),
            porte=porte_descricao,
            natureza_juridica=natureza_juridica,
            telefone=dados.get("telefone1"),
            email=dados.get("email"),
            dados_brutos=dados
        )
        
        # Extrair endereço
        if dados.get("municipio"):
            empresa.endereco = self._parse_endereco(dados)
        
        # Extrair atividade principal
        if dados.get("cnae_fiscal"):
            empresa.atividade_principal = CNAE(
                codigo=str(dados.get("cnae_fiscal")),
                descricao=dados.get("cnae_fiscal_descricao")
            )
        
        # Extrair atividades secundárias
        if dados.get("cnaes_secundarios"):
            for cnae in dados["cnaes_secundarios"]:
                if isinstance(cnae, dict):
                    empresa.atividades_secundarias.append(self._parse_cnae(cnae))
        
        # Extrair sócios
        if dados.get("qsa"):
            empresa.socios = dados["qsa"]
        
        return empresa
    
    def consultar(self, cnpj: str) -> Optional[Empresa]:
        """Consulta um CNPJ na API do OpenCNPJ"""
        cnpj_limpo = self._limpar_cnpj(cnpj)
        
        if not self._validar_cnpj(cnpj_limpo):
            raise ValueError(f"CNPJ inválido: {cnpj}. Deve conter 14 dígitos.")
        
        url = f"{self.BASE_URL}/{cnpj_limpo}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            dados = response.json()
            return self._parse_empresa(dados)
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print(f"CNPJ {cnpj_limpo} não encontrado.")
                return None
            elif response.status_code == 403:
                print("Erro 403: Acesso proibido. Verifique o User-Agent.")
            elif response.status_code == 429:
                print("Erro 429: Muitas requisições. Aguarde um momento.")
            else:
                print(f"Erro HTTP {response.status_code}: {e}")
            return None
            
        except requests.exceptions.ConnectionError:
            print("Erro de conexão. Verifique sua internet.")
            return None
            
        except requests.exceptions.Timeout:
            print(f"Timeout após {self.timeout} segundos.")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return None
            
        except json.JSONDecodeError:
            print("Erro ao decodificar resposta JSON.")
            return None
    
    def consultar_multiplos(self, lista_cnpjs: List[str]) -> Dict[str, Optional[Empresa]]:
        """Consulta múltiplos CNPJs"""
        resultados = {}
        for cnpj in lista_cnpjs:
            try:
                print(f"Consultando CNPJ: {cnpj}")
                resultados[cnpj] = self.consultar(cnpj)
            except Exception as e:
                print(f"Erro ao consultar {cnpj}: {e}")
                resultados[cnpj] = None
        return resultados


# Função de atalho
def consultar_cnpj(cnpj: str) -> Optional[Empresa]:
    """Função de atalho para consultar um CNPJ"""
    client = OpenCNPJClient()
    return client.consultar(cnpj)

