import os
from dotenv import load_dotenv
load_dotenv()

CONTEXT_PATH = os.getenv("CONTEXT_PATH", "/marcusan-attendance")

from fastapi import FastAPI, Request, Response, status
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import argparse

# =================================================================================================
# APP CONTEXT =====================================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan, root_path=CONTEXT_PATH)

# =================================================================================================
# RUN THE APP =====================================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()
    
    uvicorn.run("server:app", host=args.host, port=args.port)

# =================================================================================================
#67676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767676767
#HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHA