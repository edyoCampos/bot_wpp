#!/usr/bin/env python3
"""
Script helper para gerar secrets seguros para o arquivo .env
Funciona em qualquer plataforma (Windows, Linux, Mac)
"""

import secrets
import string


def generate_secret_key(length: int = 64) -> str:
    """Gera uma chave secreta hexadecimal."""
    return secrets.token_hex(length // 2)


def generate_api_key(length: int = 32) -> str:
    """Gera uma API key alfanumérica."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    """Gera todos os secrets necessários para o .env"""
    print("=" * 80)
    print("🔐 GERADOR DE SECRETS PARA .env")
    print("=" * 80)
    print()
    print("Copie os valores abaixo para o seu arquivo .env")
    print()
    
    print("# 🔐 SEGURANÇA")
    print(f"SECRET_KEY={generate_secret_key(64)}")
    print()
    
    print("# 💬 WAHA (WhatsApp HTTP API)")
    print(f"WAHA_API_KEY={generate_api_key(32)}")
    print(f"WAHA_DASHBOARD_PASSWORD={generate_api_key(32)}")
    print(f"WHATSAPP_SWAGGER_PASSWORD={generate_api_key(32)}")
    print()
    
    print("=" * 80)
    print("✅ Secrets gerados com sucesso!")
    print()
    print("📝 PRÓXIMOS PASSOS:")
    print("1. Copie os valores acima para o arquivo .env")
    print("2. Obtenha GOOGLE_API_KEY em: https://ai.google.dev/")
    print("3. (Opcional) Obtenha GROQ_API_KEY em: https://console.groq.com/")
    print("=" * 80)


if __name__ == "__main__":
    main()
