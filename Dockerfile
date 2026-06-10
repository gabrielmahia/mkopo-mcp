# mkopo-mcp — Dockerfile for Glama sandbox build and evaluation
# Glama uses this to run security checks and assign quality/security scores.
#
# Local usage:
#   docker build -t mkopo-mcp .
#   docker run mkopo-mcp

FROM python:3.11-slim

LABEL org.opencontainers.image.title="mkopo-mcp"
LABEL org.opencontainers.image.description="MCP server for alternative credit scoring in Kenya using M-PESA behavioral signals"
LABEL org.opencontainers.image.source="https://github.com/gabrielmahia/mkopo-mcp"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="Gabriel Mahia <contact@aikungfu.dev>"

# Non-root for security
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir mkopo-mcp

USER mcpuser

# MCP servers use stdio transport
ENTRYPOINT ["mkopo-mcp"]
