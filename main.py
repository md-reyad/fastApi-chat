from typing import Union
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

# Import our QA system
from qa_system import get_answer

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat")
def redirect_submit():
    # Redirect GET requests to /submit to the home page
    return RedirectResponse(url="/")


@app.post("/chat")
async def submit_form(message: str = Form(...)):
    # Process the question using our QA system
    answer = get_answer(message)
    
    # Return JSON response for AJAX
    return JSONResponse(content={"response": answer.text})