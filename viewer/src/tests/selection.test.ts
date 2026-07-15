import type { Node } from "@babylonjs/core/node";
import { describe, expect, it } from "vitest";
import { MetadataIndex } from "../viewer/metadata";

describe("semantic selection", () => {
  it("resolves a stable ID from glTF extras on a mesh or parent", () => {
    const index = new MetadataIndex(
      { model_id: "m", model_name: "Model", elements: [{ id: "deck.post.1", name: "Post", category: "Structure" }] },
      [],
    );
    const parent = { metadata: { gltf: { extras: { stable_id: "deck.post.1", category: "Structure" } } }, parent: null } as unknown as Node;
    const child = { metadata: null, parent } as unknown as Node;
    expect(index.resolve(child)?.name).toBe("Post");
  });

  it("ignores helper meshes that have no semantic stable ID", () => {
    const index = new MetadataIndex({ model_id: "m", model_name: "Model", elements: [] }, []);
    const helper = { metadata: null, parent: null } as unknown as Node;
    expect(index.resolve(helper)).toBeNull();
  });
});
