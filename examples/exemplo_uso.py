"""
Exemplo de uso do módulo opencnpj_client
"""

from opencnpj_client import OpenCNPJClient, consultar_cnpj
import time

def exemplo_basico():
    """Exemplo básico de consulta"""
    print("🔹 EXEMPLO BÁSICO")
    print("-" * 40)
    
    # Consulta direta com função de atalho
    empresa = consultar_cnpj("43.350.131/0001-01")  # Substitua por um CNPJ válido
    
    if empresa:
        print(f"Razão Social: {empresa.razao_social}")
        print(f"CNPJ: {empresa.cnpj_formatado}")
        print(f"Situação: {empresa.situacao_descricao}")
    print()


def exemplo_avancado():
    """Exemplo com acesso a todos os dados"""
    print("🔹 EXEMPLO AVANÇADO")
    print("-" * 40)
    
    # Criar cliente com configurações personalizadas
    client = OpenCNPJClient(
        timeout=20,
        user_agent="MeuApp/1.0 (contato@meuapp.com)"
    )
    
    # Lista de CNPJs para consultar
    cnpjs = [
        "03.102.452/0001-72",  # Substitua por CNPJs válidos
        "28.176.667/0002-40",
    ]
    
    for cnpj in cnpjs:
        print(f"\nConsultando: {cnpj}")
        empresa = client.consultar(cnpj)
        
        if empresa:
            print(f"✅ Encontrada: {empresa.razao_social}")
            print(f"   Endereço: {empresa.endereco.formatar_completo()[:100]}...")
            
            if empresa.atividade_principal:
                print(f"   Atividade: {empresa.atividade_principal}")
        
        # Pequena pausa entre consultas
        time.sleep(1)
    print()


def exemplo_tratamento_erros():
    """Exemplo de tratamento de erros"""
    print("🔹 EXEMPLO DE TRATAMENTO DE ERROS")
    print("-" * 40)
    
    client = OpenCNPJClient()
    
    # Teste com CNPJ inválido
    try:
        empresa = client.consultar("123")
    except ValueError as e:
        print(f"✅ Erro capturado (esperado): {e}")
    
    # Teste com CNPJ não existente
    empresa = client.consultar("03.102.452/0001-72")
    if empresa is None:
        print("✅ CNPJ não encontrado (tratado corretamente)")
    
    print()


def exemplo_processamento_dados():
    """Exemplo de processamento dos dados retornados"""
    print("🔹 EXEMPLO DE PROCESSAMENTO")
    print("-" * 40)
    
    client = OpenCNPJClient()
    empresa = client.consultar("03.102.452/0001-72")  # Substitua por um CNPJ válido
    
    if empresa:
        # Acessar propriedades calculadas
        print(f"CNPJ Formatado: {empresa.cnpj_formatado}")
        print(f"Capital Social: {empresa.capital_social_formatado}")
        
        # Verificar situação cadastral
        if "ATIVA" in empresa.situacao_cadastral.upper() if empresa.situacao_cadastral else False:
            print("✅ Empresa está ATIVA")
        else:
            print("⚠️ Empresa não está ativa")
        
        # Contar atividades secundárias
        if empresa.atividades_secundarias:
            print(f"📋 Possui {len(empresa.atividades_secundarias)} atividades secundárias")
        
        # Verificar se tem sócios
        if empresa.socios:
            print(f"👥 Número de sócios: {len(empresa.socios)}")


if __name__ == "__main__":
    print("=" * 60)
    print("📦 TESTE DO MÓDULO OPENCnpj")
    print("=" * 60)
    
    exemplo_basico()
    exemplo_avancado()
    exemplo_tratamento_erros()
    exemplo_processamento_dados()


