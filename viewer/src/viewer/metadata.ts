import type { AbstractMesh } from "@babylonjs/core/Meshes/abstractMesh";
import type { Node } from "@babylonjs/core/node";
import type {
  BuildManifest,
  DesignElement,
  DesignManifest,
  ElementMetadata,
  GltfExtras,
  QuantityRecord,
} from "../types/artifacts";

export function validateDesignManifest(value: unknown): DesignManifest {
  if (!value || typeof value !== "object") throw new Error("Design metadata is not an object");
  const candidate = value as Partial<DesignManifest>;
  if (typeof candidate.model_id !== "string" || typeof candidate.model_name !== "string" || !Array.isArray(candidate.elements)) {
    throw new Error("Design metadata is missing model_id, model_name, or elements");
  }
  if (candidate.elements.some((element) => !element || typeof element.id !== "string")) {
    throw new Error("Design metadata contains an element without a stable ID");
  }
  return candidate as DesignManifest;
}

export function validateBuildManifest(value: unknown): BuildManifest {
  if (!value || typeof value !== "object") throw new Error("Build manifest is not an object");
  const candidate = value as BuildManifest;
  if (candidate.artifacts !== undefined && !Array.isArray(candidate.artifacts)) {
    throw new Error("Build manifest artifacts must be an array");
  }
  return candidate;
}

export function gltfExtras(node: Node | AbstractMesh | null): GltfExtras {
  let current: Node | null = node;
  while (current) {
    const metadata = current.metadata as { gltf?: { extras?: GltfExtras }; extras?: GltfExtras } | null;
    const extras = metadata?.gltf?.extras ?? metadata?.extras;
    if (extras?.stable_id) return extras;
    current = current.parent;
  }
  return {};
}

export class MetadataIndex {
  readonly design: DesignManifest;
  readonly elements = new Map<string, ElementMetadata>();

  constructor(design: DesignManifest, quantities: QuantityRecord[]) {
    this.design = validateDesignManifest(design);
    const quantityById = new Map(quantities.map((item) => [item.element_id, item]));
    for (const element of design.elements) {
      this.elements.set(element.id, normalizeElement(element, quantityById.get(element.id)));
    }
  }

  resolve(node: Node | AbstractMesh | null): ElementMetadata | null {
    const extras = gltfExtras(node);
    if (!extras.stable_id) return null;
    const known = this.elements.get(extras.stable_id);
    if (known) return { ...known, ...extras, id: known.id, name: known.name, category: known.category };
    return {
      id: extras.stable_id,
      name: extras.stable_id,
      category: extras.category || "Uncategorized",
      ...extras,
    };
  }

  categories(): Map<string, ElementMetadata[]> {
    const groups = new Map<string, ElementMetadata[]>();
    for (const element of this.elements.values()) {
      if (element.physical === false) continue;
      const values = groups.get(element.category) ?? [];
      values.push(element);
      groups.set(element.category, values);
    }
    return new Map(
      [...groups.entries()]
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([name, values]) => [name, values.sort((left, right) => left.name.localeCompare(right.name))]),
    );
  }
}

function normalizeElement(element: DesignElement, quantities?: QuantityRecord): ElementMetadata {
  return {
    ...element,
    id: element.id,
    name: element.name || element.id,
    category: element.category || "Uncategorized",
    quantities,
  };
}
