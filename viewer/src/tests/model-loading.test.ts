import { ShaderStore } from "@babylonjs/core/Engines/shaderStore";
import { _ImportHelper } from "@babylonjs/core/import.helper";
import { describe, expect, it } from "vitest";
import { axisScaleForBounds, cadAxisDirections, clippingRange, progressValue } from "../viewer/designViewer";

describe("GLB loading feedback", () => {
  it("calculates determinate progress when the loader reports a total", () => {
    expect(progressValue({ lengthComputable: true, loaded: 50, total: 200 })).toEqual({ loaded: 50, total: 200, percent: 25 });
  });

  it("keeps streaming progress indeterminate without a content length", () => {
    expect(progressValue({ lengthComputable: false, loaded: 512, total: 0 })).toEqual({ loaded: 512, total: null, percent: null });
  });

  it("expands the clipping range for building-scale models measured in millimetres", () => {
    const diagonal = 30_000;
    const range = clippingRange(diagonal);
    expect(range.minimum).toBeLessThan(5);
    expect(range.maximum).toBeGreaterThan(diagonal * 10);
    expect(range.maximum).toBeGreaterThan(diagonal * 1.1);
  });

  it("maps the CAD X/Y/Z axes into Babylon's loaded scene coordinates", () => {
    const axes = cadAxisDirections();
    expect(axes.x.asArray()).toEqual([-1, 0, 0]);
    expect(axes.y.asArray()).toEqual([0, 0, -1]);
    expect(axes.z.asArray()).toEqual([0, 1, 0]);
    expect(axisScaleForBounds(10_000)).toBeCloseTo(350);
  });

  it("registers the highlight shaders instead of fetching them from the Vite fallback", () => {
    expect(ShaderStore.ShadersStore.glowMapGenerationVertexShader).toContain("void main");
    expect(ShaderStore.ShadersStore.glowMapGenerationPixelShader).toContain("void main");
    expect(ShaderStore.ShadersStore.glowMapMergeVertexShader).toContain("void main");
    expect(ShaderStore.ShadersStore.glowMapMergePixelShader).toContain("void main");
  });

  it("registers the default shaders used by the axes viewer", () => {
    expect(ShaderStore.ShadersStore.defaultVertexShader).toContain("void main");
    expect(ShaderStore.ShadersStore.defaultPixelShader).toContain("void main");
  });

  it("registers the PBR shaders used by prepared GLB materials", () => {
    expect(ShaderStore.ShadersStore.pbrVertexShader).toContain("void main");
    expect(ShaderStore.ShadersStore.pbrPixelShader).toContain("void main");
    expect(ShaderStore.ShadersStore.rgbdDecodePixelShader).toContain("void main");
  });

  it("registers Babylon's ray implementation for mesh picking", () => {
    expect(_ImportHelper._IsPickingAvailable).toBe(true);
  });
});
