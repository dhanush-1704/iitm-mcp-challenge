# IITM MCP Challenge Server

A minimal FastAPI MCP-compatible JSON-RPC endpoint for the IITM exam challenge.

## Endpoint

- MCP: `POST /api/mcp`
- Health: `GET /`

## Tool

Exactly one tool is exposed: `solve_challenge`. It has no required input properties.

For each `tools/call`, the server reads `X-Exam-Challenge` from that HTTP request's headers and returns the first 16 lowercase hexadecimal characters of:

```text
SHA-256("<challenge>:23f2001912@ds.study.iitm.ac.in")
```

The challenge is read from the request header, not from the JSON body.

## MCP flow

Supports `initialize`, notifications (including `notifications/initialized`), `ping`, `tools/list`, and `tools/call`.

## Deploy

Connect this public GitHub repository to a Vercel project using the Python runtime. After deployment, use `https://YOUR-VERCEL-DOMAIN/api/mcp` as the MCP URL.
