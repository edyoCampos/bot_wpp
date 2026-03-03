---
slug: deployment
category: operations
generatedAt: 2026-02-09T15:05:24.518Z
relevantFiles:
  - docker-compose.yml
  - Dockerfile
---

# How do I deploy this project?

## Deployment

### Docker

This project includes Docker configuration.

```bash
docker build -t app .
docker run -p 3000:3000 app
```
