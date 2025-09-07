import httpx
from fastapi import FastAPI, Request, Response

app = FastAPI(title="AI Gateway")

# Define the internal locations of our backend AI services
SERVICE_URLS = {
    "asr": "http://asr:8000/infer",
    "vision": "http://vision:8000/infer",
    "docqa": "http://docqa:8000/ask",
    "forecaster": "http://forecaster:8000/forecast",
}

@app.post("/route/{service_name}")
async def route_request(service_name: str, request: Request):
    """
    Receives a request, finds the correct backend service,
    and forwards the request body and headers to it.
    """
    if service_name not in SERVICE_URLS:
        return Response(content=f"Service '{service_name}' not found.", status_code=404)

    backend_url = SERVICE_URLS[service_name]

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Build a new request that mirrors the original one
        backend_request = client.build_request(
            method=request.method,
            url=backend_url,
            headers=request.headers.raw,
            content=await request.body(),
        )

        try:
            # Send the mirrored request to the backend service
            backend_response = await client.send(backend_request)

            # Return the response from the backend service back to the original caller
            return Response(
                content=backend_response.content,
                status_code=backend_response.status_code,
                headers=dict(backend_response.headers),
            )
        except httpx.RequestError as e:
            error_message = f"Error communicating with backend service '{service_name}': {e}"
            return Response(content=error_message, status_code=502) # 502 Bad Gateway

@app.get("/healthz")
def healthz():
    return {"status": "ok", "configured_services": list(SERVICE_URLS.keys())}