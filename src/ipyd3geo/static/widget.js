import * as d3geo from "https://esm.sh/d3-geo@3.1.1";
import * as d3geoProjection from "https://esm.sh/d3-geo-projection@4.0.0";
import * as d3geoPolygon from "https://esm.sh/d3-geo-polygon@2.0.1";
import { zoom } from "https://esm.sh/d3-zoom@3.0.0";
import { select } from "https://esm.sh/d3-selection@3.0.0";

const d3 = { ...d3geo, ...d3geoProjection, ...d3geoPolygon };

async function render({ model, el }) {
  if (model.get("hamburger")) {
    const menuButton = document.createElement("button");
    menuButton.textContent = "☰";
    menuButton.style.display = "block";
    el.appendChild(menuButton);
    const menuContent = document.createElement("div");
    menuContent.style.display = "none";
    menuContent.style.position = "absolute";
    menuContent.style.color = "black";
    menuContent.style.cursor = "pointer";
    menuContent.style.backgroundColor = "lightgray";
    menuContent.style.padding = "5px";
    menuContent.style.border = "1px solid black";

    const exportSvgButton = document.createElement("div");
    exportSvgButton.textContent = "Export SVG";
    exportSvgButton.addEventListener("click", () => {
      const svgString = new XMLSerializer().serializeToString(svg);
      const blob = new Blob([svgString], { type: "image/svg+xml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "map.svg";
      a.click();
      URL.revokeObjectURL(url);
    });
    menuContent.appendChild(exportSvgButton);

    //TODO this is the wrong approach to toggling graticule visibility, bc it doesn't toggle on if it didn't start visible.
    const graticuleButton = document.createElement("div");
    graticuleButton.textContent = `Toggle Graticule${model.get("graticule") ? " ✓" : ""}`;
    graticuleButton.addEventListener("click", () => {
      if (graticule) {
        const isShown = graticule.style.display === "none";
        graticule.style.display = isShown ? "block" : "none";
        model.set("graticule", isShown);
        model.save_changes();
        graticuleButton.textContent = `Toggle Graticule${isShown ? " ✓" : ""}`;
      }
    });
    menuContent.appendChild(graticuleButton);

    el.appendChild(menuContent);

    menuButton.addEventListener("click", () => {
      menuContent.style.display =
        menuContent.style.display === "none" ? "block" : "none";
    });
  }

  const countries = await fetch(
    "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector/geojson/ne_110m_admin_0_countries.geojson",
  ).then((res) => res.json());

  const projection = d3[model.get("projection")]();
  projection.rotate(model.get("projection_rotate"));
  const center = model.get("projection_center");
  if (center) projection.center(center);
  const precision = model.get("projection_precision");
  if (precision != null) projection.precision(precision);
  const parallels = model.get("projection_parallels");
  if (parallels) projection.parallels(parallels);
  const a = model.get("projection_a");
  if (a != null) projection.a(a);
  const alpha = model.get("projection_alpha");
  if (alpha != null) projection.alpha(alpha);
  const b = model.get("projection_b");
  if (b != null) projection.b(b);
  const coefficient = model.get("projection_coefficient");
  if (coefficient != null) projection.coefficient(coefficient);
  const cutoffLatitude = model.get("projection_cutoff_latitude");
  if (cutoffLatitude != null) projection.cutoffLatitude(cutoffLatitude);
  const distance = model.get("projection_distance");
  if (distance != null) projection.distance(distance);
  const fraction = model.get("projection_fraction");
  if (fraction != null) projection.fraction(fraction);
  const gamma = model.get("projection_gamma");
  if (gamma != null) projection.gamma(gamma);
  const inflation = model.get("projection_inflation");
  if (inflation != null) projection.inflation(inflation);
  const k = model.get("projection_k");
  if (k != null) projection.k(k);
  const lobes = model.get("projection_lobes");
  if (lobes != null) projection.lobes(lobes);
  const parallel = model.get("projection_parallel");
  if (parallel != null) projection.parallel(parallel);
  const poleline = model.get("projection_poleline");
  if (poleline != null) projection.poleline(poleline);
  const psiMax = model.get("projection_psi_max");
  if (psiMax != null) projection.psiMax(psiMax);
  const radius = model.get("projection_radius");
  if (radius != null) projection.radius(radius);
  const ratio = model.get("projection_ratio");
  if (ratio != null) projection.ratio(ratio);
  const shift = model.get("projection_shift");
  if (shift != null) projection.shift(shift);
  const spacing = model.get("projection_spacing");
  if (spacing != null) projection.spacing(spacing);
  const tilt = model.get("projection_tilt");
  if (tilt != null) projection.tilt(tilt);
  const path = d3.geoPath(projection);
  const baseScale = projection.scale();
  const baseTranslate = projection.translate();
  const basemap = model.get("basemap");
  const border = model.get("border");

  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 960 500");
  svg.setAttribute("width", "960");
  svg.setAttribute("height", "500");
  const sphere = document.createElementNS("http://www.w3.org/2000/svg", "path");
  sphere.setAttribute("fill", "none");
  sphere.setAttribute("stroke", border ? "black" : "none");
  svg.appendChild(sphere);

  let naturalEarth = null;
  if (basemap === "naturalearth") {
    naturalEarth = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "path",
    );
    naturalEarth.setAttribute("fill", "none");
    naturalEarth.setAttribute("stroke", "black");
    svg.appendChild(naturalEarth);
  }

  const layerGroup = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "g",
  );
  svg.appendChild(layerGroup);
  function drawLayers() {
    layerGroup.replaceChildren();
    for (const layerData of model.get("layers")) {
      for (const feature of layerData.features) {
        const style = feature.properties.__ipyd3geo_style__ || {};
        const layer = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "path",
        );
        if (style.radius != null) {
          path.pointRadius(style.radius);
        } else {
          path.pointRadius(4.5);
        }
        layer.setAttribute("d", path(feature));
        layer.setAttribute("fill", style.fill_color || "none");
        layer.setAttribute("stroke", style.stroke_color || "#000000");
        layer.setAttribute("stroke-width", style.weight || 3);
        layer.setAttribute("stroke-opacity", style.stroke_opacity || 1.0);
        layer.setAttribute("fill-opacity", style.fill_opacity || 0.2);
        layerGroup.appendChild(layer);
      }
    }
  }
  model.on("change:layers", drawLayers);

  let graticule = null;
  if (model.get("graticule")) {
    graticule = document.createElementNS("http://www.w3.org/2000/svg", "path");
    graticule.setAttribute("fill", "none");
    graticule.setAttribute("stroke", "lightgray");
    graticule.setAttribute("opacity", "0.5");
    svg.appendChild(graticule);
  }

  svg.style.border = "2px solid black";

  function redraw() {
    sphere.setAttribute("d", path({ type: "Sphere" }));
    if (naturalEarth) naturalEarth.setAttribute("d", path(countries));
    if (graticule) graticule.setAttribute("d", path(d3.geoGraticule()()));
    drawLayers();
  }
  redraw();

  const dynamic = model.get("dynamic");
  if (dynamic !== "none") {
    let prev = { x: 0, y: 0 };
    const zoomBehavior = zoom().on("zoom", (event) => {
      const t = event.transform;
      projection.scale(baseScale * t.k);
      const isDrag = /^(mouse|touch)move$/.test(event.sourceEvent?.type);
      if (dynamic === "rotate") {
        if (isDrag) {
          const [lambda, phi, gamma] = projection.rotate();
          const degPerPixel = 180 / (Math.PI * projection.scale());
          projection.rotate([
            lambda + (t.x - prev.x) * degPerPixel,
            phi - (t.y - prev.y) * degPerPixel,
            gamma,
          ]);
        }
      } else {
        projection.translate([
          t.x + baseTranslate[0] * t.k,
          t.y + baseTranslate[1] * t.k,
        ]);
      }
      prev = { x: t.x, y: t.y };
      redraw();
    });
    select(svg).call(zoomBehavior);
  }

  el.appendChild(svg);
}

export default { render };
