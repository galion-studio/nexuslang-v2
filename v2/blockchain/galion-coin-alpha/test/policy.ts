import { expect } from "chai";
import { readFileSync } from "fs";
import { proposedDistribution } from "../src/tokenomics/distribution";
import { DEV_TOKEN_PLACEHOLDER, PROPOSED_MAX_WHOLE_TOKENS } from "../src/tokenomics/placeholders";
import { emptyFaucetState, evaluateFaucetClaim, FAUCET_POLICY, type FaucetClaimRequest } from "../src/faucet/policy";
import { ServiceCreditLedger } from "../src/payments/ledger";
import { assertNoPrivatePayload } from "../src/payments/privacy";
import { FINALITY_CONFIRMATIONS, type PaymentConfirmation, type ServiceQuote } from "../src/payments/types";

const ADDRESS = "0x1111111111111111111111111111111111111111";
const OTHER = "0x2222222222222222222222222222222222222222";
const IP_A = "0x" + "ab".repeat(32);
const IP_B = "0x" + "cd".repeat(32);
const NOW = 1_700_000_000;

function claim(overrides: Partial<FaucetClaimRequest> = {}): FaucetClaimRequest {
  return {
    chainId: 80002,
    address: ADDRESS,
    ipHash: IP_A,
    idempotencyKey: "claim-1",
    amount: FAUCET_POLICY.perAddressMaxAmount,
    nowUnix: NOW,
    ...overrides,
  };
}

function quote(overrides: Partial<ServiceQuote> = {}): ServiceQuote {
  return {
    quoteId: "quote-1",
    settlementId: "settle-1",
    surface: "galion_one",
    accountId: "acct-opaque",
    sku: "credit_pack_100",
    serviceCredits: 100n,
    tokenAmount: 5n * 10n ** 18n,
    chainId: 80002,
    expiresAtUnix: NOW + 600,
    ...overrides,
  };
}

function confirmation(overrides: Partial<PaymentConfirmation> = {}): PaymentConfirmation {
  return {
    quoteId: "quote-1",
    settlementId: "settle-1",
    txHash: "0x" + "11".repeat(32),
    logIndex: 0,
    chainId: 80002,
    confirmations: FINALITY_CONFIRMATIONS,
    finality: "finalized",
    tokenAmount: 5n * 10n ** 18n,
    ...overrides,
  };
}

describe("proposed distribution", function () {
  it("keeps the placeholder out of market language and sums the unapproved cap", function () {
    expect(DEV_TOKEN_PLACEHOLDER.status).to.equal("DEVELOPMENT_PLACEHOLDER_NOT_A_NAMING_DECISION");
    const distribution = proposedDistribution();
    expect(distribution.status).to.equal("UNAPPROVED_DESIGN_PROPOSAL");
    expect(distribution.bpsTotal).to.equal(10_000);
    expect(distribution.wholeTotal).to.equal(PROPOSED_MAX_WHOLE_TOKENS);
    expect(distribution.buckets.map((bucket) => bucket.id)).to.deep.equal([
      "protocol_reserve",
      "credit_settlement_inventory",
      "contributors",
      "ecosystem_programs",
      "partnerships",
      "community_access",
    ]);
  });
});

describe("faucet policy", function () {
  it("accepts one drip per address and ignores an identical replay", function () {
    const first = evaluateFaucetClaim(emptyFaucetState(), claim());
    expect(first.accept).to.equal(true);
    expect(first.replay).to.equal(false);
    expect(first.nextState.claims).to.have.length(1);

    const replay = evaluateFaucetClaim(first.nextState, claim());
    expect(replay.accept).to.equal(true);
    expect(replay.replay).to.equal(true);
    expect(replay.nextState.claims).to.have.length(1);

    const second = evaluateFaucetClaim(first.nextState, claim({ idempotencyKey: "claim-2", nowUnix: NOW + 10 }));
    expect(second.accept).to.equal(false);
    expect(second.reason).to.equal("address rate limit");
    expect(second.nextState.claims).to.have.length(1);
  });

  it("caps an ip hash, the global window, and refuses raw IPs or other chains", function () {
    let state = emptyFaucetState();
    for (let index = 0; index < 3; index += 1) {
      const decision = evaluateFaucetClaim(state, claim({
        address: `0x${(index + 1).toString(16).padStart(40, "0")}`,
        idempotencyKey: `ip-${index}`,
        amount: 1n,
      }));
      expect(decision.accept).to.equal(true);
      state = decision.nextState;
    }
    const fourth = evaluateFaucetClaim(state, claim({
      address: OTHER,
      idempotencyKey: "ip-3",
      amount: 1n,
    }));
    expect(fourth.reason).to.equal("ip hash rate limit");

    const huge = evaluateFaucetClaim(emptyFaucetState(), claim({
      address: OTHER,
      ipHash: IP_B,
      idempotencyKey: "global",
      amount: FAUCET_POLICY.globalMaxAmountPerWindow + 1n,
    }));
    expect(huge.reason).to.equal("amount is outside the per-address drip");

    expect(evaluateFaucetClaim(emptyFaucetState(), claim({ ipHash: "127.0.0.1" })).reason).to.equal(
      "ipHash must be a 32-byte hex hash, not a raw address or IP"
    );
    expect(evaluateFaucetClaim(emptyFaucetState(), claim({ chainId: 1 })).accept).to.equal(false);
    expect(evaluateFaucetClaim(emptyFaucetState(), claim({ chainId: 31337 })).accept).to.equal(false);

    const conflict = evaluateFaucetClaim(state, claim({ amount: 1n, idempotencyKey: "ip-0" }));
    expect(conflict.reason).to.equal("idempotency key conflicts with an earlier claim");
  });

  it("keeps keys and RPC URLs out of the policy module", function () {
    const source = readFileSync("src/faucet/policy.ts", "utf8");
    expect(source.toLowerCase().includes("private_key")).to.equal(false);
    expect(source.toLowerCase().includes("mnemonic")).to.equal(false);
    expect(source.includes("https://")).to.equal(false);
  });
});

describe("service credit ledger", function () {
  it("posts credits only after finality and does not double-post a replay", function () {
    const ledger = new ServiceCreditLedger();
    const reserved = ledger.reserve(quote(), NOW);
    expect(reserved.status).to.equal("reserved");
    expect(ledger.balance("acct-opaque", "galion_one")).to.equal(0n);
    expect(ledger.reserve(quote(), NOW).entryId).to.equal(reserved.entryId);

    const pending = ledger.applyConfirmation(quote(), confirmation({
      finality: "pending",
      confirmations: 2,
    }), NOW);
    expect(pending.status).to.equal("reserved");
    expect(ledger.balance("acct-opaque", "galion_one")).to.equal(0n);

    const posted = ledger.applyConfirmation(quote(), confirmation(), NOW);
    expect(posted.status).to.equal("posted");
    expect(ledger.balance("acct-opaque", "galion_one")).to.equal(100n);
    const replay = ledger.applyConfirmation(quote(), confirmation(), NOW);
    expect(replay.entryId).to.equal(posted.entryId);
    expect(ledger.balance("acct-opaque", "galion_one")).to.equal(100n);
  });

  it("meters usage once, releases a failed quote, and refunds an unused grant once", function () {
    const ledger = new ServiceCreditLedger();
    ledger.reserve(quote(), NOW);
    ledger.applyConfirmation(quote(), confirmation(), NOW);
    ledger.consume({
      accountId: "acct-opaque",
      surface: "galion_one",
      usageId: "use-1",
      sku: "nexuslang_execution",
      serviceCredits: 40n,
    });
    ledger.consume({
      accountId: "acct-opaque",
      surface: "galion_one",
      usageId: "use-1",
      sku: "nexuslang_execution",
      serviceCredits: 40n,
    });
    expect(ledger.balance("acct-opaque", "galion_one")).to.equal(60n);
    expect(() => ledger.refund("settle-1", "service_unavailable")).to.throw(/already used/);

    const voice = new ServiceCreditLedger();
    voice.reserve(quote({ surface: "galion_voice", quoteId: "q-voice", settlementId: "s-voice" }), NOW);
    voice.applyConfirmation(
      quote({ surface: "galion_voice", quoteId: "q-voice", settlementId: "s-voice" }),
      confirmation({ quoteId: "q-voice", settlementId: "s-voice" }),
      NOW
    );
    const refund = voice.refund("s-voice", "service_unavailable");
    expect(refund.status).to.equal("refunded");
    expect(voice.balance("acct-opaque", "galion_voice")).to.equal(0n);
    expect(() => voice.refund("s-voice", "service_unavailable")).to.throw(/already refunded/);

    const failed = new ServiceCreditLedger();
    failed.reserve(quote({ surface: "galion_research", quoteId: "q-r", settlementId: "s-r" }), NOW);
    const released = failed.applyConfirmation(
      quote({ surface: "galion_research", quoteId: "q-r", settlementId: "s-r" }),
      confirmation({ quoteId: "q-r", settlementId: "s-r", finality: "failed", confirmations: 0 }),
      NOW
    );
    expect(released.status).to.equal("released");
    expect(failed.balance("acct-opaque", "galion_research")).to.equal(0n);
    expect(() => failed.applyConfirmation(
      quote({ surface: "galion_research", quoteId: "q-r", settlementId: "s-r" }),
      confirmation({ quoteId: "q-r", settlementId: "s-r" }),
      NOW
    )).to.throw(/cannot post/);
  });

  it("refuses prompts, personal data, expired quotes, and other chains", function () {
    expect(() => assertNoPrivatePayload({ sku: "credit_pack_100" })).to.not.throw();
    expect(() => assertNoPrivatePayload({ prompt: "hello" })).to.throw(/off public IPFS/);
    expect(() => assertNoPrivatePayload({ nested: { email: "a@example.com" } })).to.throw(/email/);

    const ledger = new ServiceCreditLedger();
    expect(() => ledger.reserve({ ...quote(), prompt: "secret prompt" } as ServiceQuote, NOW)).to.throw(/prompt/);
    // Negative fixture only. Chain id 137 is not a configured network.
    expect(() => ledger.reserve(quote({ chainId: 137 as 80002 }), NOW)).to.throw(/Amoy/);
    expect(() => ledger.reserve(quote(), quote().expiresAtUnix)).to.throw(/expired/);
    expect(() => ledger.reserve(quote({ serviceCredits: 0n }), NOW)).to.throw(/positive integer/);
  });
});
