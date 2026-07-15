export interface ArtifactFile {
  path: string;
  name: string;
  extension: string;
  kind: "model" | "step" | "ifc" | "drawing-svg" | "drawing-dxf" | "drawing-pdf" | "quantities-json" | "csv" | "json";
  size: number;
}

export interface DownloadManifest {
  schemaVersion: number;
  generatedAt: string;
  repository: string | null;
  model: string;
  designElements: string;
  buildManifest: string;
  runMetadata: string | null;
  buildTimestamp: string | null;
  files: ArtifactFile[];
}

export interface Dimensions {
  length_mm?: number | null;
  width_mm?: number | null;
  height_mm?: number | null;
  radius_mm?: number | null;
  extras?: Record<string, unknown>;
}

export interface Placement {
  translation_mm?: [number, number, number] | number[];
  rotation_deg_xyz?: [number, number, number] | number[];
}

export interface DesignElement {
  id: string;
  name?: string | null;
  category?: string | null;
  ifc_class?: string | null;
  material_id?: string | null;
  storey?: string | null;
  source_module?: string | null;
  dimensions?: Dimensions | null;
  tags?: string[];
  physical?: boolean;
  geometry_kind?: string | null;
  parent_id?: string | null;
  placement?: Placement;
  bounds_mm?: [number, number, number, number, number, number] | number[];
  properties?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface DesignManifest {
  model_id: string;
  model_name: string;
  metadata?: Record<string, unknown>;
  elements: DesignElement[];
  semantic_hash?: string;
}

export interface QuantityRecord {
  element_id: string;
  category?: string | null;
  material_id?: string | null;
  count?: number | null;
  area_mm2?: number | null;
  volume_mm3?: number | null;
  mass_kg?: number | null;
  provenance?: string | null;
}

export interface BuildManifest {
  tool_version?: string;
  git_sha?: string | null;
  build_timestamp_utc?: string | null;
  selected_exporters?: string[];
  model_element_count?: number;
  validation_status?: string;
  semantic_hash?: string;
  artifacts?: Array<{ path: string; size?: number; sha256?: string }>;
}

export interface ElementMetadata extends DesignElement {
  id: string;
  name: string;
  category: string;
  quantities?: QuantityRecord;
}

export interface GltfExtras {
  stable_id?: string;
  category?: string;
  source_module?: string;
  [key: string]: unknown;
}

export interface ArtifactBundle {
  downloads: DownloadManifest;
  design: DesignManifest;
  build: BuildManifest;
  quantities: QuantityRecord[];
}
