from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gpt4all import GPT4All
import os

app = FastAPI(title="Paul Graham Chat API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the model
model = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.on_event("startup")
async def startup_event():
    global model
    print("Initializing GPT4All model...")
    model = GPT4All("ggml-gpt4all-j-v1.3-groovy")
    print("Model initialized!")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not model:
        raise HTTPException(status_code=503, detail="Model not initialized")
    
    try:
        response = model.generate(
            prompt=request.message,
            max_tokens=200,
            temp=0.7,
            top_k=40,
            top_p=0.9,
            repeat_penalty=1.1
        )
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_initialized": model is not None} 