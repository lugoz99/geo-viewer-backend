from fastapi import FastAPI , Request 
app = FastAPI()


@app.get("/health")
async def health_check(request:Request):
    
    return {"status": "ok"}

