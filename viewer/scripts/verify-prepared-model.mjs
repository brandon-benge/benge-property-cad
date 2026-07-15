#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { NullEngine } from "@babylonjs/core/Engines/nullEngine.js";
import { SceneLoader } from "@babylonjs/core/Loading/sceneLoader.js";
import { Scene } from "@babylonjs/core/scene.js";
import "@babylonjs/loaders/glTF/index.js";

const viewerRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modelRoot = path.join(viewerRoot, "public", "model");
const downloads = JSON.parse(await readFile(path.join(modelRoot, "download-manifest.json"), "utf8"));
const design = JSON.parse(await readFile(path.join(modelRoot, downloads.designElements), "utf8"));
const bytes = await readFile(path.join(modelRoot, downloads.model));
const dataUrl = `data:model/gltf-binary;base64,${bytes.toString("base64")}`;
const engine = new NullEngine({ renderWidth: 64, renderHeight: 64 });
const scene = new Scene(engine);

try {
  const result = await SceneLoader.ImportMeshAsync(null, "", dataUrl, scene, undefined, ".glb");
  const stableIds = new Set(
    result.meshes.map((mesh) => mesh.metadata?.gltf?.extras?.stable_id).filter((value) => typeof value === "string"),
  );
  const expected = design.elements
    .filter((element) => element.physical !== false && element.export_formats?.includes("glb"))
    .map((element) => element.id);
  const missing = expected.filter((id) => !stableIds.has(id));
  if (missing.length) throw new Error(`Babylon GLB load is missing semantic nodes: ${missing.join(", ")}`);
  if (stableIds.size === 0) throw new Error("Babylon GLB load found no stable IDs in glTF extras");
  console.log(`Babylon loaded ${result.meshes.length} meshes with ${stableIds.size} selectable stable IDs.`);
} finally {
  scene.dispose();
  engine.dispose();
}
