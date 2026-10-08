"""A D3-Geo backed interactive map widget for Jupyter."""

from __future__ import annotations

import inspect
import json
import pathlib
import warnings
from typing import TYPE_CHECKING

import anywidget
import traitlets

from .jgis import read_layers

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_DEFAULT_COLOR = "#3388ff"


class Map(anywidget.AnyWidget):
    """Defines a D3-Geo backed map widget for Jupyter notebooks.

    Args:
        center (tuple): center of the map (longitude, latitude).
            **Not implemented yet.**
        zoom (float): The zoom level of the map. **Not implemented yet.**
        projection (Projection or str): The projection to use for the map. If a
            string is provided, it will be used to create a Projection object.
            Defaults to "geoEqualEarth".
        graticule (bool): Whether to show the graticule.
        border (bool): Whether to draw a border frame around the map.
        basemap (str): The basemap to use. **Not implemented yet. Currently
            defaults to Natural Earth small scale borders.**
        hamburger (bool): Whether to show the hamburger menu.
            **Not implemented yet.**
        dynamic (str or bool): Whether the map is dynamically draggable. Value
            can be True, False, "pan", or "rotate". If True, the map will be
            draggable, and choose a default mode. If False, the map will not be
            draggable. If "pan", the map will pan post-projection. If "rotate",
            the map will be rotatable pre-projection.
    """

    _esm = pathlib.Path(__file__).parent / "static" / "widget.js"

    projection = traitlets.Unicode("geoEqualEarth").tag(sync=True)
    border = traitlets.Bool(default_value=True).tag(sync=True)
    graticule = traitlets.Bool(default_value=False).tag(sync=True)
    projection_rotate = traitlets.Tuple(
        traitlets.Float(), traitlets.Float(), traitlets.Float(), default_value=(0, 0, 0)
    ).tag(sync=True)
    projection_center = traitlets.Tuple(
        traitlets.Float(), traitlets.Float(), allow_none=True, default_value=None
    ).tag(sync=True)
    projection_precision = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_parallels = traitlets.Tuple(
        traitlets.Float(), traitlets.Float(), allow_none=True, default_value=None
    ).tag(sync=True)
    projection_a = traitlets.Float(allow_none=True, default_value=None).tag(sync=True)
    projection_alpha = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_b = traitlets.Float(allow_none=True, default_value=None).tag(sync=True)
    projection_coefficient = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_cutoff_latitude = traitlets.Float(
        allow_none=True, default_value=None
    ).tag(sync=True)
    projection_distance = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_fraction = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_gamma = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_inflation = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_k = traitlets.Float(allow_none=True, default_value=None).tag(sync=True)
    projection_lobes = traitlets.Union(
        [traitlets.Int(), traitlets.List()], allow_none=True, default_value=None
    ).tag(sync=True)
    projection_parallel = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_poleline = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_psi_max = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_radius = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_ratio = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_shift = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_spacing = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    projection_tilt = traitlets.Float(allow_none=True, default_value=None).tag(
        sync=True
    )
    layers = traitlets.List().tag(sync=True)
    dynamic = traitlets.Unicode("pan").tag(sync=True)
    basemap = traitlets.Unicode("").tag(sync=True)
    hamburger = traitlets.Bool(default_value=True).tag(sync=True)

    class Export:
        """Export helpers for a map."""

        def __init__(self, map_widget: Map) -> None:
            self._map = map_widget

        def svg(self, path: str | pathlib.Path) -> None:
            """Export the map as an SVG file.

            **Not implemented yet.**
            """
            raise NotImplementedError

    # The many options mirror the documented public API; everything past
    # `projection` is keyword-only so the boolean flags can't be mixed up.
    # Each projection option is copied onto its own synced trait, one statement
    # apiece, which pushes the statement count past the limit.
    def __init__(  # noqa: PLR0913, PLR0915
        self,
        center: tuple[float, float] = (0.0, 0.0),
        zoom: float = 1.0,
        projection: Projection | str | None = None,
        *,
        graticule: bool = False,
        border: bool = True,
        basemap: bool | str = False,
        hamburger: bool = True,
        dynamic: bool | str = True,
    ) -> None:
        if center != (0.0, 0.0) or zoom != 1.0:
            raise NotImplementedError
        if projection is None:
            projection = Projection()
        elif isinstance(projection, str):
            projection = Projection(projection)
        super().__init__()
        self.projection = projection.name
        self.projection_rotate = projection.rotate
        self.projection_center = projection.center
        self.projection_precision = projection.precision
        self.projection_parallels = projection.parallels
        self.projection_a = projection.a
        self.projection_alpha = projection.alpha
        self.projection_b = projection.b
        self.projection_coefficient = projection.coefficient
        self.projection_cutoff_latitude = projection.cutoff_latitude
        self.projection_distance = projection.distance
        self.projection_fraction = projection.fraction
        self.projection_gamma = projection.gamma
        self.projection_inflation = projection.inflation
        self.projection_k = projection.k
        self.projection_lobes = projection.lobes
        self.projection_parallel = projection.parallel
        self.projection_poleline = projection.poleline
        self.projection_psi_max = projection.psi_max
        self.projection_radius = projection.radius
        self.projection_ratio = projection.ratio
        self.projection_shift = projection.shift
        self.projection_spacing = projection.spacing
        self.projection_tilt = projection.tilt
        self.border = border
        self.graticule = graticule
        if basemap in {"naturalearth", True}:
            self.basemap = "naturalearth"
        elif basemap is False:
            self.basemap = ""
        else:
            msg = "basemap must be 'naturalearth', True, or False"
            raise ValueError(msg)
        self.hamburger = hamburger
        if dynamic is True or dynamic is False:
            # Always "pan" for now; ideally the default mode would depend on
            # whether the projection is globe-like.
            self.dynamic = "pan" if dynamic else "none"
        elif dynamic == "pan":
            self.dynamic = "pan"
        elif dynamic == "rotate":
            self.dynamic = "rotate"
        else:
            msg = "dynamic must be True, False, 'pan', or 'rotate'"
            raise ValueError(msg)
        self.export = Map.Export(self)

    def add(self, layer: Layer) -> None:
        """Add a layer to the map. Only GeoJSON layers are supported so far."""
        self.layers = [*self.layers, layer.data]

    def add_from_jgis(
        self,
        jgis: pathlib.Path | str,
        layers: list | str | None = None,
        style: VectorStyle | None = None,
    ) -> None:
        """Add all compatible layers from a .jGIS file to the map.

        Args:
            jgis (pathlib.Path or str): The path to the .jGIS file.
            style (VectorStyle, optional): The style to apply to all layers. If None,
                the default style will be used. Defaults to None. Note that pulling
                a style from the .jGIS file is not supported yet, so this is the only
                way to style layers from a .jGIS file.
            layers (list or str, optional): The names of the layers to add.
                If None, all compatible layers will be added. Defaults to None.
        """
        if isinstance(layers, str):
            layers = [layers]
        layers_info = read_layers(jgis)
        for layer in layers_info:
            if layers is not None and layer["name"] not in layers:
                continue
            if not layer["visible"]:
                continue
            # Remote sources (layer["url"]) aren't supported yet.
            data = layer["data"] if layer["data"] is not None else layer["path"]
            if (
                layer["type"] == "VectorLayer"
                and layer["source_type"] == "GeoJSONSource"
                and data is not None
            ):
                self.add(GeoJSON(data, name=layer["name"], style=style))
                if layer["has_filters"]:
                    pass
            else:
                msg = (
                    f"Skipping layer {layer['name']} of type {layer['type']} "
                    f"and source type {layer['source_type']} because it is not "
                    "yet implemented."
                )
                warnings.warn(msg, stacklevel=2)

    def remove(self, layer: Layer) -> None:
        """Remove a layer from the map.

        **Not implemented yet.**
        """
        raise NotImplementedError


Map.__signature__ = inspect.Signature(
    list(inspect.signature(Map.__init__).parameters.values())[1:]
)


class Projection:
    """Defines a D3-Geo projection for the map widget.

    Args:
        name (str): The name of the projection. Defaults to "geoEqualEarth". See
            `d3-geo <https://d3js.org/d3-geo/projection#geoProjection>`_,
            `d3-geo-projection <https://github.com/d3/d3-geo-projection>`_, and
            `d3-geo-polygon <https://github.com/d3/d3-geo-polygon>`_ for options.
        rotate (tuple): The rotation of the projection.
        center (tuple): The center of the projection.
        precision (float): The precision of the projection.
        *the following are projection-specific. Use the above linked documentation
            to determine which are applicable for your projection.*
        parallels (tuple): The parallels of the projection. Only applicable for
            conic projections.
        a (float): The a parameter. Only applicable for geoHufnagel.
        alpha (float): The alpha parameter. Only applicable for
            geoHyperelliptical and geoFoucautSinusoidal.
        b (float): The b parameter. Only applicable for geoHufnagel.
        coefficient (float): The coefficient. Only applicable for geoHammer.
        cutoff_latitude (float): The cutoff latitude. Only applicable for
            geoComplexLog.
        distance (float): The distance from the center of the sphere. Only
            applicable for geoSatellite.
        fraction (float): The fraction. Only applicable for geoBottomley.
        gamma (float): The gamma parameter. Only applicable for
            geoHyperelliptical.
        inflation (float): The inflation. Only applicable for geoWagner.
        k (float): The k parameter. Only applicable for geoHyperelliptical,
            geoImago, and geoImagoBlock.
        lobes (int or list): The lobes. Only applicable for interrupted
            projections, geoBerghaus, geoGingery, and geoHealpix.
        parallel (float): The parallel. Only applicable for projections with a
            single standard parallel, such as geoBonne.
        poleline (float): The pole line. Only applicable for geoWagner.
        psi_max (float): The psi max parameter. Only applicable for geoHufnagel.
        radius (float): The radius. Only applicable for geoAiry and geoGingery.
        ratio (float): The ratio. Only applicable for geoHill, geoHufnagel, and
            geoWagner.
        shift (float): The shift. Only applicable for geoImago.
        spacing (float): The spacing. Only applicable for geoLagrange.
        tilt (float): The tilt. Only applicable for geoSatellite.
    """

    # Each projection-specific option from d3-geo-projection and d3-geo-polygon
    # is its own keyword-only argument, mirroring the documented public API.
    def __init__(  # noqa: PLR0913
        self,
        name: str = "geoEqualEarth",
        rotate: tuple[float, float, float] = (0, 0, 0),
        center: tuple[float, float] | None = None,
        precision: float | None = None,
        parallels: tuple[float, float] | None = None,
        *,
        a: float | None = None,
        alpha: float | None = None,
        b: float | None = None,
        coefficient: float | None = None,
        cutoff_latitude: float | None = None,
        distance: float | None = None,
        fraction: float | None = None,
        gamma: float | None = None,
        inflation: float | None = None,
        k: float | None = None,
        lobes: int | list | None = None,
        parallel: float | None = None,
        poleline: float | None = None,
        psi_max: float | None = None,
        radius: float | None = None,
        ratio: float | None = None,
        shift: float | None = None,
        spacing: float | None = None,
        tilt: float | None = None,
    ) -> None:
        self.name = name
        self.rotate = tuple(rotate)
        self.center = center
        self.precision = precision
        self.parallels = parallels
        self.a = a
        self.alpha = alpha
        self.b = b
        self.coefficient = coefficient
        self.cutoff_latitude = cutoff_latitude
        self.distance = distance
        self.fraction = fraction
        self.gamma = gamma
        self.inflation = inflation
        self.k = k
        self.lobes = lobes
        self.parallel = parallel
        self.poleline = poleline
        self.psi_max = psi_max
        self.radius = radius
        self.ratio = ratio
        self.shift = shift
        self.spacing = spacing
        self.tilt = tilt


class VectorStyle:
    """Style for vector features.

    Each attribute may be a constant or a callable that receives a feature's
    properties and returns the value for that feature.

    Args:
        stroke_color (str or callable): The stroke color.
        fill_color (str or callable): The fill color.
        weight (float or callable): The stroke width.
        stroke_opacity (float or callable): The stroke opacity.
        fill_opacity (float or callable): The fill opacity.
    """

    def __init__(
        self,
        stroke_color: str | Callable[[dict], str] = "#000000",
        fill_color: str | Callable[[dict], str] = "#ffffff",
        weight: float | Callable[[dict], float] = 3,
        stroke_opacity: float | Callable[[dict], float] = 1.0,
        fill_opacity: float | Callable[[dict], float] = 1.0,
    ) -> None:
        self.stroke_color = stroke_color
        self.fill_color = fill_color
        self.weight = weight
        self.stroke_opacity = stroke_opacity
        self.fill_opacity = fill_opacity

    def resolve(self, properties: dict) -> dict:
        """Return the concrete style for one feature.

        Callables receive the feature's properties.
        """
        return {
            attribute: value(properties) if callable(value) else value
            for attribute, value in vars(self).items()
        }


class Layer:
    """Base class for all layers in the map widget.

    Args:
        name (str): The name of the layer.
    """

    def __init__(self, name: str = "") -> None:
        self.name = name


class Point(Layer):
    """A point layer on the map.

    **Not implemented yet.**
    """

    def __init__(
        self,
        location: tuple[float, float],
        color: str = _DEFAULT_COLOR,
        name: str = "",
    ) -> None:
        raise NotImplementedError


class Polygon(Layer):
    """A polygon layer on the map.

    **Not implemented yet.**
    """

    def __init__(
        self,
        locations: Sequence[tuple[float, float]],
        color: str = _DEFAULT_COLOR,
        fill_color: str = _DEFAULT_COLOR,
        name: str = "",
    ) -> None:
        raise NotImplementedError


class Line(Layer):
    """A line layer on the map.

    **Not implemented yet.**
    """

    def __init__(
        self,
        locations: Sequence[tuple[float, float]],
        color: str = _DEFAULT_COLOR,
        name: str = "",
    ) -> None:
        raise NotImplementedError


class GeoJSON(Layer):
    """A GeoJSON layer on the map.

    Args:
        data (dict, str, or pathlib.Path): GeoJSON as a dict, a JSON string, or a
            path to a GeoJSON file.
        name (str): The name of the layer.
        style (VectorStyle): The style of the layer.
    """

    def __init__(
        self,
        data: dict | str | pathlib.Path,
        name: str = "",
        style: VectorStyle | None = None,
    ) -> None:
        super().__init__(name)
        if isinstance(data, pathlib.Path):
            data = json.loads(data.read_text())
        elif isinstance(data, str):
            if data.strip().startswith("{"):
                data = json.loads(data)
            elif pathlib.Path(data).exists():
                data = json.loads(pathlib.Path(data).read_text())
            else:
                msg = f"data string is not a valid JSON or file path: {data}"
                raise ValueError(msg)
        elif not isinstance(data, dict):
            msg = "data must be a dict, str, or pathlib.Path"
            raise TypeError(msg)
        style = style or VectorStyle()
        features = []
        for f in data.get("features", []):
            props = f.get("properties") or {}
            features.append(
                {
                    **f,
                    "properties": {
                        **props,
                        "__ipyd3geo_style__": style.resolve(props),
                    },
                }
            )
        self.data = {**data, "features": features}


class GeoData(Layer):
    """A GeoDataFrame (such as from geopandas) layer on the map.

    **Not implemented yet.**
    """

    def __init__(self, data: object, name: str = "") -> None:
        raise NotImplementedError


class Raster(Layer):
    """A local raster layer on the map.

    **Not implemented yet.**
    """

    def __init__(self, data: str | pathlib.Path, name: str = "") -> None:
        raise NotImplementedError


class TileService(Layer):
    """Raster tiles from a service.

    **Not implemented yet.**
    """

    def __init__(self, url: str, name: str = "") -> None:
        raise NotImplementedError


if __name__ == "__main__":
    pass
