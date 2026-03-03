"""
ChromaDB client for vector storage and semantic search.

Este módulo fornece interface para ChromaDB, permitindo:
- Armazenar embeddings de conversas
- Buscar contexto similar
- Persistir dados entre restarts
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from robbot.config.settings import settings
from robbot.core.custom_exceptions import VectorDBError

logger = logging.getLogger(__name__)


class ChromaClient:
    """
    Client para ChromaDB com persistência local.

    Responsabilidades:
    - Gerenciar coleções ChromaDB
    - Adicionar documentos com embeddings
    - Buscar contexto similar semanticamente
    - Persistir dados em disco
    """

    def __init__(self, collection_name: str = "conversations"):
        """
        Inicializar cliente ChromaDB com persistência.

        Args:
            collection_name: Nome da coleção para armazenar conversas
        """
        try:
            # Configurar ChromaDB com persistência
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                ),
            )

            # Obter ou criar coleção
            self.collection = self.client.get_or_create_collection(
                name=collection_name, metadata={"description": "WhatsApp conversation contexts"}
            )

            logger.info(
                "[SUCCESS] ChromaClient initialized (collection=%s, path=%s, count=%s)",
                collection_name,
                settings.CHROMA_PERSIST_DIR,
                self.collection.count(),
            )

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(f"[ERROR] Failed to initialize ChromaClient: {e}", exc_info=True)
            raise VectorDBError(f"Initialization failed: {e}", original_error=e)

    def add_conversation(
        self,
        conversation_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
        doc_id: str | None = None,
    ) -> str:
        """
        Adicionar conversa ao ChromaDB com embedding automático.

        Args:
            conversation_id: ID da conversa
            text: Texto para criar embedding
            metadata: Metadados adicionais (timestamp, phone, etc.)
            doc_id: ID do documento (opcional, será gerado se não fornecido)

        Returns:
            ID do documento adicionado

        Raises:
            DatabaseError: Se falhar ao adicionar
        """
        try:
            # Gerar ID único se não fornecido
            if doc_id is None:
                doc_id = f"{conversation_id}_{uuid.uuid4().hex[:8]}"

            # Preparar metadados
            final_metadata = {
                "conversation_id": conversation_id,
                "timestamp": datetime.now(UTC).isoformat(),
                **(metadata or {}),
            }

            # Adicionar ao ChromaDB
            # ChromaDB gera embeddings automaticamente
            self.collection.add(
                documents=[text],
                metadatas=[final_metadata],
                ids=[doc_id],
            )

            logger.info(
                "[SUCCESS] Conversation added to ChromaDB (id=%s, conv_id=%s, length=%s)",
                doc_id,
                conversation_id,
                len(text),
            )

            return doc_id

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(
                "[ERROR] Failed to add conversation to ChromaDB: %s",
                e,
                exc_info=True,
                extra={"conversation_id": conversation_id},
            )
            raise VectorDBError(f"Failed to add conversation: {e}", original_error=e)

    def search_similar(
        self,
        query: str,
        conversation_id: str | None = None,
        n_results: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Buscar contextos similares semanticamente.

        Args:
            query: Texto para buscar similaridade
            conversation_id: Filtrar por conversa específica (opcional)
            n_results: Número máximo de resultados

        Returns:
            Lista de resultados similares:
            [
                {
                    "id": str,
                    "text": str,
                    "metadata": dict,
                    "distance": float
                }
            ]

        Raises:
            DatabaseError: Se falhar ao buscar
        """
        try:
            # Preparar filtro de metadados
            where_filter = None
            if conversation_id:
                where_filter = {"conversation_id": conversation_id}

            # Buscar no ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
            )

            # Formatar resultados
            formatted_results = []

            if results and results["documents"]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append(
                        {
                            "id": results["ids"][0][i],
                            "text": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i] if results.get("distances") else None,
                        }
                    )

            logger.info(
                "[SUCCESS] ChromaDB search completed (query_length=%s, n_results=%s, conv_id=%s)",
                len(query),
                len(formatted_results),
                conversation_id,
            )

            return formatted_results

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error("[ERROR] Failed to search ChromaDB: %s", e, exc_info=True, extra={"query": query[:100]})
            raise VectorDBError(f"Search failed: {e}", original_error=e)

    def get_context(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Obter contexto de uma conversa específica.

        Args:
            conversation_id: ID da conversa
            limit: Número máximo de documentos

        Returns:
            Lista de documentos da conversa:
            [
                {
                    "id": str,
                    "text": str,
                    "metadata": dict
                }
            ]

        Raises:
            DatabaseError: Se falhar ao obter contexto
        """
        try:
            # Buscar documentos da conversa
            results = self.collection.get(
                where={"conversation_id": conversation_id},
                limit=limit,
            )

            # Formatar resultados
            formatted_results = []

            if results and results["documents"]:
                for i in range(len(results["ids"])):
                    formatted_results.append(
                        {
                            "id": results["ids"][i],
                            "text": results["documents"][i],
                            "metadata": results["metadatas"][i],
                        }
                    )

            logger.info(
                "[SUCCESS] Context retrieved from ChromaDB (conv_id=%s, count=%s)",
                conversation_id,
                len(formatted_results),
            )

            return formatted_results

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(
                "[ERROR] Failed to get context from ChromaDB: %s",
                e,
                exc_info=True,
                extra={"conversation_id": conversation_id},
            )
            raise VectorDBError(f"Failed to get context: {e}", original_error=e)

    def delete_conversation(self, conversation_id: str) -> int:
        """
        Deletar todos os documentos de uma conversa.

        Args:
            conversation_id: ID da conversa

        Returns:
            Número de documentos deletados

        Raises:
            DatabaseError: Se falhar ao deletar
        """
        try:
            # Obter IDs dos documentos
            results = self.collection.get(
                where={"conversation_id": conversation_id},
            )

            if not results or not results["ids"]:
                logger.warning("[WARNING] No documents found for conv_id=%s", conversation_id)
                return 0

            # Deletar documentos
            self.collection.delete(ids=results["ids"])

            count = len(results["ids"])
            logger.info("[SUCCESS] Context deleted from ChromaDB (conv_id=%s, count=%s)", conversation_id, count)

            return count

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(
                "[ERROR] Failed to delete context from ChromaDB: %s",
                e,
                exc_info=True,
                extra={"conversation_id": conversation_id},
            )
            raise VectorDBError(f"Delete failed: {e}", original_error=e)

    def count(self) -> int:
        """
        Contar total de documentos na coleção.

        Returns:
            Total de documentos
        """
        return self.collection.count()

    def reset(self) -> None:
        """
        Limpar todos os dados da coleção.

        CUIDADO: Esta operação é irreversível!
        """
        try:
            # Deletar coleção
            self.client.delete_collection(name=self.collection.name)

            # Recriar coleção vazia
            self.collection = self.client.get_or_create_collection(
                name=self.collection.name, metadata={"description": "WhatsApp conversation contexts"}
            )

            logger.warning("[WARNING] ChromaDB collection reset: %s", self.collection.name)

        except Exception as e:  # noqa: BLE001 (blind exception)
            logger.error(f"[ERROR] Failed to reset ChromaDB: {e}", exc_info=True)
            raise VectorDBError(f"Reset failed: {e}", original_error=e)


# Singleton global
_chroma_client: ChromaClient | None = None


def get_chroma_client() -> ChromaClient:
    """
    Obter instância singleton do cliente ChromaDB.

    Returns:
        ChromaClient singleton
    """
    global _chroma_client

    if _chroma_client is None:
        _chroma_client = ChromaClient()
        logger.info("[INFO] ChromaClient initialized as singleton")

    return _chroma_client


def close_chroma_client() -> None:
    """Fechar cliente (cleanup)."""
    global _chroma_client
    if _chroma_client is not None:
        logger.info("[INFO] Closing ChromaClient")
        _chroma_client = None
