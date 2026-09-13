# Ruling D6: CORS `*` on the public, credential-free machine-readable
# files only — never on /mcp. `always` so a signposted 404 carries it.
add_header Access-Control-Allow-Origin "*" always;
