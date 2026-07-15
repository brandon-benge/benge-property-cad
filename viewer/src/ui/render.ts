import type { ArtifactBundle, ArtifactFile, ElementMetadata } from "../types/artifacts";
import { modelUrl } from "../viewer/artifacts";
import type { MetadataIndex } from "../viewer/metadata";
import {
  formatArea,
  formatLength,
  formatMass,
  formatMeasurementValue,
  formatRange,
  formatVolume,
  measurementLabel,
  type MeasurementSystem,
} from "./measurements";

export function createAppShell(root: HTMLElement): void {
  root.innerHTML = `
    <div class="app-shell">
      <header class="app-header">
        <div class="brand-block">
          <span class="brand-mark" aria-hidden="true">B</span>
          <div><p class="eyebrow">Generated design</p><h1 id="model-title">Design Viewer</h1></div>
        </div>
        <div class="header-tools">
          <label class="unit-control" for="measurement-system"><span>Units</span><select id="measurement-system" aria-label="Measurement units"><option value="metric">Metric</option><option value="us">US customary</option></select></label>
          <div class="header-status"><span id="build-status" class="status-pill">Preparing</span><span id="offline-status" class="offline-status" aria-live="polite"></span></div>
        </div>
      </header>
      <div class="workspace">
        <nav class="section-nav" aria-label="Viewer sections">
          <button type="button" class="nav-button is-active" data-panel="model" aria-pressed="true"><span aria-hidden="true">◇</span><span>Model</span></button>
          <button type="button" class="nav-button" data-panel="drawings" aria-pressed="false"><span aria-hidden="true">▤</span><span>Drawings</span></button>
          <button type="button" class="nav-button" data-panel="downloads" aria-pressed="false"><span aria-hidden="true">⇩</span><span>Files</span></button>
          <button type="button" class="nav-button" data-panel="build" aria-pressed="false"><span aria-hidden="true">ⓘ</span><span>Build</span></button>
        </nav>
        <aside class="aux-panel is-open" aria-label="Model tools">
          <div class="panel-heading"><div><p class="eyebrow">Browse</p><h2 id="aux-title">Model tree</h2></div><button class="icon-button close-aux" type="button" aria-label="Close panel">×</button></div>
          <div id="aux-content" class="panel-scroll"></div>
        </aside>
        <main class="viewport" aria-label="Interactive 3D design viewer">
          <canvas id="viewer-canvas" tabindex="0" aria-label="3D model. Drag to orbit, pinch or scroll to zoom, and use two fingers or the secondary mouse button to pan."></canvas>
          <div id="loading-overlay" class="loading-overlay" role="status" aria-live="polite">
            <div class="loader-ring" aria-hidden="true"></div><strong id="loading-title">Loading generated model</strong>
            <span id="loading-detail">Reading artifact manifest…</span>
            <div class="progress-track"><span id="progress-bar"></span></div>
          </div>
          <div class="view-toolbar" role="toolbar" aria-label="Camera views">
            <button type="button" data-view="reset">Reset</button><button type="button" data-view="fit">Fit</button>
            <button type="button" data-view="axes" aria-pressed="true">Axes</button>
            <span class="toolbar-divider" aria-hidden="true"></span>
            <button type="button" data-view="isometric">Iso</button><button type="button" data-view="front">Front</button>
            <button type="button" data-view="top">Top</button><button type="button" data-view="right">Right</button>
          </div>
          <div id="axis-legend" class="axis-legend" aria-label="CAD coordinate axes"><span class="axis-x">X</span><span class="axis-y">Y</span><span class="axis-z">Z</span></div>
          <p class="navigation-hint">Drag to orbit · Scroll or pinch to zoom · Two fingers to pan</p>
        </main>
        <aside id="property-panel" class="property-panel" aria-labelledby="property-title">
          <div class="sheet-handle" aria-hidden="true"></div>
          <div class="panel-heading"><div><p class="eyebrow">Selection</p><h2 id="property-title">Properties</h2></div><button class="icon-button close-properties" type="button" aria-label="Close properties">×</button></div>
          <div id="property-content" class="panel-scroll"><div class="empty-state"><span aria-hidden="true">◇</span><p>Select an element in the model or tree to inspect its semantic metadata.</p></div></div>
          <div class="property-actions"><button id="isolate-selection" type="button" disabled>Isolate</button><button id="frame-selection" type="button" disabled>Frame selected</button></div>
        </aside>
      </div>
    </div>`;
}

export function renderModelTree(container: HTMLElement, metadata: MetadataIndex): void {
  container.replaceChildren();
  const actions = element("div", "tree-actions");
  actions.append(button("Show all", "show-all"), button("Collapse all", "collapse-all"));
  container.append(actions);
  const tree = element("div", "model-tree");
  tree.setAttribute("role", "tree");
  for (const [category, elements] of metadata.categories()) {
    const details = document.createElement("details");
    details.open = true;
    details.dataset.category = category;
    const summary = document.createElement("summary");
    summary.innerHTML = `<span class="category-name"></span><span class="category-count"></span>`;
    setText(summary.querySelector(".category-name"), category);
    setText(summary.querySelector(".category-count"), String(elements.length));
    const visibility = document.createElement("input");
    visibility.type = "checkbox";
    visibility.checked = true;
    visibility.className = "category-visibility";
    visibility.dataset.category = category;
    visibility.setAttribute("aria-label", `Show ${category}`);
    visibility.addEventListener("click", (event) => event.stopPropagation());
    summary.prepend(visibility);
    details.append(summary);
    const list = element("div", "element-list");
    list.setAttribute("role", "group");
    for (const item of elements) {
      const itemButton = button(item.name, "tree-element");
      itemButton.dataset.elementId = item.id;
      itemButton.setAttribute("role", "treeitem");
      itemButton.title = item.id;
      list.append(itemButton);
    }
    details.append(list);
    tree.append(details);
  }
  container.append(tree);
}

export function renderDrawings(container: HTMLElement, bundle: ArtifactBundle): void {
  container.replaceChildren();
  const svgFiles = bundle.downloads.files.filter((file) => file.kind === "drawing-svg");
  const pdfFiles = bundle.downloads.files.filter((file) => file.kind === "drawing-pdf");
  if (!svgFiles.length && !pdfFiles.length) return container.append(empty("No generated drawings are available in this build."));
  for (const file of svgFiles) {
    const card = element("article", "drawing-card");
    const image = document.createElement("img");
    image.src = modelUrl(file.path);
    image.alt = `${file.name} generated drawing`;
    image.loading = "lazy";
    card.append(image, downloadLink(file, "Open SVG", true));
    container.append(card);
  }
  for (const file of pdfFiles) container.append(downloadLink(file, "Open drawing package", true));
}

export function renderDownloads(container: HTMLElement, bundle: ArtifactBundle): void {
  container.replaceChildren();
  const groups = new Map<string, ArtifactFile[]>();
  for (const file of bundle.downloads.files) {
    const group = downloadGroup(file);
    const values = groups.get(group) ?? [];
    values.push(file);
    groups.set(group, values);
  }
  for (const [name, files] of groups) {
    const section = element("section", "download-group");
    const heading = document.createElement("h3");
    heading.textContent = name;
    section.append(heading);
    for (const file of files) {
      const opensInBrowser = file.kind === "drawing-svg" || file.kind === "drawing-pdf";
      section.append(downloadLink(file, `${file.extension} · ${formatBytes(file.size)}`, opensInBrowser));
    }
    container.append(section);
  }
}

export function renderBuildInfo(container: HTMLElement, bundle: ArtifactBundle): void {
  container.replaceChildren();
  const repository = bundle.downloads.repository;
  const fields: Array<[string, string]> = [
    ["Repository", repository || "Not recorded"],
    ["Commit", shortSha(bundle.build.git_sha)],
    ["Build version", bundle.build.tool_version || "Not recorded"],
    ["Build timestamp", formatDate(bundle.build.build_timestamp_utc || bundle.downloads.buildTimestamp)],
    ["Exporters", bundle.build.selected_exporters?.join(", ") || "Not recorded"],
    ["Validation", bundle.build.validation_status || "Not recorded"],
    ["Element count", bundle.build.model_element_count?.toLocaleString() || String(bundle.design.elements.length)],
    ["Build hash", bundle.build.semantic_hash || "Not recorded"],
  ];
  const list = element("dl", "build-info");
  for (const [term, value] of fields) {
    const dt = document.createElement("dt");
    dt.textContent = term;
    const dd = document.createElement("dd");
    dd.textContent = value;
    dd.title = value;
    list.append(dt, dd);
  }
  container.append(list);
}

export function renderProperties(container: HTMLElement, item: ElementMetadata | null, system: MeasurementSystem = "metric"): void {
  container.replaceChildren();
  if (!item) return container.append(empty("Select an element in the model or tree to inspect its semantic metadata."));
  const identity = propertySection("Identity", [
    ["Name", item.name], ["Stable ID", item.id], ["Category", item.category], ["IFC class", text(item.ifc_class)],
    ["Material", text(item.material_id)], ["Storey", text(item.storey)], ["Source component", text(item.source_module)],
  ]);
  container.append(identity);
  const translation = coordinateTuple(item.placement?.translation_mm, 3);
  if (translation) {
    container.append(propertySection("Position", [
      ["X origin", formatLength(translation[0], system)],
      ["Y origin", formatLength(translation[1], system)],
      ["Z origin", formatLength(translation[2], system)],
    ]));
  }
  const bounds = coordinateTuple(item.bounds_mm, 6);
  if (bounds) {
    container.append(propertySection("Extents", [
      ["X range", formatRange(bounds[0], bounds[3], system)],
      ["Y range", formatRange(bounds[1], bounds[4], system)],
      ["Z range", formatRange(bounds[2], bounds[5], system)],
    ]));
  }
  if (item.dimensions) {
    const dimensions = Object.entries(item.dimensions)
      .filter(([key, value]) => key !== "extras" && value != null)
      .map(([key, value]) => [measurementLabel(key), typeof value === "number" ? formatLength(value, system) : text(value)] as [string, string]);
    if (dimensions.length) container.append(propertySection("Dimensions", dimensions));
  }
  const properties: Array<[string, string]> = [];
  if (item.geometry_kind) properties.push(["Geometry", item.geometry_kind]);
  if (item.tags?.length) properties.push(["Tags", item.tags.join(", ")]);
  const custom = { ...(item.properties || {}), ...(item.dimensions?.extras || {}) };
  for (const [key, value] of Object.entries(custom)) properties.push([measurementLabel(key), formatMeasurementValue(key, value, system)]);
  if (properties.length) container.append(propertySection("Properties", properties));
  if (item.quantities) {
    container.append(propertySection("Quantities", [
      ["Count", text(item.quantities.count)],
      ["Area", formatArea(item.quantities.area_mm2, system)],
      ["Volume", formatVolume(item.quantities.volume_mm3, system)],
      ["Mass", formatMass(item.quantities.mass_kg, system)],
      ["Provenance", text(item.quantities.provenance)],
    ]));
  }
}

function propertySection(title: string, values: Array<[string, string]>): HTMLElement {
  const section = element("section", "property-section");
  const heading = document.createElement("h3");
  heading.textContent = title;
  const list = document.createElement("dl");
  for (const [name, value] of values) {
    const dt = document.createElement("dt"); dt.textContent = name;
    const dd = document.createElement("dd"); dd.textContent = value;
    list.append(dt, dd);
  }
  section.append(heading, list);
  return section;
}

function downloadLink(file: ArtifactFile, detail: string, openInBrowser: boolean): HTMLAnchorElement {
  const link = document.createElement("a");
  link.className = "file-link";
  link.href = modelUrl(file.path);
  if (openInBrowser) {
    link.target = "_blank";
    link.rel = "noopener";
  } else link.download = pathName(file.path);
  const label = document.createElement("span"); label.textContent = file.name;
  const meta = document.createElement("small"); meta.textContent = detail;
  link.append(label, meta);
  return link;
}

function element<K extends keyof HTMLElementTagNameMap>(tag: K, className: string): HTMLElementTagNameMap[K] {
  const value = document.createElement(tag); value.className = className; return value;
}

function button(label: string, className: string): HTMLButtonElement {
  const value = document.createElement("button"); value.type = "button"; value.className = className; value.textContent = label; return value;
}

function empty(message: string): HTMLElement {
  const value = element("div", "empty-state");
  const icon = document.createElement("span"); icon.setAttribute("aria-hidden", "true"); icon.textContent = "◇";
  const copy = document.createElement("p"); copy.textContent = message;
  value.append(icon, copy); return value;
}

function setText(target: Element | null, value: string): void { if (target) target.textContent = value; }
function text(value: unknown): string { return value == null || value === "" ? "—" : String(value); }
function shortSha(value?: string | null): string { return value ? value.slice(0, 12) : "Not recorded"; }
function formatDate(value?: string | null): string { return value ? new Date(value).toLocaleString() : "Not recorded"; }
function pathName(value: string): string { return value.split("/").at(-1) || value; }
function formatBytes(bytes: number): string { if (bytes < 1024) return `${bytes} B`; if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`; return `${(bytes / 1024 ** 2).toFixed(1)} MB`; }
function downloadGroup(file: ArtifactFile): string {
  if (file.kind === "model" || file.kind === "step" || file.kind === "ifc") return "Models";
  if (file.kind.startsWith("drawing-")) return "Drawings";
  if (file.kind === "quantities-json" || file.kind === "csv") return "Quantities";
  return "Metadata";
}

function coordinateTuple(value: number[] | undefined, length: 3): [number, number, number] | null;
function coordinateTuple(value: number[] | undefined, length: 6): [number, number, number, number, number, number] | null;
function coordinateTuple(value: number[] | undefined, length: 3 | 6): number[] | null {
  return value?.length === length && value.every(Number.isFinite) ? value : null;
}
