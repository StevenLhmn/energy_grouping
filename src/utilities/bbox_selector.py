"""
bbox_selector.py

Interactive bounding-box selector for Jupyter notebooks in VS Code.

Install once:
    pip install ipyleaflet ipywidgets

Usage in a notebook:
    from bbox_selector import BBoxSelector

    selector = BBoxSelector()
    selector.display()

    # Draw a rectangle on the map, then run:
    selector.bbox

The bbox is returned as:
    (min_lon, min_lat, max_lon, max_lat)

You can also get it as a dict:
    selector.bbox_dict
"""

from ipyleaflet import Map, DrawControl, basemaps


class BBoxSelector:
    """Interactive map for selecting one geographic bounding box."""

    def __init__(self, center=(50.8, 10.0), zoom=5, height="600px"):
        self.map = Map(
            center=center,
            zoom=zoom,
            basemap=basemaps.OpenStreetMap.Mapnik,
            layout={"height": height},
        )

        self.draw_control = DrawControl(
            rectangle={
                "shapeOptions": {
                    "color": "#3388ff",
                    "fillOpacity": 0.15,
                }
            },
            polygon={},
            polyline={},
            circle={},
            circlemarker={},
            marker={},
        )

        self._bbox = None
        self._layer = None

        self.draw_control.on_draw(self._handle_draw)
        self.map.add(self.draw_control)

    def _handle_draw(self, target, action, geo_json):
        """Store the bbox whenever a rectangle is drawn."""
        if action == "created" and geo_json["geometry"]["type"] == "Polygon":
            coordinates = geo_json["geometry"]["coordinates"][0]

            lons = [p[0] for p in coordinates]
            lats = [p[1] for p in coordinates]

            self._bbox = (
                min(lons),
                min(lats),
                max(lons),
                max(lats),
            )

            # Keep only the newest rectangle.
            if self._layer is not None:
                try:
                    self.map.remove_layer(self._layer)
                except Exception:
                    pass

            self._layer = geo_json

    @property
    def bbox(self):
        """
        Return the selected bbox as:
            (min_lon, min_lat, max_lon, max_lat)

        Returns None until a rectangle has been selected.
        """
        return self._bbox

    @property
    def bbox_dict(self):
        """Return the selected bbox as a dictionary."""
        if self._bbox is None:
            return None

        min_lon, min_lat, max_lon, max_lat = self._bbox
        return {
            "min_lon": min_lon,
            "min_lat": min_lat,
            "max_lon": max_lon,
            "max_lat": max_lat,
        }

    def clear(self):
        """Clear the current selection."""
        self._bbox = None
        self._layer = None
        self.draw_control.clear()

    def display(self):
        """Display the interactive map in a Jupyter notebook."""
        return self.map

    def __repr__(self):
        if self._bbox is None:
            return "BBoxSelector(bbox=None)"
        return f"BBoxSelector(bbox={self._bbox!r})"
