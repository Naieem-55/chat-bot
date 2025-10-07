"""Debug server to see full error."""
import sys
import traceback
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    import uvicorn
    from src.config import settings

    # Run with debug logging
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,  # Disable reload for debugging
        log_level="debug"
    )
except Exception as e:
    print(f"Error starting server: {e}")
    traceback.print_exc()
