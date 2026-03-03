# Mobile Specialist Agent Playbook (Backend Context)

## Mission
The Mobile Specialist agent ensures that the BotDB backend provides robust and efficient data support for mobile consumers, prioritizing performance, reliability, and security for users on the go.

## Responsibilities
- **Mobile-Optimized APIs**: helping to design backend endpoints that are optimized for mobile network conditions, prioritizing payload size and latency.
- **Push Notification Support**: collaborating on the backend infrastructure for sending timely and relevant notifications to mobile users.
- **Security Check**: ensuring that mobile-facing endpoints and auth patterns are secure and follow mobile best practices.
- **Cross-Platform Consistency**: advocating for backend data structures that work seamlessly across both iOS and Android platforms.

## Best Practices
- **Payload Efficiency**: minimize data transfer to support users on potentially limited or unstable mobile connections.
- **Robustness**: ensure the backend can gracefully handle intermittent connectivity or unexpected mobile client behavior.
- **Communication**: keep mobile clients informed of system status and data changes through efficient polling or push mechanisms.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Data Flow](../docs/data-flow.md)

## Repository Starting Points
- `src/robbot/api/`: the primary location for exposing services to mobile consumers.
- `src/robbot/services/communication/`: where notification and messaging logic lives.

## Key Files
- `src/robbot/schemas/auth.py`: critical for ensuring secure mobile authentication.
- `src/robbot/api/main.py`: entry point for mobile client interaction.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Security Notes](../docs/security.md)

## Collaboration Checklist
1. Review backend changes for their impact on mobile performance and reliability.
2. Collaborate on the design of mobile-specific API endpoints.
3. Verify that push notifications and realtime updates are handled correctly.
