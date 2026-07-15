import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { tmpdir } from "node:os";
import { mkdtemp } from "node:fs/promises";
import { describe, expect, it } from "vitest";
import { prepareModel } from "../../scripts/prepare-model.mjs";

async function fixture(): Promise<{ source: string; destination: string }> {
  const root = await mkdtemp(path.join(tmpdir(), "cad-viewer-"));
  const source = path.join(root, "generated");
  const destination = path.join(root, "model");
  await mkdir(path.join(source, "manifests"), { recursive: true });
  await mkdir(path.join(source, "glb"), { recursive: true });
  await writeFile(path.join(source, "glb", "house.glb"), "glTF");
  await writeFile(path.join(source, "manifests", "design-elements.json"), JSON.stringify({ model_id: "m", model_name: "Model", elements: [] }));
  await writeFile(path.join(source, "manifests", "build-manifest.json"), JSON.stringify({ artifacts: [{ path: "glb/house.glb" }] }));
  return { source, destination };
}

describe("prepare-model", () => {
  it("copies discovered artifacts and generates the viewer download manifest", async () => {
    const paths = await fixture();
    const manifest = await prepareModel(paths);
    expect(manifest.model).toBe("glb/house.glb");
    const stored = JSON.parse(await readFile(path.join(paths.destination, "download-manifest.json"), "utf8")) as { files: unknown[] };
    expect(stored.files).toHaveLength(3);
  });

  it("fails clearly when the required GLB is missing", async () => {
    const paths = await fixture();
    await writeFile(path.join(paths.source, "manifests", "build-manifest.json"), JSON.stringify({ artifacts: [] }));
    await import("node:fs/promises").then(({ rm }) => rm(path.join(paths.source, "glb", "house.glb")));
    await expect(prepareModel(paths)).rejects.toThrow(/\.glb model/);
  });

  it("fails when the build manifest references a missing artifact", async () => {
    const paths = await fixture();
    await writeFile(path.join(paths.source, "manifests", "build-manifest.json"), JSON.stringify({ artifacts: [{ path: "step/missing.step" }] }));
    await expect(prepareModel(paths)).rejects.toThrow(/references a missing artifact/);
  });
});
