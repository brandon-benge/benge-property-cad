export interface PrepareOptions {
  source: string;
  destination: string;
  repository?: string | null;
}

export interface PreparedManifest {
  schemaVersion: number;
  files: Array<{ path: string; kind: string; size: number }>;
  model: string;
}

export function prepareModel(options: PrepareOptions): Promise<PreparedManifest>;
