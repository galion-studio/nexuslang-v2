import { assertNoPrivatePayload } from "./privacy";
import {
  FINALITY_CONFIRMATIONS,
  type LedgerEntry,
  type LedgerStatus,
  type PaymentConfirmation,
  type PaymentSurface,
  type ServiceQuote,
} from "./types";

export interface ConsumeRequest {
  accountId: string;
  surface: PaymentSurface;
  usageId: string;
  sku: string;
  serviceCredits: bigint;
}

/**
 * In-memory reference for service-credit accounting. It is not wired to
 * Galion One, Galion Voice, Galion Research, or Galion OS, and it does not
 * persist prompts or personal data. Posted credits are a usage allowance.
 * They are not redeemable for tokens or fiat by this ledger.
 */
export class ServiceCreditLedger {
  private readonly entries: LedgerEntry[] = [];
  private readonly balances = new Map<string, bigint>();
  private sequence = 0;

  balance(accountId: string, surface: PaymentSurface): bigint {
    return this.balances.get(balanceKey(accountId, surface)) ?? 0n;
  }

  list(): readonly LedgerEntry[] {
    return this.entries.map((entry) => ({ ...entry }));
  }

  reserve(quote: ServiceQuote, nowUnix: number): LedgerEntry {
    assertNoPrivatePayload(quote);
    assertQuoteShape(quote, nowUnix);
    const existing = this.entries.find((entry) => entry.quoteId === quote.quoteId || entry.settlementId === quote.settlementId);
    if (existing) {
      if (
        existing.quoteId === quote.quoteId &&
        existing.settlementId === quote.settlementId &&
        existing.accountId === quote.accountId &&
        existing.serviceCreditsDelta === quote.serviceCredits &&
        existing.status === "reserved"
      ) {
        return { ...existing };
      }
      throw new Error("quote or settlement id conflicts with an existing entry");
    }

    const entry = this.nextEntry({
      accountId: quote.accountId,
      surface: quote.surface,
      sku: quote.sku,
      serviceCreditsDelta: quote.serviceCredits,
      settlementId: quote.settlementId,
      quoteId: quote.quoteId,
      usageId: "",
      txHash: "",
      status: "reserved",
      reasonCode: "quote_reserved",
    });
    this.entries.push(entry);
    return { ...entry };
  }

  applyConfirmation(quote: ServiceQuote, confirmation: PaymentConfirmation, nowUnix: number): LedgerEntry {
    assertNoPrivatePayload(quote);
    assertNoPrivatePayload(confirmation);
    assertQuoteShape(quote, nowUnix);
    if (confirmation.quoteId !== quote.quoteId || confirmation.settlementId !== quote.settlementId) {
      throw new Error("confirmation does not match the quote");
    }
    if (confirmation.chainId !== 80002) {
      throw new Error("confirmation chain must be Polygon Amoy 80002");
    }
    if (!/^0x[0-9a-fA-F]{64}$/.test(confirmation.txHash)) {
      throw new Error("tx hash must be a 32-byte hex id");
    }
    if (confirmation.tokenAmount !== quote.tokenAmount) {
      throw new Error("token amount does not match the quoted amount");
    }

    const entry = this.requireEntry(quote.quoteId);
    if (confirmation.finality === "failed" || confirmation.finality === "reorged") {
      if (entry.status === "posted" || entry.status === "refunded") {
        throw new Error("a posted grant is not reversed automatically; it needs manual review");
      }
      entry.status = "released";
      entry.reasonCode = confirmation.finality;
      entry.txHash = confirmation.txHash;
      return { ...entry };
    }

    const finalized =
      confirmation.finality === "finalized" && confirmation.confirmations >= FINALITY_CONFIRMATIONS;
    if (!finalized) {
      return { ...entry };
    }
    if (entry.status === "posted") {
      if (entry.txHash !== confirmation.txHash) {
        throw new Error("posted settlement replay used a different transaction");
      }
      return { ...entry };
    }
    if (entry.status !== "reserved") {
      throw new Error(`cannot post credits from status ${entry.status}`);
    }

    entry.status = "posted";
    entry.txHash = confirmation.txHash;
    entry.reasonCode = "settlement_finalized";
    this.addBalance(entry.accountId, entry.surface, entry.serviceCreditsDelta);
    return { ...entry };
  }

  consume(request: ConsumeRequest): LedgerEntry {
    assertNoPrivatePayload(request);
    if (request.serviceCredits <= 0n) throw new Error("usage amount must be positive");
    if (request.usageId.trim().length === 0) throw new Error("usage id is required");
    if (request.sku.trim().length === 0) throw new Error("sku is required");

    const existing = this.entries.find((entry) => entry.usageId === request.usageId);
    if (existing) {
      if (
        existing.accountId === request.accountId &&
        existing.surface === request.surface &&
        existing.serviceCreditsDelta === -request.serviceCredits
      ) {
        return { ...existing };
      }
      throw new Error("usage id conflicts with an earlier debit");
    }

    const available = this.balance(request.accountId, request.surface);
    if (available < request.serviceCredits) {
      throw new Error("insufficient service credits");
    }

    const entry = this.nextEntry({
      accountId: request.accountId,
      surface: request.surface,
      sku: request.sku,
      serviceCreditsDelta: -request.serviceCredits,
      settlementId: "",
      quoteId: "",
      usageId: request.usageId,
      txHash: "",
      status: "posted",
      reasonCode: "usage_metered",
    });
    this.entries.push(entry);
    this.addBalance(request.accountId, request.surface, entry.serviceCreditsDelta);
    return { ...entry };
  }

  refund(settlementId: string, reasonCode: string): LedgerEntry {
    assertNoPrivatePayload({ reasonCode });
    if (!/^[a-z0-9_]{1,64}$/.test(reasonCode)) {
      throw new Error("reason code must be a short opaque slug");
    }
    const entry = this.entries.find((candidate) => candidate.settlementId === settlementId && candidate.serviceCreditsDelta > 0n);
    if (!entry) throw new Error("unknown settlement");
    if (entry.status === "refunded") {
      throw new Error("settlement was already refunded");
    }
    if (entry.status !== "posted") {
      throw new Error("only a posted grant can be refunded");
    }
    const available = this.balance(entry.accountId, entry.surface);
    if (available < entry.serviceCreditsDelta) {
      throw new Error("service credits were already used; refund needs manual review");
    }

    entry.status = "refunded";
    entry.reasonCode = reasonCode;
    this.addBalance(entry.accountId, entry.surface, -entry.serviceCreditsDelta);
    const reversal = this.nextEntry({
      accountId: entry.accountId,
      surface: entry.surface,
      sku: entry.sku,
      serviceCreditsDelta: -entry.serviceCreditsDelta,
      settlementId: entry.settlementId,
      quoteId: entry.quoteId,
      usageId: "",
      txHash: entry.txHash,
      status: "refunded",
      reasonCode,
    });
    this.entries.push(reversal);
    return { ...reversal };
  }

  private requireEntry(quoteId: string): LedgerEntry {
    const entry = this.entries.find((candidate) => candidate.quoteId === quoteId && candidate.serviceCreditsDelta > 0n);
    if (!entry) throw new Error("unknown quote");
    return entry;
  }

  private addBalance(accountId: string, surface: PaymentSurface, delta: bigint): void {
    const key = balanceKey(accountId, surface);
    this.balances.set(key, (this.balances.get(key) ?? 0n) + delta);
  }

  private nextEntry(fields: Omit<LedgerEntry, "entryId"> & { status: LedgerStatus }): LedgerEntry {
    this.sequence += 1;
    return { entryId: `entry-${this.sequence}`, ...fields };
  }
}

function assertQuoteShape(quote: ServiceQuote, nowUnix: number): void {
  if (quote.chainId !== 80002) throw new Error("quote chain must be Polygon Amoy 80002");
  if (quote.serviceCredits <= 0n) throw new Error("service credits must be a positive integer");
  if (quote.tokenAmount <= 0n) throw new Error("token amount must be a positive integer");
  if (quote.quoteId.trim().length === 0 || quote.settlementId.trim().length === 0) {
    throw new Error("quote id and settlement id are required");
  }
  if (quote.accountId.trim().length === 0 || quote.sku.trim().length === 0) {
    throw new Error("account id and sku are required");
  }
  if (nowUnix >= quote.expiresAtUnix) throw new Error("quote expired");
}

function balanceKey(accountId: string, surface: PaymentSurface): string {
  return `${surface}:${accountId}`;
}
