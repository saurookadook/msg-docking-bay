/**
 * @description Parses a JSON string without throwing.
 * @returns the parsed value, or `null` when `text` is not valid JSON
 * @todo Move to `@app/shared` once the shared workspace exists.
 */
export function safeParseJSON(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}
