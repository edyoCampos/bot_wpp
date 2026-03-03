"""
Script para monitorar workers RQ e estatísticas das filas.

Uso:
    python scripts/monitor_workers.py

    # Atualização contínua (Linux/Mac):
    watch -n 2 python scripts/monitor_workers.py
"""

from redis import Redis
from rq import Queue, Worker

from robbot.config.settings import settings


def monitor_queues():
    """Mostra estatísticas das filas RQ."""
    print("=" * 60)
    print("MONITOR DE WORKERS E FILAS RQ")
    print("=" * 60)
    print()

    # Conectar ao Redis
    redis_conn = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    # Listar workers ativos
    workers = Worker.all(connection=redis_conn)
    print(f"WORKERS ATIVOS: {len(workers)}")
    for worker in workers:
        state = "[LIVRE]" if worker.state == "idle" else "[OCUPADO]"
        queues_str = ", ".join([q.name for q in worker.queues])
        print(f"  - {worker.name}: {state} (filas: {queues_str})")
    print()

    # Estatísticas das filas
    queue_names = ["messages", "ai", "escalation", "failed"]
    print("JOBS NAS FILAS:")
    for queue_name in queue_names:
        queue = Queue(queue_name, connection=redis_conn)
        count = queue.count
        marker = "[!]" if count > 5 else "[OK]" if count == 0 else "[ ]"
        print(f"  {marker} {queue_name:12} : {count:3} jobs")
    print()

    # Jobs sendo processados
    started_jobs = redis_conn.smembers("rq:workers:started")
    print(f"JOBS SENDO PROCESSADOS: {len(started_jobs)}")
    for job_id in started_jobs:
        print(f"  - {job_id}")
    print()

    # Estatísticas globais
    processed = redis_conn.get("rq:stat:processed") or 0
    failed = redis_conn.get("rq:stat:failed") or 0
    print("TOTAL HISTÓRICO:")
    print(f"  Processados: {processed}")
    print(f"  Falhas: {failed}")
    print()

    # Recomendação
    total_pending = sum([Queue(name, connection=redis_conn).count for name in queue_names[:3]])
    if total_pending > len(workers) * 5:
        print("[RECOMENDAÇÃO] Escalar para mais workers!")
        print(f"  Comando: docker compose up -d --scale worker={len(workers) + 1}")
    elif len(workers) > 1 and total_pending == 0:
        print("[INFO] Sistema ocioso - workers esperando jobs")
    else:
        print("[OK] Sistema operando normalmente")

    print("=" * 60)


if __name__ == "__main__":
    try:
        monitor_queues()
    except KeyboardInterrupt:
        print("\nMonitor interrompido")
    except Exception as e:
        print(f"Erro: {e}")
