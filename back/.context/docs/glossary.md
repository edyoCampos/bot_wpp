# Glossary & Domain Concepts

## Core Business Entities
- **Lead**: A potential patient captured from WhatsApp. Leads have a maturity level (Cold, Warm, Hot) and a source.
- **Conversation**: A thread of messages between a Lead and the Bot/Human. Conversations track current status (Handling, Waiting, Handoff) and metadata.
- **Message**: Individual units of communication stored in the history.
- **Maturity**: A metric that indicates how close a lead is to scheduling an appointment.
- **Tag**: Metadata assigned to conversations or leads for categorization and reporting.

## Technical Concepts
- **WAHA**: WhatsApp HTTP API, the engine that powers the WhatsApp integration.
- **RQ (Redis Queue)**: The job processing system used for asynchronous tasks.
- **Spin Selling**: The sales methodology (Situation, Problem, Implication, Need-payoff) implemented in the AI logic.
- **RAG (Retrieval-Augmented Generation)**: The technique used to provide current clinic context to the LLM.
- **Drift**: A state where the database schema desynchronizes from the SQLAlchemy models.

## Type Definitions & Interfaces
- `LeadModel`: SQLAlchemy model representing the lead in PostgreSQL.
- `ConversationModel`: SQLAlchemy model for conversation state.
- `MessageSchema`: Pydantic schema for message data validation.
- `SPINStrategy`: Interface or logic for the SPIN-selling conversation flow.

## Enumerations
- `LeadStatus`: Active, Passive, Converted, etc.
- `ConversationStatus`: Bot, Human, Closed.
- `InteractionType`: User message, Bot response, System note.

## personae / Actors
- **Bot (Robbot)**: The automated responder qualifying leads.
- **Secretary / Human Agent**: The clinical staff who takes over when the bot escalates or finishes qualification.
- **Patient / Lead**: The user interacting via WhatsApp.
