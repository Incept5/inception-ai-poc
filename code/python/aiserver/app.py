import asyncio
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from bots.configured_bots import get_configured_bots, get_bot_dependency, get_all_bots
from bots.system_bots import SystemBotManager
from mylangchain.retriever_manager import retriever_manager
from routes import combined_routes  # Import the combined_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize bot instances
    app.state.configured_bots = get_configured_bots()
    SystemBotManager.initialize_system_bots(app)

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

# Include the combined routes
app.include_router(combined_routes)


async def run_check_imports():
    try:
        await retriever_manager.check_imports()
    except Exception as e:
        print(f"An error occurred during import checking: {e}")
        # You might want to log this error or handle it in some other way


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9871)