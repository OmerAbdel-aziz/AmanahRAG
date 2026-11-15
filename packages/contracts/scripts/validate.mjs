import { readdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const failures = [];

function read(path) {
  return readFileSync(join(root, path), "utf8");
}

for (const file of readdirSync(join(root, "events"))) {
  if (!file.endsWith(".schema.json")) continue;
  const path = `events/${file}`;
  try {
    const schema = JSON.parse(read(path));
    if (!schema.$schema?.includes("2020-12")) failures.push(`${path}: missing draft 2020-12 $schema`);
    if (schema.additionalProperties !== false) failures.push(`${path}: must set additionalProperties false`);
    if (!Array.isArray(schema.required) || schema.required.length === 0) {
      failures.push(`${path}: must declare required fields`);
    }
    if (!schema.properties?.event_type?.const) {
      failures.push(`${path}: must pin event_type with const`);
    }
  } catch (error) {
    failures.push(`${path}: ${error.message}`);
  }
}

for (const file of readdirSync(join(root, "openapi"))) {
  if (!file.endsWith(".yaml")) continue;
  const path = `openapi/${file}`;
  const text = read(path);
  if (!/^openapi:\s*3\.\d/m.test(text)) failures.push(`${path}: missing openapi 3.x header`);
  if (!/^paths:/m.test(text)) failures.push(`${path}: missing paths block`);
  if (!/^components:/m.test(text)) failures.push(`${path}: missing components block`);
}

if (failures.length > 0) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log("contracts: schemas parsed and invariants hold");
