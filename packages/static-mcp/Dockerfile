# static-mcp — a read-only MCP server over a directory of static files.
# Stdlib only; no dependencies to install.
#
# Run with the site mounted read-only at /srv/site and the manifest
# directory mounted read-only at /etc/static-mcp. The container binds
# 0.0.0.0:8080 because a reverse proxy on the same internal network is
# the only expected client; the CLI's own default stays 127.0.0.1.
FROM python:3.12-slim
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin staticmcp
COPY src/ /opt/static-mcp/src/
ENV PYTHONPATH=/opt/static-mcp/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 --start-period=5s \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).status == 200 else 1)"]
ENTRYPOINT ["python", "-m", "static_mcp", "serve", "--root", "/srv/site", "--host", "0.0.0.0", "--port", "8080"]
CMD ["--manifest", "/etc/static-mcp/manifest.json"]
