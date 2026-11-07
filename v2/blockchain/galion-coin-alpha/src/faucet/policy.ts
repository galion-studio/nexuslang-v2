import { POLYGON_AMOY_CHAIN_ID } from "../tokenomics/placeholders";

const WHOLE = 10n ** 18n;

/**
 * Unapproved testnet drip limits. These amounts are not a slice of the proposed
 * token cap and they are not production balances. The module holds no keys and
 * does not talk to a network.
 */
export const FAUCET_POLICY = {
  status: "UNAPPROVED_TESTNET_POLICY",
  chainId: POLYGON_AMOY_CHAIN_ID,
  windowSeconds: 24 * 60 * 60,
  maxClaimsPerAddressPerWindow: 1,
  maxClaimsPerIpHashPerWindow: 3,
  perAddressMaxAmount: 100n * WHOLE,
  globalMaxAmountPerWindow: 10_000n * WHOLE,
} as const;

export interface FaucetClaimRecord {
  address: string;
  ipHash: string;
  idempotencyKey: string;
  amount: bigint;
  atUnix: number;
}

export interface FaucetState {
  claims: readonly FaucetClaimRecord[];
}

export interface FaucetClaimRequest {
  chainId: number;
  address: string;
  /** Hash of the client address. Raw IPs are rejected. */
  ipHash: string;
  idempotencyKey: string;
  amount: bigint;
  nowUnix: number;
}

export interface FaucetDecision {
  accept: boolean;
  replay: boolean;
  reason: string;
  nextState: FaucetState;
}

const ADDRESS_RE = /^0x[0-9a-fA-F]{40}$/;
const HASH_RE = /^0x[0-9a-fA-F]{64}$/;

export function emptyFaucetState(): FaucetState {
  return { claims: [] };
}

export function evaluateFaucetClaim(state: FaucetState, request: FaucetClaimRequest): FaucetDecision {
  const reject = (reason: string): FaucetDecision => ({
    accept: false,
    replay: false,
    reason,
    nextState: state,
  });

  if (request.chainId !== FAUCET_POLICY.chainId) {
    return reject("chain must be Polygon Amoy 80002");
  }
  if (!ADDRESS_RE.test(request.address)) {
    return reject("address must be a 20-byte hex account");
  }
  if (!HASH_RE.test(request.ipHash)) {
    return reject("ipHash must be a 32-byte hex hash, not a raw address or IP");
  }
  if (request.idempotencyKey.trim().length === 0 || request.idempotencyKey.length > 128) {
    return reject("idempotency key is required");
  }
  if (request.amount <= 0n || request.amount > FAUCET_POLICY.perAddressMaxAmount) {
    return reject("amount is outside the per-address drip");
  }
  if (!Number.isInteger(request.nowUnix) || request.nowUnix < 0) {
    return reject("timestamp is invalid");
  }

  const address = request.address.toLowerCase();
  const ipHash = request.ipHash.toLowerCase();
  const existing = state.claims.find((claim) => claim.idempotencyKey === request.idempotencyKey);
  if (existing) {
    if (existing.address === address && existing.amount === request.amount && existing.ipHash === ipHash) {
      return {
        accept: true,
        replay: true,
        reason: "idempotent replay",
        nextState: state,
      };
    }
    return reject("idempotency key conflicts with an earlier claim");
  }

  const windowStart = request.nowUnix - FAUCET_POLICY.windowSeconds;
  const inWindow = state.claims.filter((claim) => claim.atUnix > windowStart);
  const addressClaims = inWindow.filter((claim) => claim.address === address);
  if (addressClaims.length >= FAUCET_POLICY.maxClaimsPerAddressPerWindow) {
    return reject("address rate limit");
  }
  const ipClaims = inWindow.filter((claim) => claim.ipHash === ipHash);
  if (ipClaims.length >= FAUCET_POLICY.maxClaimsPerIpHashPerWindow) {
    return reject("ip hash rate limit");
  }
  const windowTotal = inWindow.reduce((sum, claim) => sum + claim.amount, 0n);
  if (windowTotal + request.amount > FAUCET_POLICY.globalMaxAmountPerWindow) {
    return reject("global window cap");
  }

  const record: FaucetClaimRecord = {
    address,
    ipHash,
    idempotencyKey: request.idempotencyKey,
    amount: request.amount,
    atUnix: request.nowUnix,
  };
  return {
    accept: true,
    replay: false,
    reason: "accepted",
    nextState: { claims: [...state.claims, record] },
  };
}
