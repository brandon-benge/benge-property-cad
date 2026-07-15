import "./styles.css";
import { createAppShell, renderBuildInfo, renderDownloads, renderDrawings, renderModelTree, renderProperties } from "./ui/render";
import { loadArtifactBundle, modelUrl } from "./viewer/artifacts";
import { DesignViewer } from "./viewer/designViewer";
import { MetadataIndex } from "./viewer/metadata";

const root = document.querySelector<HTMLElement>("#app");
if (!root) throw new Error("App root is missing");
createAppShell(root);
if (window.matchMedia("(max-width: 760px)").matches) document.querySelector(".aux-panel")?.classList.remove("is-open");

const required = <T extends Element>(selector: string): T => {
  const value = document.querySelector<T>(selector);
  if (!value) throw new Error(`Viewer UI is missing ${selector}`);
  return value;
};

const loading = required<HTMLElement>("#loading-overlay");
const loadingTitle = required<HTMLElement>("#loading-title");
const loadingDetail = required<HTMLElement>("#loading-detail");
const progressBar = required<HTMLElement>("#progress-bar");
const propertyPanel = required<HTMLElement>("#property-panel");
const propertyContent = required<HTMLElement>("#property-content");
const isolateButton = required<HTMLButtonElement>("#isolate-selection");
const frameButton = required<HTMLButtonElement>("#frame-selection");
const auxPanel = required<HTMLElement>(".aux-panel");
const auxTitle = required<HTMLElement>("#aux-title");
const auxContent = required<HTMLElement>("#aux-content");
let viewer: DesignViewer | null = null;
let selectedPanel = "model";

async function start(): Promise<void> {
  try {
    const bundle = await loadArtifactBundle();
    const metadata = new MetadataIndex(bundle.design, bundle.quantities);
    required<HTMLElement>("#model-title").textContent = bundle.design.model_name;
    const buildStatus = required<HTMLElement>("#build-status");
    buildStatus.textContent = bundle.build.validation_status === "passed" ? "Validated build" : bundle.build.validation_status || "Build loaded";
    buildStatus.classList.toggle("is-warning", bundle.build.validation_status !== "passed");
    renderModelTree(auxContent, metadata);
    bindTree();
    viewer = new DesignViewer(required<HTMLCanvasElement>("#viewer-canvas"), metadata);
    viewer.onSelectionChanged = (item) => {
      renderProperties(propertyContent, item);
      propertyPanel.classList.toggle("has-selection", Boolean(item));
      isolateButton.disabled = !item;
      frameButton.disabled = !item;
      document.querySelectorAll(".tree-element.is-selected").forEach((node) => node.classList.remove("is-selected"));
      if (item) {
        const target = document.querySelector<HTMLElement>(`.tree-element[data-element-id="${CSS.escape(item.id)}"]`);
        target?.classList.add("is-selected");
        target?.closest("details")?.setAttribute("open", "");
      }
    };
    loadingTitle.textContent = "Loading 3D geometry";
    loadingDetail.textContent = "Starting Babylon.js loader…";
    await viewer.load(modelUrl(bundle.downloads.model), (progress) => {
      progressBar.style.width = `${progress.percent ?? 28}%`;
      loadingDetail.textContent = progress.percent == null ? `${formatBytes(progress.loaded)} received` : `${progress.percent}%`;
    });
    loading.classList.add("is-complete");
    setTimeout(() => loading.setAttribute("hidden", ""), 260);
    bindPanels(bundle, metadata);
    bindViewerControls();
    void enableOfflineCache().catch(() => {
      required<HTMLElement>("#offline-status").textContent = "Online mode";
    });
  } catch (error) {
    showError(error instanceof Error ? error.message : String(error));
  }
}

function bindTree(): void {
  if (auxContent.dataset.treeEventsBound === "true") return;
  auxContent.dataset.treeEventsBound = "true";
  auxContent.addEventListener("click", (event) => {
    const target = event.target as HTMLElement;
    const treeItem = target.closest<HTMLButtonElement>(".tree-element");
    if (treeItem?.dataset.elementId) viewer?.selectById(treeItem.dataset.elementId);
    if (target.closest(".show-all")) {
      viewer?.showAll();
      document.querySelectorAll<HTMLInputElement>(".category-visibility").forEach((checkbox) => (checkbox.checked = true));
    }
    if (target.closest(".collapse-all")) document.querySelectorAll<HTMLDetailsElement>(".model-tree details").forEach((item) => (item.open = false));
  });
  auxContent.addEventListener("change", (event) => {
    const checkbox = (event.target as HTMLElement).closest<HTMLInputElement>(".category-visibility");
    if (checkbox?.dataset.category) viewer?.setCategoryVisible(checkbox.dataset.category, checkbox.checked);
  });
}

function bindPanels(bundle: Awaited<ReturnType<typeof loadArtifactBundle>>, metadata: MetadataIndex): void {
  document.querySelectorAll<HTMLButtonElement>(".nav-button").forEach((button) => {
    button.addEventListener("click", () => {
      const name = button.dataset.panel || "model";
      const sameOpenPanel = selectedPanel === name && auxPanel.classList.contains("is-open");
      selectedPanel = name;
      document.querySelectorAll<HTMLButtonElement>(".nav-button").forEach((item) => {
        const active = item === button && !sameOpenPanel;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-pressed", String(active));
      });
      if (sameOpenPanel) return auxPanel.classList.remove("is-open");
      auxPanel.classList.add("is-open");
      if (name === "model") { auxTitle.textContent = "Model tree"; renderModelTree(auxContent, metadata); bindTree(); }
      if (name === "drawings") { auxTitle.textContent = "Drawings"; renderDrawings(auxContent, bundle); }
      if (name === "downloads") { auxTitle.textContent = "Downloads"; renderDownloads(auxContent, bundle); }
      if (name === "build") { auxTitle.textContent = "Build information"; renderBuildInfo(auxContent, bundle); }
    });
  });
  required<HTMLButtonElement>(".close-aux").addEventListener("click", () => auxPanel.classList.remove("is-open"));
  required<HTMLButtonElement>(".close-properties").addEventListener("click", () => viewer?.clearSelection());
}

function bindViewerControls(): void {
  document.querySelectorAll<HTMLButtonElement>("[data-view]").forEach((button) => button.addEventListener("click", () => {
    const view = button.dataset.view;
    if (view === "reset") {
      viewer?.resetView();
      document.querySelectorAll<HTMLInputElement>(".category-visibility").forEach((checkbox) => (checkbox.checked = true));
    }
    else if (view === "fit") viewer?.fitModel();
    else if (view === "isometric" || view === "front" || view === "top" || view === "right") viewer?.setView(view);
  }));
  isolateButton.addEventListener("click", () => viewer?.isolateSelection());
  frameButton.addEventListener("click", () => viewer?.frameSelected());
  window.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (propertyPanel.classList.contains("has-selection")) viewer?.clearSelection();
    else auxPanel.classList.remove("is-open");
  });
}

async function enableOfflineCache(): Promise<void> {
  if (!("serviceWorker" in navigator) || import.meta.env.DEV) return;
  await navigator.serviceWorker.register(new URL("sw.js", document.baseURI));
  const registration = await navigator.serviceWorker.ready;
  registration.active?.postMessage({ type: "CACHE_MODEL" });
  required<HTMLElement>("#offline-status").textContent = "Available offline after first load";
}

function showError(message: string): void {
  loading.classList.add("is-error");
  loadingTitle.textContent = "Viewer could not start";
  loadingDetail.textContent = `${message} Prepare artifacts with: npm run prepare-model`;
  progressBar.style.width = "100%";
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
}

void start();
