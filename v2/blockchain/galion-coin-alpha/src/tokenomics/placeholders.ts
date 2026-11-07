/**
 * Development-only names. These are not a token naming decision and not market facts.
 * The contract takes name and symbol as initializer arguments so this file is not on-chain.
 */
export const DEV_TOKEN_PLACEHOLDER = {
  status: "DEVELOPMENT_PLACEHOLDER_NOT_A_NAMING_DECISION",
  name: "Galion Alpha Placeholder",
  symbol: "GLNDEV",
  decimals: 18,
} as const;

/** Polygon PoS Amoy. The only chain id the alpha contracts accept. */
export const POLYGON_AMOY_CHAIN_ID = 80002;

/**
 * Unapproved supply proposal, in whole tokens. The contract cap is whatever
 * the initializer receives. This constant is not compiled into the contracts.
 */
export const PROPOSED_MAX_WHOLE_TOKENS = 1_000_000_000n;

export const PROPOSAL_STATUS = "UNAPPROVED_DESIGN_PROPOSAL" as const;
