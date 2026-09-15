# auth.md — Free Agentic Publication Digester

This file exists so automated clients can learn, without guessing, how
to authenticate to fapd.info. The answer is that you do not.

- **Audience:** any AI agent, crawler, or program.
- **Registration:** none. There are no accounts, API keys, OAuth
  clients, or registration endpoints, and none are planned.
- **Supported access:** anonymous HTTPS `GET` and `HEAD` for every
  published file, and anonymous JSON-RPC `POST` to the read-only MCP
  service at `/mcp`. Nothing else is accepted.
- **Credentials:** none are issued or read. Send none; an
  `Authorization` header is ignored.
- **What we ask in return:** identify yourself honestly in
  `User-Agent`, and use conditional requests (`If-None-Match`,
  `If-Modified-Since`). A per-address rate limit protects the shared
  server.
- **Start here:** `/llms.txt` · `/.well-known/api-catalog` ·
  `/agents.html`
