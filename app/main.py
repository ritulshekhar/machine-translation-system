from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.core.inference import engine
import json

app = FastAPI(title="Automotive MT Prototype")

# Templates setup
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/translate")
async def translate(text: str = Form(...), lang: str = Form(...)):
    return StreamingResponse(
        engine.generate_translation_stream(text, lang),
        media_type="text/event-stream"
    )

@app.post("/debug/tokenize")
async def tokenize(text: str = Form(...)):
    return engine.get_tokenization_steps(text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
