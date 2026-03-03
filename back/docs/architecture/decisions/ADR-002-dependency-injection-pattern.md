# ADR-001: Dependency Injection Pattern

**Status:** IMPLEMENTED  
**Date:** 2026-01-15  
**Context:** Rampant Singleton Anti-Pattern (Issue #1)  
**Affected Components:** main.py, api/v1/dependencies.py, config/container.py

---

## Problem

The codebase scattered multiple singleton functions across different modules:
- `get_conversation_orchestrator()` in services
- `get_gemini_client()` in adapters
- `get_redis_pool()` in infra
- `get_chroma_client()` in infra
- `get_queue_manager()` in infra

**Issues with this approach:**
1. **Global State Coupling:** Services depend on global state, making them hard to test
2. **Implicit Dependencies:** Constructor signatures don't show what a service needs
3. **Temporal Coupling:** Order of initialization matters
4. **Difficult Mocking:** Hard to inject test doubles in unit tests
5. **Scattered Initialization:** App startup logic spread across multiple modules

---

## Decision

Implement a **Centralized DIContainer** pattern:

1. **Single Container Class** (`config/container.py`)
   - One place for all dependency creation
   - Initialized once at FastAPI startup
   - Manages full lifecycle of all dependencies

2. **Constructor Injection**
   - Services receive dependencies via `__init__` parameters
   - Explicit dependencies in code
   - Enables easy mocking for tests

3. **FastAPI Depends()**
   - Container injected into endpoints via `Depends(get_container_dep)`
   - Services passed to handlers via explicit `get_*` functions
   - Type-safe with mypy

4. **Async Initialization**
   - Container initialized in FastAPI lifespan context
   - Proper async/await support
   - Graceful shutdown on app stop

---

## Implementation

### 1. DIContainer Class
```python
# config/container.py
class DIContainer:
    async def initialize(self) -> None:
        # Initialize all dependencies
        self._llm = GeminiLLMProvider(...)
        self._vector_store = ChromaVectorStore(...)
        self._waha = WAHAIntegration(...)
        
    def get_llm_provider(self) -> LLMProvider:
        return self._llm
```

### 2. Main App Initialization
```python
# main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_container(settings)  # Startup
    yield
    await shutdown_container()  # Shutdown
```

### 3. FastAPI Dependency Injection
```python
# api/v1/dependencies.py
async def get_container_dep() -> DIContainer:
    return get_global_container()

# In endpoints:
@app.post("/messages")
async def handle_message(
    container: DIContainer = Depends(get_container_dep),
    db: Session = Depends(get_db),
):
    llm = container.get_llm_provider()
    # Use LLM...
```

### 4. Service Constructor DI
```python
# services/lead_service.py
class LeadService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LeadRepository(db)
```

---

## Benefits

✅ **Testability:** Easy to inject mock dependencies  
✅ **Explicit Contracts:** Dependencies visible in constructors  
✅ **Single Responsibility:** Container manages one thing: dependencies  
✅ **Composability:** Mix and match implementations (Gemini vs Claude)  
✅ **No Global State:** Each app instance has isolated container  

---

## Trade-offs

⚠️ **Verbosity:** Need to pass session/LLM through function parameters  
⚠️ **One-time Setup:** Container initialization overhead at startup  

---

## Related ADRs

- ADR-003: Session Dependency Injection
- ADR-002: Repository Interface Pattern

---

## References

- [Dependency Injection Pattern](https://en.wikipedia.org/wiki/Dependency_injection)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Loose Coupling with DI](https://stackoverflow.com/questions/130794/what-is-dependency-injection)
