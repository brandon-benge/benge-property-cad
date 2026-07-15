import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

describe("mobile layout", () => {
  it("defines touch, safe-area, orientation-friendly, and bottom-sheet rules", () => {
    const css = readFileSync("src/styles.css", "utf8");
    expect(css).toContain("@media (max-width: 760px)");
    expect(css).toContain("env(safe-area-inset-bottom)");
    expect(css).toContain("touch-action: none");
    expect(css).toContain(".property-panel.has-selection");
  });
});
