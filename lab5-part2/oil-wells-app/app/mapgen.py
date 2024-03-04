import folium
from folium.plugins import MarkerCluster
from app.crud import get_all_clean
from app.database import get_db

db = get_db()


def generate_map_html():
    wells = get_all_clean(db)

    center = wells.compute_center()
    w_geojson = wells.convert_to_geojson()

    # Create a Folium map centered at a specific location
    m = folium.Map(location=center, zoom_start=12)

    marker_cluster = MarkerCluster(name="marker_cluster", control=False).add_to(m)

    # folium.GeoJson(
    #     w_geojson,
    #     tooltip=folium.GeoJsonTooltip(fields=["well_name"], aliases=["Well Name"]),
    #     popup=folium.GeoJsonPopup(
    #         fields=[
    #             "api_no",
    #             "closest_city",
    #             "county",
    #             "latest_barrels_of_oil_produced",
    #             "latest_mcf_of_gas_produced",
    #             "link",
    #             "operator",
    #             "well_name",
    #             "well_status",
    #             "well_type",
    #         ],
    #         aliases=[
    #             "API Number",
    #             "Closest City",
    #             "County",
    #             "Latest Barrels of Oil Produced",
    #             "Latest MCF of Gas Produced",
    #             "Link",
    #             "Operator",
    #             "Well Name",
    #             "Well Status",
    #             "Well Type",
    #         ],
    #     ),
    # ).add_to(m)

    marker_cluster = MarkerCluster().add_to(m)

    # Add markers to the MarkerCluster layer from GeoJSON data
    for feature in w_geojson["features"]:
        properties = feature["properties"]
        coordinates = feature["geometry"]["coordinates"]
        popup_html = f"""
            <div style="width: 250px;">
                <h4>{properties['well_name']}</h4><br>
                <b>API Number:</b> {properties['api_no']}<br>
                <b>Closest City:</b> {properties['closest_city']}<br>
                <b>County:</b> {properties['county']}<br>
                <b>Latest Barrels of Oil Produced:</b> {properties['latest_barrels_of_oil_produced']}<br>
                <b>Latest MCF of Gas Produced:</b> {properties['latest_mcf_of_gas_produced']}<br>
                <b>Operator:</b> {properties['operator']}<br>
                <b>Well Status:</b> {properties['well_status']}<br>
                <b>Well Type:</b> {properties['well_type']}<br>
                <b>Source:</b> <a href="{properties['link']}" target="_blank">Link</a><br>
            </div>
        """
        folium.Marker(
            location=[coordinates[1], coordinates[0]],
            popup=folium.Popup(popup_html),
            tooltip="<strong>Well Name: </strong>" + properties["well_name"],
        ).add_to(marker_cluster)

    # Add tile mode and controller
    folium.TileLayer("cartodbpositron", name="Light mode", control=True).add_to(m)
    folium.TileLayer("cartodbdark_matter", name="Dark mode", control=True, show=True).add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)

    # Render the map as HTML
    return m._repr_html_()
