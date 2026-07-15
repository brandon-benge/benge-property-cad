import type { ArtifactBundle, DownloadManifest, QuantityRecord } from "../types/artifacts";
import { validateBuildManifest, validateDesignManifest } from "./metadata";

export function modelUrl(relativePath: string): string {
  const base = new URL("model/", document.baseURI);
  return new URL(relativePath, base).toString();
}

async function fetchJson<T>(url: string, description: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Unable to load ${description} (${response.status})`);
  try {
    return (await response.json()) as T;
  } catch {
    throw new Error(`${description} is not valid JSON`);
  }
}

export async function loadArtifactBundle(): Promise<ArtifactBundle> {
  const downloads = await fetchJson<DownloadManifest>(modelUrl("download-manifest.json"), "download manifest");
  if (!downloads.model || !downloads.designElements || !downloads.buildManifest || !Array.isArray(downloads.files)) {
    throw new Error("Download manifest is missing required artifact paths");
  }
  const [designValue, buildValue] = await Promise.all([
    fetchJson<unknown>(modelUrl(downloads.designElements), "design metadata"),
    fetchJson<unknown>(modelUrl(downloads.buildManifest), "build manifest"),
  ]);
  const quantitiesFile = downloads.files.find((file) => file.kind === "quantities-json");
  const quantities = quantitiesFile
    ? await fetchJson<QuantityRecord[]>(modelUrl(quantitiesFile.path), "quantities")
    : [];
  return {
    downloads,
    design: validateDesignManifest(designValue),
    build: validateBuildManifest(buildValue),
    quantities: Array.isArray(quantities) ? quantities : [],
  };
}
