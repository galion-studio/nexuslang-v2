export const PAYMENT_SURFACES = ["galion_one", "galion_voice", "galion_research"] as const;

export type PaymentSurface = (typeof PAYMENT_SURFACES)[number];

export type Finality = "pending" | "safe" | "finalized" | "reorged" | "failed";

export type LedgerStatus = "reserved" | "posted" | "released" | "refunded";

/**
 * Proposed accounting threshold for Amoy experiments. Testnet finality is not
 * production finality. Owners still have to approve the number.
 */
export const FINALITY_CONFIRMATIONS = 64;

export interface PaymentSession {
  sessionId: string;
  /** Internal account id. Not an email and not a wallet. */
  accountId: string;
  surface: PaymentSurface;
  /** Optional payment instrument. It does not identify the account. */
  walletAddress?: string;
}

export interface ServiceQuote {
  quoteId: string;
  settlementId: string;
  surface: PaymentSurface;
  accountId: string;
  sku: string;
  /** Integer service-credit atoms. Not the volatile token and not a fiat amount. */
  serviceCredits: bigint;
  /** Smallest token units locked by this quote. The contract does not store this price. */
  tokenAmount: bigint;
  chainId: 80002;
  expiresAtUnix: number;
}

export interface PaymentConfirmation {
  quoteId: string;
  settlementId: string;
  txHash: string;
  logIndex: number;
  chainId: number;
  confirmations: number;
  finality: Finality;
  tokenAmount: bigint;
}

export interface LedgerEntry {
  entryId: string;
  accountId: string;
  surface: PaymentSurface;
  sku: string;
  serviceCreditsDelta: bigint;
  settlementId: string;
  quoteId: string;
  usageId: string;
  txHash: string;
  status: LedgerStatus;
  reasonCode: string;
}
