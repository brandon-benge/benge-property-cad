export type MeasurementSystem = "metric" | "us";

const MILLIMETRES_PER_INCH = 25.4;
const MILLIMETRES_PER_FOOT = 304.8;
const MILLIMETRES_PER_YARD = 914.4;
const SQUARE_MILLIMETRES_PER_SQUARE_FOOT = MILLIMETRES_PER_FOOT ** 2;
const CUBIC_MILLIMETRES_PER_CUBIC_FOOT = MILLIMETRES_PER_FOOT ** 3;
const CUBIC_MILLIMETRES_PER_CUBIC_YARD = MILLIMETRES_PER_YARD ** 3;
const POUNDS_PER_KILOGRAM = 2.2046226218;

export function formatLength(valueMm: number, system: MeasurementSystem): string {
  if (system === "metric") {
    if (Math.abs(valueMm) < 1_000) return `${formatNumber(valueMm, 2)} mm`;
    return `${formatNumber(valueMm / 1_000, 3)} m`;
  }
  const absoluteInches = Math.abs(valueMm / MILLIMETRES_PER_INCH);
  if (absoluteInches < 36) return `${formatNumber(valueMm / MILLIMETRES_PER_INCH, 3)} in`;
  if (absoluteInches < 27 * 12) return `${formatNumber(valueMm / MILLIMETRES_PER_FOOT, 3)} ft`;
  return `${formatNumber(valueMm / MILLIMETRES_PER_YARD, 3)} yd`;
}

export function formatArea(valueMm2: number | null | undefined, system: MeasurementSystem): string {
  if (valueMm2 == null) return "—";
  if (system === "metric") return `${formatNumber(valueMm2 / 1_000_000, 3)} m²`;
  return `${formatNumber(valueMm2 / SQUARE_MILLIMETRES_PER_SQUARE_FOOT, 3)} ft²`;
}

export function formatVolume(valueMm3: number | null | undefined, system: MeasurementSystem): string {
  if (valueMm3 == null) return "—";
  if (system === "metric") return `${formatNumber(valueMm3 / 1_000_000_000, 4)} m³`;
  if (Math.abs(valueMm3) < CUBIC_MILLIMETRES_PER_CUBIC_YARD) {
    return `${formatNumber(valueMm3 / CUBIC_MILLIMETRES_PER_CUBIC_FOOT, 3)} ft³`;
  }
  return `${formatNumber(valueMm3 / CUBIC_MILLIMETRES_PER_CUBIC_YARD, 3)} yd³`;
}

export function formatMass(valueKg: number | null | undefined, system: MeasurementSystem): string {
  if (valueKg == null) return "—";
  return system === "metric"
    ? `${formatNumber(valueKg, 3)} kg`
    : `${formatNumber(valueKg * POUNDS_PER_KILOGRAM, 3)} lb`;
}

export function formatMeasurementValue(key: string, value: unknown, system: MeasurementSystem): string {
  if (typeof value !== "number") return formatValue(value);
  if (key.endsWith("_mm3")) return formatVolume(value, system);
  if (key.endsWith("_mm2")) return formatArea(value, system);
  if (key.endsWith("_mm")) return formatLength(value, system);
  if (key.endsWith("_kg")) return formatMass(value, system);
  return formatNumber(value, 4);
}

export function measurementLabel(key: string): string {
  return humanize(key.replace(/_(?:mm3|mm2|mm|kg)$/, ""));
}

export function formatRange(minimumMm: number, maximumMm: number, system: MeasurementSystem): string {
  return `${formatLength(minimumMm, system)} – ${formatLength(maximumMm, system)}`;
}

function formatNumber(value: number, maximumFractionDigits: number): string {
  return value.toLocaleString(undefined, { maximumFractionDigits });
}

function humanize(value: string): string {
  return value.replaceAll("_", " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatValue(value: unknown): string {
  if (value == null || value === "") return "—";
  return typeof value === "object" ? JSON.stringify(value) : String(value);
}
