import os
import uvicorn

if __name__ == "__main__":
    # Get the PORT from environment variables (assigned by Railway), fallback to 8000 for local dev
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    
    print(f"[Startup] Starting Uvicorn on host 0.0.0.0, port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
