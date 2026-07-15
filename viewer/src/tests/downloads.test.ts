import { describe, expect, it } from "vitest";
import { renderDownloads } from "../ui/render";
import type { ArtifactBundle } from "../types/artifacts";

describe("downloads", () => {
  it("renders links only for artifacts in the generated manifest", () => {
    const bundle = {
      downloads: {
        schemaVersion: 1,
        generatedAt: "2026-01-01T00:00:00Z",
        repository: null,
        model: "glb/model.glb",
        designElements: "manifests/design-elements.json",
        buildManifest: "manifests/build-manifest.json",
        runMetadata: null,
        buildTimestamp: null,
        files: [
          { path: "glb/model.glb", name: "model", extension: "GLB", kind: "model", size: 100 },
          { path: "drawings/plan.svg", name: "plan", extension: "SVG", kind: "drawing-svg", size: 50 },
        ],
      },
      design: { model_id: "m", model_name: "Model", elements: [] },
      build: {},
      quantities: [],
    } satisfies ArtifactBundle;
    const container = document.createElement("div");
    renderDownloads(container, bundle);
    expect(container.querySelectorAll("a")).toHaveLength(2);
    expect(container.textContent).toContain("GLB");
    expect(container.textContent).not.toContain("STEP");
  });
});
