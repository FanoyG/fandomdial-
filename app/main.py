import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat

app = FastAPI(
    title="CC Switchboard Engine",
    description="SOLID-compliant high-performance entertainment persona text and voice pipeline."
)

# Problem 10 Fix: Force open CORS validation paths before checking deployment links
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount system endpoint routers cleanly
app.include_router(chat.router)

@app.get("/health")
async def check_system_health():
    return {"status": "online", "application": "CC Switchboard Core"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
