# RFC 8288 discovery relations — master plan §8.3, verbatim. The same
# five relations appear as <link> elements in every page head (Phase 1);
# tests/test_web_conf.py holds the two in parity. `always` so the header
# also rides on non-2xx responses. Vary: Accept because the same URL
# negotiates to Markdown (§8.2).
add_header Link '</.well-known/api-catalog>; rel="api-catalog", </openapi.json>; rel="service-desc"; type="application/vnd.oai.openapi+json", </agents.html>; rel="service-doc"; type="text/html", </llms.txt>; rel="describedby"; type="text/plain", </.well-known/ai-catalog.json>; rel="ai-catalog"; type="application/ai-catalog+json"' always;
add_header Vary Accept always;
