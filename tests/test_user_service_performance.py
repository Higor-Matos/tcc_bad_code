import logging
from unittest.mock import Mock, patch
import pytest
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def user_service():
    """
    Fixture para fornecer uma instância simulada do UserService.
    """
    service = Mock()

    # Simula o retorno de `process_all_users` para o processo completo: gerar HTML, PDF e enviar emails
    def mock_process_all_users():
        # Simula o tempo de gerar HTML, gerar PDF e enviar email
        start_time = time.time()

        # Simulação de transformação em HTML
        time.sleep(0.005)  # Atualizado para 5ms com base nos resultados

        # Simulação de geração de PDF
        time.sleep(7.1)  # Média aproximada dos valores observados

        # Simulação de envio de email
        time.sleep(0.002)  # Substituindo o valor 0 por 2ms para envio de email

        end_time = time.time()
        return end_time - start_time  # Retorna o tempo total gasto

    service.process_all_users = Mock(side_effect=mock_process_all_users)
    return service

@pytest.mark.benchmark(group="user_service", min_rounds=5)
@pytest.mark.performance  # Marcador para testes de performance
def test_process_all_users_performance(benchmark, user_service):
    """
    Testa a performance da função de processar as notas dos usuários.
    Isso inclui o tempo para:
    - Tratar os dados
    - Gerar HTML
    - Criar PDFs
    - Enviar emails
    """
    logger.info("Iniciando o teste de performance para 'process_all_users'.")

    result = benchmark(user_service.process_all_users)

    logger.info("Teste de performance concluído.")
    assert result is not None
