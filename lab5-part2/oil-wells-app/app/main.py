from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import folium

from app.settings import config, Path

app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url="/openapi.json",
    description="Firebase Realtime Database RestFul API Emulator",
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


templates = Jinja2Templates(directory=Path.templates_dir)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Create a Folium map centered at a specific location
    m = folium.Map(location=[51.5074, -0.1278], zoom_start=15)

    # Add a marker to the map
    folium.Marker(location=[51.5074, -0.1278], popup="London").add_to(m)

    # Render the map as HTML
    map_html = m._repr_html_()
    return templates.TemplateResponse("index.html", {"request": request, "map_html": map_html})


# Static Files and Templates
app.mount("/static", StaticFiles(directory=config.STATIC_ROOT), name="static")
