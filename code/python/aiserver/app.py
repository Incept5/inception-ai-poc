import asyncio
import traceback
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from bots.configured_bots import get_all_bots
from mylangchain.retriever_manager import retriever_manager
from routes.all_routers import include_all_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_all_bots(app)  # Initialize configured bots

    # Initialize the retriever_manager
    await retriever_manager.loader.initialize_client()

    # Start check_imports as a background task
    check_imports_task = asyncio.create_task(run_check_imports())

    yield  # The application runs here

    # Shutdown: Cancel any running tasks if needed
    check_imports_task.cancel()
    try:
        await check_imports_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

# Include all routers and wire them together
include_all_routers(app)

async def run_check_imports():
    try:
        await retriever_manager.check_imports()
    except Exception as e:
        # Print full stack trace
        print("An error occurred during import checking:")
        traceback.print_exc()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9871)