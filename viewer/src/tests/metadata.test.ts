import { describe, expect, it } from "vitest";
import { MetadataIndex, validateBuildManifest, validateDesignManifest } from "../viewer/metadata";
import type { DesignManifest } from "../types/artifacts";

const design: DesignManifest = {
  model_id: "house",
  model_name: "House",
  elements: [
    { id: "wall.1", name: "North wall", category: "Walls", physical: true, material_id: "wood" },
    { id: "axis.x", name: "X axis", category: "Helpers", physical: false },
  ],
};

describe("artifact metadata", () => {
  it("validates design and build manifests", () => {
    expect(validateDesignManifest(design).model_name).toBe("House");
    expect(validateBuildManifest({ artifacts: [], validation_status: "passed" }).validation_status).toBe("passed");
    expect(() => validateDesignManifest({ elements: [] })).toThrow(/model_id/);
    expect(() => validateBuildManifest({ artifacts: {} })).toThrow(/array/);
  });

  it("joins element metadata to quantities and groups physical elements", () => {
    const index = new MetadataIndex(design, [{ element_id: "wall.1", volume_mm3: 2_000_000_000 }]);
    expect(index.elements.get("wall.1")?.quantities?.volume_mm3).toBe(2_000_000_000);
    expect([...index.categories().keys()]).toEqual(["Walls"]);
  });
});
