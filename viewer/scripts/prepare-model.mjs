#!/usr/bin/env node

import { copyFile, mkdir, readFile, readdir, rm, stat, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SUPPORTED_EXTENSIONS = new Set([".glb", ".step", ".stp", ".ifc", ".svg", ".dxf", ".pdf", ".json", ".csv"]);
const REQUIRED_FILES = ["manifests/build-manifest.json", "manifests/design-elements.json"];

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === "--source" || value === "--destination") {
      const next = argv[index + 1];
      if (!next) throw new Error(`${value} requires a path`);
      values[value.slice(2)] = next;
      index += 1;
    } else {
      throw new Error(`Unknown option: ${value}`);
    }
  }
  return values;
}

async function readJson(filePath) {
  try {
    return JSON.parse(await readFile(filePath, "utf8"));
  } catch (error) {
    throw new Error(`Cannot parse JSON artifact ${filePath}: ${error.message}`);
  }
}

async function walk(directory, root = directory) {
  const result = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) result.push(...(await walk(absolute, root)));
    else if (entry.isFile()) result.push(path.relative(root, absolute).split(path.sep).join("/"));
  }
  return result.sort();
}

function safeArtifactPath(relativePath) {
  const normalized = path.posix.normalize(relativePath);
  return normalized !== ".." && !normalized.startsWith("../") && !path.posix.isAbsolute(normalized);
}

function fileKind(relativePath) {
  const extension = path.extname(relativePath).toLowerCase();
  if (extension === ".glb") return "model";
  if (extension === ".step" || extension === ".stp") return "step";
  if (extension === ".ifc") return "ifc";
  if (extension === ".svg") return "drawing-svg";
  if (extension === ".dxf") return "drawing-dxf";
  if (extension === ".pdf") return "drawing-pdf";
  if (relativePath.endsWith("quantities.json")) return "quantities-json";
  if (extension === ".csv") return "csv";
  return "json";
}

function labelFor(relativePath) {
  const stem = path.basename(relativePath, path.extname(relativePath));
  return stem.replaceAll("_", " ").replaceAll("-", " ");
}

export async function prepareModel({ source, destination, repository = process.env.GITHUB_REPOSITORY || null }) {
  const sourceRoot = path.resolve(source);
  const destinationRoot = path.resolve(destination);
  for (const relativePath of REQUIRED_FILES) {
    try {
      if (!(await stat(path.join(sourceRoot, relativePath))).isFile()) throw new Error("not a file");
    } catch {
      throw new Error(`Required generated artifact is missing: ${relativePath}. Run python build.py first.`);
    }
  }

  const buildManifest = await readJson(path.join(sourceRoot, "manifests/build-manifest.json"));
  if (!Array.isArray(buildManifest.artifacts)) {
    throw new Error("Invalid build manifest: artifacts must be an array");
  }
  for (const artifact of buildManifest.artifacts) {
    if (typeof artifact?.path !== "string" || !safeArtifactPath(artifact.path)) {
      throw new Error(`Invalid artifact path in build manifest: ${String(artifact?.path)}`);
    }
    try {
      if (!(await stat(path.join(sourceRoot, artifact.path))).isFile()) throw new Error("not a file");
    } catch {
      throw new Error(`Build manifest references a missing artifact: ${artifact.path}`);
    }
  }

  const available = await walk(sourceRoot);
  const supported = available.filter((relativePath) => SUPPORTED_EXTENSIONS.has(path.extname(relativePath).toLowerCase()));
  const glbFiles = supported.filter((relativePath) => path.extname(relativePath).toLowerCase() === ".glb");
  if (glbFiles.length === 0) {
    throw new Error("Required generated artifact is missing: a .glb model. Run python build.py with the glb exporter.");
  }
  if (glbFiles.length > 1) {
    throw new Error(`Expected one generated GLB model, found ${glbFiles.length}: ${glbFiles.join(", ")}`);
  }

  await mkdir(destinationRoot, { recursive: true });
  for (const entry of await readdir(destinationRoot, { withFileTypes: true })) {
    if (entry.name !== ".gitignore") await rm(path.join(destinationRoot, entry.name), { recursive: true, force: true });
  }

  const files = [];
  for (const relativePath of supported) {
    const sourcePath = path.join(sourceRoot, relativePath);
    const targetPath = path.join(destinationRoot, relativePath);
    await mkdir(path.dirname(targetPath), { recursive: true });
    await copyFile(sourcePath, targetPath);
    const info = await stat(sourcePath);
    files.push({
      path: relativePath,
      name: labelFor(relativePath),
      extension: path.extname(relativePath).slice(1).toUpperCase(),
      kind: fileKind(relativePath),
      size: info.size,
    });
  }

  const runMetadataPath = path.join(sourceRoot, "manifests/run-metadata.json");
  const runMetadata = supported.includes("manifests/run-metadata.json") ? await readJson(runMetadataPath) : null;
  const downloadManifest = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    repository,
    model: glbFiles[0],
    designElements: "manifests/design-elements.json",
    buildManifest: "manifests/build-manifest.json",
    runMetadata: runMetadata ? "manifests/run-metadata.json" : null,
    buildTimestamp: buildManifest.build_timestamp_utc || runMetadata?.timestamp_utc || null,
    files,
  };
  await writeFile(path.join(destinationRoot, "download-manifest.json"), `${JSON.stringify(downloadManifest, null, 2)}\n`, "utf8");
  return downloadManifest;
}

async function main() {
  const scriptDirectory = path.dirname(fileURLToPath(import.meta.url));
  const viewerRoot = path.resolve(scriptDirectory, "..");
  const args = parseArgs(process.argv.slice(2));
  const source = args.source ? path.resolve(args.source) : path.resolve(viewerRoot, "..", "generated");
  const destination = args.destination ? path.resolve(args.destination) : path.resolve(viewerRoot, "public", "model");
  const manifest = await prepareModel({ source, destination });
  console.log(`Prepared ${manifest.files.length} artifacts from ${source}`);
  console.log(`GLB model: ${manifest.model}`);
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  main().catch((error) => {
    console.error(`prepare-model failed: ${error.message}`);
    process.exitCode = 1;
  });
}
