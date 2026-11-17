/**
 * Fields that must never be written to a chain event, a public IPFS blob,
 * or this alpha's payment records. Matching is case-insensitive.
 */
export const FORBIDDEN_PAYLOAD_KEYS = [
  "prompt",
  "prompts",
  "pii",
  "email",
  "name",
  "phone",
  "addressline",
  "secret",
  "secrets",
  "apikey",
  "api_key",
  "mnemonic",
  "privatekey",
  "private_key",
  "seed",
  "password",
  "transcript",
  "content",
  "message",
  "messages",
] as const;

const FORBIDDEN = new Set<string>(FORBIDDEN_PAYLOAD_KEYS);

export function assertNoPrivatePayload(value: unknown, path = "payload"): void {
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertNoPrivatePayload(item, `${path}[${index}]`));
    return;
  }
  if (value !== null && typeof value === "object") {
    for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
      if (FORBIDDEN.has(key.toLowerCase())) {
        throw new Error(
          `Refusing field ${path}.${key}: prompts, personal data, and secrets stay off-chain and off public IPFS`
        );
      }
      assertNoPrivatePayload(child, `${path}.${key}`);
    }
  }
}
