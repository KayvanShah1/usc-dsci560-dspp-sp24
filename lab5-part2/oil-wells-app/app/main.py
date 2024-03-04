from app.settings import Path, config
from app.mapgen import generate_map_html
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url="/openapi.json",
    description="Oil Wells Analysis and Visualization",
)

# Handle CORS protection
origins = config.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Static Files and Templates
templates = Jinja2Templates(directory=Path.templates_dir)
app.mount("/static", StaticFiles(directory=config.STATIC_ROOT), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    map_html = generate_map_html()
    return templates.TemplateResponse("index.html", {"request": request, "map_html": map_html})


# Catch-all route to redirect any incorrect routes to the home page
@app.get("/{path:path}")
async def catch_all(request: Request, path: str):
    return RedirectResponse(url="/", status_code=303)
