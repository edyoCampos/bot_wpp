# Data Flow & Integrations

Data in BotDB flows from external triggers (WhatsApp messages) through multiple processing stages, including filtering, queueing, AI analysis, and response generation, finally returning to the user via WhatsApp.

## Module Dependencies
- **`src\\robbot\\api`** → `services`, `infra`, `schemas`, `common`
- **`src\\robbot\\infra\\jobs`** → `services`, `infra`, `common`
- **`src\\robbot\\services`** → `infra`, `domain`, `common`
- **`src\\robbot\\infra\\persistence`** → `domain`, `common`

## Service Layer
Key services facilitating data flow:
- **`MessageFilterService`**: Determines if an incoming message should be processed.
- **`QueueService`**: Manages the enqueuing of jobs to Redis.
- **`ConversationOrchestrator`**: Coordinates the retrieval of context, LLM interaction, and state management.
- **`LLMClient`**: Interface for interacting with Groq and Gemini.
- **`WAHACoreService`**: Handles low-level HTTP communication with the WAHA API.

## High-level Flow
Incoming WhatsApp messages follow this pipeline:
1.  **Ingestion**: `message_polling_job` fetches messages from the WAHA API.
2.  **Filtering**: `MessageFilterService` checks if the message is from an authorized sender and hasn't been processed yet.
3.  **Enqueuing**: If valid, the message is enqueued via `QueueService` to the `messages` queue in Redis.
4.  **Processing**: An RQ worker picks up the `process_message_job`.
5.  **Context Retrieval**: `ConversationOrchestrator` fetches lead details from Postgres and relevant history from ChromaDB.
6.  **AI Analysis**: The orchestrator sends the context to an LLM (Groq/Gemini).
7.  **Response Generation**: The LLM generates a response based on the SPIN Selling methodology.
8.  **Action**: The orchestrator sends the generated response back to the user via `WAHACoreService`.
9.  **Storage**: The interaction is recorded in the Postgres `conversations` table and the ChromaDB vector store.

## Internal Movement
- **Redis Queues**: Used for decoupling ingestion from processing.
- **SQLAlchemy (Postgres)**: Used for structured data (leads, conversations).
- **ChromaDB**: Used for unstructured conversation history and embeddings.

## External Integrations
| Integration | Purpose | Auth | Payload | Retry |
|-------------|---------|------|---------|-------|
| **WAHA** | WhatsApp messaging | Session name | JSON webhooks/polling | Exponential backoff |
| **Groq** | Llama 3 LLM | API Key | Chat Completion JSON | Basic re-enqueue |
| **Gemini** | LLM Alternate | API Key | Chat Completion JSON | Basic re-enqueue |

## Observability & Failure Modes
- **Logs**: Every job logs its state (STARTED, PARTIAL, SUCCESS, FAILED).
- **Unique Constraints**: Prevents duplicate conversation creation.
- **Manual Drift Document**: Recent database schema desynchronization is documented in [`database_drift.md`](./database_drift.md).

## Cross-References
- [Architecture Notes](./architecture.md)
- [Project Overview](./project-overview.md)
