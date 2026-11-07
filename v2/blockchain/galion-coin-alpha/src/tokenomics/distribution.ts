import { PROPOSED_MAX_WHOLE_TOKENS, PROPOSAL_STATUS } from "./placeholders";

export interface ProposedBucket {
  id: string;
  /** Share of the proposed cap, in basis points. 10_000 is 100%. */
  bps: number;
  vesting: string;
}

/**
 * Unapproved allocation of the proposed cap. These rows are not minted by the
 * alpha contracts and are not a claim on assets, revenue, or service credits.
 */
export const PROPOSED_BUCKETS: readonly ProposedBucket[] = [
  {
    id: "protocol_reserve",
    bps: 2000,
    vesting: "Locked until a later owner action. This alpha does not mint the reserve.",
  },
  {
    id: "credit_settlement_inventory",
    bps: 3000,
    vesting: "Minted only against a unique settlement id when a service-credit quote is accepted.",
  },
  {
    id: "contributors",
    bps: 1500,
    vesting: "12 month cliff, then 36 month linear. No yield.",
  },
  {
    id: "ecosystem_programs",
    bps: 1500,
    vesting: "Milestone gated. No automatic drip and no yield.",
  },
  {
    id: "partnerships",
    bps: 1000,
    vesting: "6 month cliff, then 24 month linear. No yield.",
  },
  {
    id: "community_access",
    bps: 1000,
    vesting: "Not drawn by the Amoy faucet. The testnet drip is a separate, worthless exercise.",
  },
] as const;

export function proposedWholeTokens(bps: number): bigint {
  if (!Number.isInteger(bps) || bps < 0 || bps > 10_000) {
    throw new Error("bps must be an integer from 0 to 10000");
  }
  return (PROPOSED_MAX_WHOLE_TOKENS * BigInt(bps)) / 10_000n;
}

export function proposedDistribution() {
  const buckets = PROPOSED_BUCKETS.map((bucket) => ({
    ...bucket,
    wholeTokens: proposedWholeTokens(bucket.bps),
  }));
  const bpsTotal = buckets.reduce((sum, bucket) => sum + bucket.bps, 0);
  const wholeTotal = buckets.reduce((sum, bucket) => sum + bucket.wholeTokens, 0n);
  return {
    status: PROPOSAL_STATUS,
    capWholeTokens: PROPOSED_MAX_WHOLE_TOKENS,
    bpsTotal,
    wholeTotal,
    buckets,
  };
}
