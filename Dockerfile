FROM python:3.11-slim
RUN pip install --no-cache-dir mkopo-mcp
CMD ["mkopo-mcp"]
