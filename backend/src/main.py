from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from routers import github, linkedin, chat

app = FastAPI()

# Static CV file serving
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
def root():
    return {"message": "Welcome to Tshimbiluni's AI-Powered Portfolio API"}

@app.get("/download-cv", response_class=FileResponse)
def download_cv():
    file_path = os.path.join(static_path, "Tshimbiluni_Nedambale_CV.pdf")
    return FileResponse(path=file_path, filename="Tshimbiluni_Nedambale_CV.pdf", media_type="application/pdf")

# Register all routers
app.include_router(github.router)
app.include_router(linkedin.router)
app.include_router(chat.router)
