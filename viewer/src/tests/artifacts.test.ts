import { afterEach, describe, expect, it, vi } from "vitest";
import { loadArtifactBundle } from "../viewer/artifacts";

afterEach(() => vi.unstubAllGlobals());

describe("artifact loading", () => {
  it("discovers metadata and optional quantities through the download manifest", async () => {
    const values: Record<string, unknown> = {
      "download-manifest.json": {
        schemaVersion: 1,
        generatedAt: "2026-01-01T00:00:00Z",
        repository: "owner/repo",
        model: "glb/model.glb",
        designElements: "manifests/design-elements.json",
        buildManifest: "manifests/build-manifest.json",
        runMetadata: null,
        buildTimestamp: null,
        files: [{ path: "quantities/quantities.json", name: "quantities", extension: "JSON", kind: "quantities-json", size: 10 }],
      },
      "design-elements.json": { model_id: "m", model_name: "Model", elements: [] },
      "build-manifest.json": { artifacts: [], validation_status: "passed" },
      "quantities.json": [{ element_id: "wall.1", count: 1 }],
    };
    vi.stubGlobal("fetch", vi.fn(async (input: string | URL | Request) => {
      const name = new URL(String(input)).pathname.split("/").at(-1) || "";
      return new Response(JSON.stringify(values[name]), { status: 200 });
    }));
    const bundle = await loadArtifactBundle();
    expect(bundle.build.validation_status).toBe("passed");
    expect(bundle.quantities).toHaveLength(1);
  });

  it("reports a missing download manifest clearly", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("missing", { status: 404 })));
    await expect(loadArtifactBundle()).rejects.toThrow(/download manifest \(404\)/);
  });
});
