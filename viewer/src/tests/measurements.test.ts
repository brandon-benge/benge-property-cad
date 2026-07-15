import { describe, expect, it } from "vitest";
import { createAppShell, renderProperties } from "../ui/render";
import { formatArea, formatLength, formatMass, formatVolume } from "../ui/measurements";
import type { ElementMetadata } from "../types/artifacts";

const item: ElementMetadata = {
  id: "deck.post.1",
  name: "Deck post",
  category: "Structure",
  placement: { translation_mm: [25.4, 3048, 9144] },
  bounds_mm: [0, 25.4, 3048, 914.4, 609.6, 12192],
  dimensions: { width_mm: 152.4, height_mm: 3048, extras: { footing_depth_mm: 914.4 } },
  quantities: { element_id: "deck.post.1", area_mm2: 92_903.04, volume_mm3: 764_554_857.984, mass_kg: 10 },
};

describe("measurement presentation", () => {
  it("uses adaptive metric and US customary length units", () => {
    expect(formatLength(25.4, "us")).toBe("1 in");
    expect(formatLength(3048, "us")).toBe("10 ft");
    expect(formatLength(9144, "us")).toBe("10 yd");
    expect(formatLength(3048, "metric")).toBe("3.048 m");
  });

  it("converts area, volume, and mass consistently", () => {
    expect(formatArea(92_903.04, "us")).toBe("1 ft²");
    expect(formatVolume(764_554_857.984, "us")).toBe("1 yd³");
    expect(formatMass(1, "us")).toBe("2.205 lb");
  });

  it("renders CAD origins, occupied extents, dimensions, and quantities in the selected system", () => {
    const container = document.createElement("div");
    renderProperties(container, item, "us");
    expect(container.textContent).toContain("Position");
    expect(container.textContent).toContain("X origin1 in");
    expect(container.textContent).toContain("Y origin10 ft");
    expect(container.textContent).toContain("Z origin10 yd");
    expect(container.textContent).toContain("X range0 in – 3 ft");
    expect(container.textContent).toContain("Footing Depth3 ft");
    expect(container.textContent).toContain("Area1 ft²");
    expect(container.textContent).toContain("Volume1 yd³");
  });

  it("includes accessible unit and axes controls in the application shell", () => {
    const root = document.createElement("div");
    createAppShell(root);
    expect(root.querySelector<HTMLSelectElement>("#measurement-system")?.options).toHaveLength(2);
    expect(root.querySelector<HTMLButtonElement>("[data-view='axes']")?.getAttribute("aria-pressed")).toBe("true");
    expect(root.querySelector("#axis-legend")?.textContent).toBe("XYZ");
  });
});
