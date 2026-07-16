import { ArcRotateCamera } from "@babylonjs/core/Cameras/arcRotateCamera";
import "@babylonjs/core/Culling/ray";
import { AxesViewer } from "@babylonjs/core/Debug/axesViewer";
import { Engine } from "@babylonjs/core/Engines/engine";
import { PointerEventTypes } from "@babylonjs/core/Events/pointerEvents";
import { HighlightLayer } from "@babylonjs/core/Layers/highlightLayer";
import { DirectionalLight } from "@babylonjs/core/Lights/directionalLight";
import { HemisphericLight } from "@babylonjs/core/Lights/hemisphericLight";
import { SceneLoader } from "@babylonjs/core/Loading/sceneLoader";
import type { ISceneLoaderProgressEvent } from "@babylonjs/core/Loading/sceneLoader";
import { Color3, Color4 } from "@babylonjs/core/Maths/math.color";
import { Vector3 } from "@babylonjs/core/Maths/math.vector";
import type { AbstractMesh } from "@babylonjs/core/Meshes/abstractMesh";
import { Mesh } from "@babylonjs/core/Meshes/mesh";
import { Scene } from "@babylonjs/core/scene";
import "@babylonjs/core/Shaders/default.fragment";
import "@babylonjs/core/Shaders/default.vertex";
import "@babylonjs/core/Shaders/glowBlurPostProcess.fragment";
import "@babylonjs/core/Shaders/glowMapGeneration.fragment";
import "@babylonjs/core/Shaders/glowMapGeneration.vertex";
import "@babylonjs/core/Shaders/glowMapMerge.fragment";
import "@babylonjs/core/Shaders/glowMapMerge.vertex";
import "@babylonjs/core/Shaders/pass.fragment";
import "@babylonjs/core/Shaders/pbr.fragment";
import "@babylonjs/core/Shaders/pbr.vertex";
import "@babylonjs/core/Shaders/postprocess.vertex";
import "@babylonjs/core/Shaders/rgbdDecode.fragment";
import "@babylonjs/loaders/glTF";
import type { ElementMetadata } from "../types/artifacts";
import { MetadataIndex } from "./metadata";

type ViewName = "isometric" | "front" | "top" | "right";

export interface LoadProgress {
  loaded: number;
  total: number | null;
  percent: number | null;
}

export class DesignViewer {
  readonly engine: Engine;
  readonly scene: Scene;
  readonly camera: ArcRotateCamera;
  readonly metadata: MetadataIndex;
  onSelectionChanged: (metadata: ElementMetadata | null) => void = () => undefined;

  private readonly highlight: HighlightLayer;
  private readonly axesViewer: AxesViewer;
  private readonly resizeObserver: ResizeObserver;
  private readonly meshesById = new Map<string, Mesh[]>();
  private selectedId: string | null = null;
  private modelBounds: { minimum: Vector3; maximum: Vector3 } | null = null;

  constructor(canvas: HTMLCanvasElement, metadata: MetadataIndex) {
    this.metadata = metadata;
    this.engine = new Engine(canvas, true, { preserveDrawingBuffer: false, stencil: true, antialias: true });
    this.scene = new Scene(this.engine);
    this.scene.clearColor = new Color4(0.93, 0.95, 0.96, 1);
    this.camera = new ArcRotateCamera("review-camera", -Math.PI / 4, Math.PI / 3, 10, Vector3.Zero(), this.scene);
    this.camera.attachControl(canvas, true);
    this.camera.wheelPrecision = 25;
    this.camera.pinchPrecision = 70;
    this.camera.panningSensibility = 120;
    this.camera.lowerBetaLimit = 0.01;
    this.camera.upperBetaLimit = Math.PI - 0.01;
    this.camera.useNaturalPinchZoom = true;
    const hemisphere = new HemisphericLight("environment-light", new Vector3(0, 1, 0), this.scene);
    hemisphere.intensity = 0.8;
    hemisphere.groundColor = new Color3(0.42, 0.46, 0.5);
    const directional = new DirectionalLight("directional-light", new Vector3(-0.6, -1, -0.45), this.scene);
    directional.position = new Vector3(20, 30, 20);
    directional.intensity = 1.15;
    this.highlight = new HighlightLayer("selection-highlight", this.scene);
    this.highlight.innerGlow = false;
    this.highlight.outerGlow = true;
    this.axesViewer = new AxesViewer(this.scene, 1, 2, undefined, undefined, undefined, 1.5);
    const axes = cadAxisDirections();
    this.axesViewer.update(Vector3.Zero(), axes.x, axes.y, axes.z);

    this.scene.onPointerObservable.add((pointer) => {
      if (pointer.type !== PointerEventTypes.POINTERTAP) return;
      const picked = pointer.pickInfo?.hit ? pointer.pickInfo.pickedMesh : null;
      const element = this.metadata.resolve(picked);
      if (element) this.selectById(element.id);
      else this.clearSelection();
    });
    this.engine.runRenderLoop(() => this.scene.render());
    this.resizeObserver = new ResizeObserver(() => this.engine.resize());
    this.resizeObserver.observe(canvas);
    window.addEventListener("resize", this.resize);
    window.addEventListener("orientationchange", this.resize);
  }

  async load(url: string, onProgress: (progress: LoadProgress) => void): Promise<void> {
    const separator = url.lastIndexOf("/") + 1;
    const rootUrl = url.slice(0, separator);
    const fileName = url.slice(separator);
    const result = await SceneLoader.ImportMeshAsync(
      null,
      rootUrl,
      fileName,
      this.scene,
      (event: ISceneLoaderProgressEvent) => onProgress(progressValue(event)),
    );
    for (const abstractMesh of result.meshes) {
      if (!(abstractMesh instanceof Mesh) || abstractMesh.getTotalVertices() === 0) continue;
      const element = this.metadata.resolve(abstractMesh);
      if (!element) {
        abstractMesh.isPickable = false;
        continue;
      }
      const meshes = this.meshesById.get(element.id) ?? [];
      meshes.push(abstractMesh);
      this.meshesById.set(element.id, meshes);
      abstractMesh.isPickable = true;
    }
    this.modelBounds = boundsFor([...this.meshesById.values()].flat());
    if (!this.modelBounds) throw new Error("The GLB loaded, but it contains no selectable model geometry");
    this.axesViewer.scaleLines = axisScaleForBounds(Vector3.Distance(this.modelBounds.minimum, this.modelBounds.maximum));
    this.engine.resize(true);
    this.fitModel();
    this.scene.render();
    requestAnimationFrame(() => {
      this.engine.resize(true);
      this.fitModel();
    });
    onProgress({ loaded: 1, total: 1, percent: 100 });
  }

  selectById(id: string): void {
    const meshes = this.meshesById.get(id);
    const element = this.metadata.elements.get(id);
    if (!meshes || !element) return;
    this.highlight.removeAllMeshes();
    for (const mesh of meshes) this.highlight.addMesh(mesh, new Color3(0.04, 0.55, 0.9));
    this.selectedId = id;
    this.onSelectionChanged(element);
  }

  clearSelection(): void {
    this.highlight.removeAllMeshes();
    this.selectedId = null;
    this.onSelectionChanged(null);
  }

  fitModel(): void {
    if (this.modelBounds) this.frameBounds(this.modelBounds);
  }

  frameSelected(): void {
    if (!this.selectedId) return;
    const bounds = boundsFor(this.meshesById.get(this.selectedId) ?? []);
    if (bounds) this.frameBounds(bounds);
  }

  isolateSelection(): void {
    if (!this.selectedId) return;
    for (const [id, meshes] of this.meshesById) {
      for (const mesh of meshes) mesh.setEnabled(id === this.selectedId);
    }
  }

  showAll(): void {
    for (const meshes of this.meshesById.values()) for (const mesh of meshes) mesh.setEnabled(true);
  }

  setCategoryVisible(category: string, visible: boolean): void {
    for (const [id, meshes] of this.meshesById) {
      if (this.metadata.elements.get(id)?.category !== category) continue;
      for (const mesh of meshes) mesh.setEnabled(visible);
    }
    if (!visible && this.selectedId && this.metadata.elements.get(this.selectedId)?.category === category) this.clearSelection();
  }

  setAxesVisible(visible: boolean): void {
    this.axesViewer.xAxis.setEnabled(visible);
    this.axesViewer.yAxis.setEnabled(visible);
    this.axesViewer.zAxis.setEnabled(visible);
  }

  setView(view: ViewName): void {
    const positions: Record<ViewName, [number, number]> = {
      isometric: [-Math.PI / 4, Math.PI / 3],
      front: [-Math.PI / 2, Math.PI / 2],
      top: [-Math.PI / 2, 0.01],
      right: [0, Math.PI / 2],
    };
    [this.camera.alpha, this.camera.beta] = positions[view];
    this.fitModel();
  }

  resetView(): void {
    this.showAll();
    this.clearSelection();
    this.setView("isometric");
  }

  dispose(): void {
    this.resizeObserver.disconnect();
    window.removeEventListener("resize", this.resize);
    window.removeEventListener("orientationchange", this.resize);
    this.axesViewer.dispose();
    this.scene.dispose();
    this.engine.dispose();
  }

  private readonly resize = (): void => {
    this.engine.resize();
  };

  private frameBounds(bounds: { minimum: Vector3; maximum: Vector3 }): void {
    const center = bounds.minimum.add(bounds.maximum).scale(0.5);
    const diagonal = Vector3.Distance(bounds.minimum, bounds.maximum);
    const clipping = clippingRange(diagonal);
    this.camera.setTarget(center);
    this.camera.radius = Math.max(diagonal * 1.1, 1);
    this.camera.lowerRadiusLimit = Math.max(diagonal * 0.005, 0.01);
    this.camera.upperRadiusLimit = Math.max(diagonal * 20, 100);
    this.camera.minZ = clipping.minimum;
    this.camera.maxZ = clipping.maximum;
  }
}

export function progressValue(event: ISceneLoaderProgressEvent): LoadProgress {
  const total = event.lengthComputable && event.total > 0 ? event.total : null;
  return {
    loaded: event.loaded,
    total,
    percent: total ? Math.min(100, Math.round((event.loaded / total) * 100)) : null,
  };
}

export function clippingRange(modelDiagonal: number): { minimum: number; maximum: number } {
  return {
    minimum: Math.max(modelDiagonal * 0.0001, 0.1),
    maximum: Math.max(modelDiagonal * 25, 10_000),
  };
}

export function cadAxisDirections(): { x: Vector3; y: Vector3; z: Vector3 } {
  // The exporter maps CAD (x, y, z) to glTF (x, z, -y). Babylon's default
  // left-handed loader conversion then maps positive CAD X/Y/Z to -X/-Z/+Y.
  return { x: Vector3.Left(), y: Vector3.Backward(), z: Vector3.Up() };
}

export function axisScaleForBounds(modelDiagonal: number): number {
  // AxesViewer's arrow geometry is four times scaleLines.
  return Math.max(modelDiagonal * 0.035, 1);
}

function boundsFor(meshes: AbstractMesh[]): { minimum: Vector3; maximum: Vector3 } | null {
  let minimum: Vector3 | null = null;
  let maximum: Vector3 | null = null;
  for (const mesh of meshes) {
    mesh.computeWorldMatrix(true);
    const box = mesh.getBoundingInfo().boundingBox;
    minimum = minimum ? Vector3.Minimize(minimum, box.minimumWorld) : box.minimumWorld.clone();
    maximum = maximum ? Vector3.Maximize(maximum, box.maximumWorld) : box.maximumWorld.clone();
  }
  return minimum && maximum ? { minimum, maximum } : null;
}
