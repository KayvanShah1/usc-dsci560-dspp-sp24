import folium
from app.crud import get_well_data
from app.database import get_db
from app.settings import Path
from folium.plugins import MarkerCluster
from jinja2 import Environment, FileSystemLoader

db = get_db()


def generate_map_html():
    wells = get_well_data(db)

    center = wells.compute_center()
    w_geojson = wells.convert_to_geojson()

    # Create a Folium map centered at a specific location
    m = folium.Map(location=center, zoom_start=12)

    marker_cluster = MarkerCluster(name="marker_cluster", control=False).add_to(m)

    # Load the Jinja2 environment
    env = Environment(loader=FileSystemLoader(searchpath=Path.templates_dir))
    template = env.get_template("well_map_popup_template.html")

    # Add markers to the MarkerCluster layer from GeoJSON data
    for feature in w_geojson["features"]:
        properties = feature["properties"]
        coordinates = feature["geometry"]["coordinates"]
        popup_html = template.render(properties)
        folium.Marker(
            location=[coordinates[1], coordinates[0]],
            popup=folium.Popup(popup_html),
            tooltip="<strong>Well Name: </strong>" + properties["details"]["well_name"],
        ).add_to(marker_cluster)

    # Add tile mode and controller
    folium.TileLayer("cartodbpositron", name="Light mode", control=True).add_to(m)
    folium.TileLayer("cartodbdark_matter", name="Dark mode", control=True, show=True).add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)

    # Render the map as HTML
    return m._repr_html_()
