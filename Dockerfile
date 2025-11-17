FROM python:3.10.8-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt || true

ENV MCP_ENDPOINT=""

CMD ["python", "mcp_pipe.py", "lxdata.py"]