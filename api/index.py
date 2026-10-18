import hashlib
import json
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="IITM MCP Challenge Server", docs_url=None, redoc_url=None)

EXAM_EMAIL = "23f2001912@ds.study.iitm.ac.in"
TOOL_NAME = "solve_challenge"


def rpc_result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def rpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


@app.get("/")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "iitm-mcp-challenge"}


@app.post("/api/mcp")
async def mcp(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}, status_code=400)

    if not isinstance(body, dict) or body.get("jsonrpc") != "2.0" or not isinstance(body.get("method"), str):
        return JSONResponse(rpc_error(body.get("id") if isinstance(body, dict) else None, -32600, "Invalid Request"))

    method = body["method"]
    request_id = body.get("id")

    # JSON-RPC notifications must not produce a response body.
    if "id" not in body:
        return JSONResponse({}, status_code=202)

    if method == "initialize":
        return rpc_result(request_id, {
            "protocolVersion": body.get("params", {}).get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "iitm-mcp-challenge", "version": "1.0.0"},
        })

    if method == "ping":
        return rpc_result(request_id, {})

    if method == "tools/list":
        return rpc_result(request_id, {
            "tools": [{
                "name": TOOL_NAME,
                "description": "Solve the current exam challenge from the X-Exam-Challenge HTTP request header.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False,
                },
            }]
        })

    if method == "tools/call":
        params = body.get("params") or {}
        if params.get("name") != TOOL_NAME:
            return JSONResponse(rpc_error(request_id, -32602, "Unknown tool"))
        challenge = request.headers.get("x-exam-challenge")
        if challenge is None:
            return rpc_result(request_id, {
                "content": [{"type": "text", "text": "Missing X-Exam-Challenge header"}],
                "isError": True,
            })
        answer = hashlib.sha256(f"{challenge}:{EXAM_EMAIL}".encode("utf-8")).hexdigest()[:16]
        return rpc_result(request_id, {
            "content": [{"type": "text", "text": answer}],
            "isError": False,
        })

    return JSONResponse(rpc_error(request_id, -32601, "Method not found"))
