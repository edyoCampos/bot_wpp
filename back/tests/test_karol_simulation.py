"""
Script para simular conversa da Karol e testar fluxo completo.

Este script envia mensagens HTTP diretamente para o webhook simulando WAHA.
"""

import requests
import time
import json

API_URL = "http://localhost:3333"
WEBHOOK_URL = f"{API_URL}/api/v1/webhooks/waha"

# Simular conversa da Karol (mesmas mensagens reais)
KAROL_MESSAGES = [
    {
        "time": 0,
        "from_user": "oi",
        "expected_bot_behavior": "Saudar + Perguntar nome naturalmente"
    },
    {
        "time": 80,  # 1min 20s depois
        "from_user": "vi a clinica pelo insta",
        "expected_bot_behavior": "Reconhecer canal + Perguntar interesse"
    },
    {
        "time": 30,  # 30s depois
        "from_user": "me chamo karol",
        "expected_bot_behavior": "Usar nome Karol + Perguntar sobre interesse/necessidade"
    },
    {
        "time": 60,
        "from_user": "foi a descrição da clinica",
        "expected_bot_behavior": "Entender que viu perfil + Perguntar o que chamou atenção (SEM REPETIR depois!)"
    },
    {
        "time": 20,
        "from_user": "queria saber se a doutora trabalha com coleta cp",
        "expected_bot_behavior": "Confirmar que oferece + Perguntar contexto (SEM perguntar 'já fez antes?' ainda)"
    },
    {
        "time": 80,
        "from_user": "ja fiz antes",
        "expected_bot_behavior": "Salvar fact 'has_done_procedure_before=true' + Perguntar sobre experiência (NÃO perguntar 'já fez?' novamente!)"
    },
    {
        "time": 240,  # 4min depois
        "from_user": "foi uma experiência okay",
        "expected_bot_behavior": "Explorar o que foi 'okay' + Identificar necessidades atuais"
    },
    {
        "time": 90,
        "from_user": "sim, consegui, gostaria de agendar outra coleta, por favor",
        "expected_bot_behavior": "INTENT=SCHEDULING detectado + Pergunta rápida sobre disponibilidade (preparando handoff)"
    },
    {
        "time": 480,  # 8min depois (2x mensagens juntas)
        "from_user": "tem disponibilidade?\nficaria bom na sexta da semana que vem, de manhã",
        "expected_bot_behavior": "TRIGGER HANDOFF (calendar_access) + Mensagem: 'Vou te passar para o responsável...'"
    },
    {
        "time": 30,
        "from_user": "é você mesma que marca?",
        "expected_bot_behavior": "Confirmar handoff natural (sem revelar que é bot)"
    },
    {
        "time": 120,
        "from_user": "queria saber se é você que marca, se sim, quero saber se tem horário na sexta que vem pela manha",
        "expected_bot_behavior": "Já em handoff - Confirmar que responsável vai responder"
    },
    {
        "time": 30,
        "from_user": "e quanto fica o valor da consulta",
        "expected_bot_behavior": "Responder: R$ 600 mas SEM agendar (continuar handoff)"
    },
    {
        "time": 90,
        "from_user": "me passa as opções por favor",
        "expected_bot_behavior": "HANDOFF ativo - responsável está vendo"
    }
]


def send_waha_webhook(message_text: str, chat_id: str = "555198098876@c.us"):
    """Envia webhook simulando WAHA."""
    payload = {
        "session": "default",
        "event": "message",
        "payload": {
            "from": chat_id,
            "body": message_text,
            "type": "text",
            "timestamp": int(time.time()),
            "fromMe": False,
            "id": f"fake_{int(time.time() * 1000)}"
        }
    }
    
    print(f"\n{'='*80}")
    print(f"📤 ENVIANDO: {message_text}")
    print(f"{'='*80}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print(f"✅ Webhook aceito: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")
        return None


def wait_for_processing(seconds: int):
    """Aguarda processamento com feedback visual."""
    print(f"\n⏳ Aguardando {seconds}s para processamento...", end="", flush=True)
    for i in range(seconds):
        time.sleep(1)
        print(".", end="", flush=True)
    print(" ✅")


def check_conversation_state():
    """Verifica estado da conversa no banco."""
    # TODO: Implementar query no banco para verificar
    print("\n📊 Estado da conversa:")
    print("   (Verificar manualmente com: docker exec postgres psql...)")


def main():
    """Executa simulação completa."""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                   SIMULAÇÃO CONVERSA DA KAROL                         ║
║                                                                       ║
║  Objetivo: Testar fluxo completo e verificar:                        ║
║  ✓ Memória persistente (sem repetições)                              ║
║  ✓ Handoff triggers (scheduling, calendar)                           ║
║  ✓ Context builder (10 docs, 5000 chars)                             ║
║  ✓ Uso correto do nome                                               ║
║  ✓ Facts salvos (has_done_procedure_before)                          ║
╚═══════════════════════════════════════════════════════════════════════╝
""")
    
    input("Pressione ENTER para iniciar simulação...")
    
    for i, msg in enumerate(KAROL_MESSAGES, 1):
        print(f"\n\n{'#'*80}")
        print(f"# MENSAGEM {i}/{len(KAROL_MESSAGES)}")
        print(f"# Comportamento esperado: {msg['expected_bot_behavior']}")
        print(f"{'#'*80}")
        
        send_waha_webhook(msg['from_user'])
        
        # Aguardar processamento (simula delay real + tempo de processamento)
        wait_for_processing(15)  # 15s para processar + gerar resposta
        
        # Aguardar tempo até próxima mensagem (simula conversa real)
        if i < len(KAROL_MESSAGES):
            delay = msg.get('time', 30)
            print(f"⏸️  Simulando delay de {delay}s até próxima mensagem...")
            # Não aguardar de verdade (teste rápido)
            # time.sleep(delay)
    
    print(f"\n\n{'='*80}")
    print("✅ SIMULAÇÃO COMPLETA")
    print(f"{'='*80}")
    print("\nVerificar logs:")
    print("  docker-compose logs -f worker | grep -E 'MEMORY|HANDOFF|Karol'")
    print("\nVerificar banco de dados:")
    print("  docker exec postgres psql -U dba -d BotDB -c 'SELECT * FROM conversations WHERE phone_number LIKE \"%98098876%\";'")


if __name__ == "__main__":
    main()
