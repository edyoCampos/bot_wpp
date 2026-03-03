
import asyncio
import os
import sys
# Adiciona /app/src ao path para importar módulos do projeto
sys.path.append("/app/src")

from robbot.infra.integrations.waha.waha_client import WAHAClient
from robbot.config.settings import settings

async def test_health():
    print(f"Testing connectivity to WAHA at: {settings.WAHA_URL}")
    client = WAHAClient()
    
    try:
        print("1. Testing ping()...")
        resp = await client.ping()
        print(f"SUCCESS: {resp}")
    except Exception as e:
        print(f"FAILED ping: {e}")

    try:
        print("2. Testing get_server_version()...")
        resp = await client.get_server_version()
        print(f"SUCCESS: {resp}")
    except Exception as e:
        print(f"FAILED version: {e}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(test_health())
