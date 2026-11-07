# Galion coin alpha — design

**Status:** unapproved design proposal and unaudited code skeleton  
**Date:** 7 November 2026  
**Scope:** `v2/blockchain/galion-coin-alpha/` only  
**Network target of the contracts:** Polygon Amoy, chain id `80002`  
**Deployment:** disabled in this package, including Amoy. No broadcast, no funded wallet, no mainnet network entry.  
**Token name and symbol:** not decided. The development placeholder is configurable and is not written into the contract source.

Human author of record: Maciej Grajczyk

This document proposes how a Galion token could sit beside the service-credit meter already sketched for Nexus Lang. The figures in the tokenomics section are design proposals for an owner to accept or replace. They are not prices, not a circulating supply, and not a description of any issued asset.

## 1. What already exists

The source architecture is [v2/blockchain/docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md), version 1.0, marked planning. It separates three phases:

| Phase | Architecture statement | What is in this repository |
| --- | --- | --- |
| Phase 1, alpha | Centralized VPS, PostgreSQL, local backups, B2 offsite. Marked implemented. | No blockchain package existed beyond that document. |
| Phase 2, beta | PostgreSQL plus IPFS, with Filecoin for permanent storage. Marked planning. | The IPFS client snippet in the architecture doc is not a source file. There is no `ipfs.py`, no Filecoin client, and no sync daemon. |
| Phase 3, production | IPFS plus OrbitDB, Akash compute, Filecoin and Arweave, Ceramic identity, Polygon/zkSync payments. Marked roadmap. | Ceramic, OrbitDB, Akash, and zkSync are not implemented. No Solidity file existed before this branch. |

The payment sketches inside the architecture document are examples, not contracts:

- `UserRegistry` would store a Ceramic DID string and an on-chain credit balance, and `buyCredits` would price credits in native coin.
- `PaymentProcessor` would take a native-coin subscription and forward the value to an owner.

This alpha does not implement those sketches. A public mapping from address to DID and credit balance would publish identity linkage and usage capacity. Service credits stay off-chain. The token contract stores balances, a cap, role membership, and opaque settlement ids.

### Credits that already run off-chain

Nexus Lang v2 already meters usage in application storage. This alpha reads that meter and does not change it.

| Location | What it does today |
| --- | --- |
| `v2/backend/models/user.py` | `credits` is a float, default `100.0`. `deduct_credits` and `add_credits` mutate that column. The tier map in the same file lists 100, 1,000, 5,000, 25,000, and unlimited monthly credits. |
| `v2/backend/models/billing.py` | `Subscription.credits_included` and `credits_remaining` are integers, default 100. A `credits` table stores integer movements. A `transactions` table stores an integer credit count next to a fiat amount field. |
| `v2/backend/services/subscription_tiers.py` | Action limits per studio tier, plus `CREDIT_COSTS` for developer-platform metering (`nexuslang_execution` 1, `image_sd` 5, `image_dalle` 10, `video_5s` 20, `video_30s` 50, text rates per 1,000 tokens, `voice_tts` 3, `voice_stt` 2, and others). |
| `v2/frontend/pages/pricing.tsx` | Product-page copy: Free $0 / 100 credits, Creator $20 / 1,000, Professional $50 / 5,000, Business $200 / 25,000, each per month. |

Those dollar figures are existing subscription copy. This design does not reuse them as a token price or as a peg.

The float column and the integer billing tables disagree. This branch leaves both in place. The proposed ledger below uses integers.

Galion OS, Galion Voice, and Samantha workspaces were not opened and were not modified. Galion One, Galion Voice, and Galion Research appear here only as payment-surface names on an interface.

### Storage and identity, as proposed integrations

| Architecture piece | This alpha |
| --- | --- |
| IPFS and Filecoin for code, public assets, and encrypted backups | Unchanged proposal from the architecture doc. Payment records, prompts, and personal data are out of scope for public IPFS. |
| Ceramic DID and 3ID Connect | Future sign-in option. A DID is not an initializer argument and is not an event field. |
| OrbitDB on IPFS | Future store for public, non-sensitive replicas. The architecture sample opens writes to `*`. That mode is unfit for credits, prompts, or account records. The reference ledger in this package is in-memory and is not OrbitDB. |
| Polygon and zkSync | Contracts accept Polygon Amoy only. zkSync is not configured. There is no bridge. |

## 2. Two units, one quote

Users meet two different units.

**Service credits** are the metering unit for Galion OS and for the Nexus Lang actions above. Inside one quote, the credit count is an integer fixed for that quote. A later move in the token's market does not change how many credits that quote grants, and it does not change how many credits an action costs in `CREDIT_COSTS`. Service credits in this design are an allowance to run metered product actions. The contracts do not give the holder a right to convert credits into tokens, fiat, or any other asset.

**The token** is the proposed payment asset. Its market price can move. The contract does not store a price, an oracle, or a credit conversion rate. A quote, created off-chain, names both a credit count and a token amount for a few minutes. Paying that token amount, and reaching the finality rule below, is what posts the credits. The next quote can name a different token amount for the same credit pack.

Holding the token confers no share of revenue, no yield, and no contract right to exchange tokens or credits for fiat or for each other. A posted credit grant is consumed by product usage. Where a delivery fails before the credits are used, the off-chain ledger can reverse the grant. Tokens already pulled into the payment sink stay there unless a later, separate operating procedure says otherwise. That procedure is not in this skeleton, and it is not a standing redemption right.

```text
product session
    -> quote (sku, credit atoms, token amount, expiry, opaque ids)
        -> user pays the quoted token amount on Amoy
            -> watcher waits for finality
                -> ledger posts service credits
                    -> product meters usage with consume(usageId)
```

The token contract never sees the sku, the account id, or the credit count. It sees an address, an amount, and a `bytes32`.

## 3. Proposed tokenomics

**Label on every figure in this section:** `UNAPPROVED_DESIGN_PROPOSAL`. Nothing here has been minted. The contracts do not contain these numbers. The cap is an argument to `initialize`, so a test fixture cannot freeze this proposal.

### Naming

| Field | Development placeholder | Where it lives |
| --- | --- | --- |
| Name | `Galion Alpha Placeholder` | `src/tokenomics/placeholders.ts`, passed into `initialize` by tests |
| Symbol | `GLNDEV` | Same. The Solidity source does not contain this symbol. |
| Decimals | 18 | OpenZeppelin ERC-20 default. Not overridden. |

Owners replace the placeholder by passing different initializer arguments. This document does not pick the production name.

### Supply

| Parameter | Proposal |
| --- | --- |
| Maximum whole tokens | 1,000,000,000 |
| Unit | 18 decimal places, so the integer cap would be `1_000_000_000 * 10^18` if an owner later initializes with this proposal |
| Cap rule | `cumulativeMinted` only increases. Burning reduces `totalSupply` and balances. It does not make room to mint again. |
| Who mints | `MINTER_ROLE`, and only through `settleMint` with a unique `settlementId` |
| Public mint | None |

The alpha tests use fixture caps of 1,000 and 1,000,000 whole tokens. Those fixtures are not the proposal.

### Distribution

Shares are basis points of the proposed cap. They describe a future allocation policy. This package does not mint them and does not create the holders.

| Bucket | Share | Whole tokens at the proposed cap | Release proposal |
| --- | ---: | ---: | --- |
| Protocol reserve | 20% | 200,000,000 | Left unminted until a later owner action. |
| Credit-settlement inventory | 30% | 300,000,000 | Minted only when a service-credit quote is accepted, one `settlementId` per grant. |
| Contributors | 15% | 150,000,000 | 12 month cliff, then linear for 36 months. |
| Ecosystem programs | 15% | 150,000,000 | Released against named milestones. No drip and no yield. |
| Partnerships | 10% | 100,000,000 | 6 month cliff, then linear for 24 months. |
| Community access | 10% | 100,000,000 | Not a source for the Amoy faucet. |

The basis points sum to 10,000 and the whole tokens sum to 1,000,000,000. `src/tokenomics/distribution.ts` checks that. Contributor and partnership schedules are the shape exercised by `GalionVestingAlpha`: nothing before the cliff, then linear until the end. The contract takes the schedule as constructor arguments, so the months above are policy, not bytecode constants.

Unvested tokens are not a promise of employment income, a dividend, or a credit balance.

### Utility

The proposed use of the token is to pay a quoted amount in exchange for a service-credit grant on one of three surfaces: Galion One, Galion Voice, or Galion Research. The grant then pays for metered actions. The existing integer costs in `CREDIT_COSTS` are the starting menu for that meter: one Nexus Lang execution is 1 service-credit atom, a short video is 20, and so on. Mapping the float `user.credits` column onto these atoms is an open decision.

No token-per-credit price is proposed. A fixed ratio in the contract would be read as a peg. The quoter sets `tokenAmount` per quote and can change it for the next quote.

## 4. Alpha wallet and faucet

This is an operating plan for a later testnet exercise. This package does not generate keys, does not store keys, and does not send transactions.

### Wallets

`initialize` requires four distinct addresses:

| Role | What the key can do | What it cannot do |
| --- | --- | --- |
| Default admin | Grant or revoke the default admin role | Mint, pause, upgrade, or grant the operational roles |
| Pauser | Pause and unpause | Mint or upgrade |
| Minter | `settleMint`, and grant or revoke minter | Pause or upgrade |
| Upgrader | Replace the implementation | Mint or pause, until a new implementation says otherwise |

The upgrader is the sensitive key. A new implementation can change the rules. A timelock in front of that key is an open decision and is not deployed here.

Alpha custody is disposable Amoy keys, one per role, kept in the operator's own password manager. They are not production keys, not a shared hot wallet, and not a file in this repository. Production custody (hardware wallet, multisig, timelock) waits for an owner decision. Lost operational keys are not recovered by the admin. Recovery would be a deliberate upgrade, which is itself an owner decision.

### Gas

Amoy gas is testnet POL. An operator who later runs a manual exercise would obtain a small amount from Polygon's public faucet and would fund only the accounts that need to send test transactions. This package does not call a faucet, does not name an RPC URL, and does not hold POL. Mainnet assets are out of scope, and none are configured.

### Faucet limits

`src/faucet/policy.ts` is the limit checker. It returns a decision. It does not sign or broadcast. Proposed limits, labeled `UNAPPROVED_TESTNET_POLICY`:

| Limit | Value |
| --- | --- |
| Chain | 80002 only |
| Window | 24 hours |
| Per address | 1 fresh claim, at most 100 whole placeholder tokens |
| Per IP hash | 3 fresh claims |
| Global | 10,000 whole placeholder tokens per window |
| Replay | The same idempotency key, address, IP hash, and amount is a no-op |
| Conflict | The same idempotency key with different parameters is refused |

The IP input is a 32-byte hex hash. A raw IP string is refused. These drip numbers are not drawn from the 100,000,000 community-access proposal. The Amoy faucet, if an owner later runs one by hand, is a test exercise with testnet tokens.

Abuse response in a future exercise: stop calling the minter, and pause the token if transfers themselves must stop. Both actions are operational. Neither is automated here.

## 5. In-app payment interfaces

The types live in `src/payments/types.ts`. The reference accounting lives in `src/payments/ledger.ts`. Neither module is imported by Galion One, Galion Voice, Galion Research, or Galion OS.

### Session

A product session carries `sessionId`, an internal `accountId`, and a surface (`galion_one`, `galion_voice`, or `galion_research`). A wallet address is an optional payment instrument. It does not identify the account. A Ceramic DID, if one is added later, stays in the off-chain profile. It is not a field on the quote that goes to the chain.

### Quote

The product asks for a sku and a credit count. The quoter returns `quoteId`, `settlementId`, `tokenAmount`, chain id `80002`, and an expiry. The proposed expiry is 10 minutes. The quote is refused when `now >= expiresAt`. An expired quote posts nothing.

### Payment and finality

Two receipt shapes share the same idempotency idea:

| Path | On-chain call | When it fits |
| --- | --- | --- |
| Spend | `GalionQuotePaymentAlpha.payQuote(quoteId, amount)` pulls tokens to a sink | The payer already holds tokens |
| Issuance | `GalionTokenAlpha.settleMint(to, amount, settlementId)` | A testnet drip or a later inventory mint against an accepted quote |

The watcher reads the event. It needs the quote id or settlement id, the account, the amount, the transaction hash, and the log index. Proposed posting rule: `finality` is `finalized` and confirmations are at least 64. Pending and safe confirmations leave the ledger entry reserved and post no credits. Amoy finality is a testnet signal. The number 64 is a proposal, not a production settlement standard.

### Duplicates

- The same `settlementId` with the same recipient and amount does not mint twice.
- The same `quoteId` with the same payer and amount does not pull tokens twice.
- A replay with different parameters reverts on-chain and is a conflict in the ledger.
- `consume(usageId)` debits service credits once. The same usage id does not debit again.

### Failure and refund

| Observation | Ledger result |
| --- | --- |
| Confirmation `failed` or `reorged` before credits post | Reservation becomes `released`. Balance stays zero. |
| Confirmation `failed` or `reorged` after credits posted | No automatic reversal. The entry stays posted for manual review. |
| Delivery fails and the grant is still unused | `refund(settlementId, reasonSlug)` reverses the service credits once. |
| Delivery fails and some credits were already metered | Refund throws. A person reviews it. The ledger does not mint a debt. |

`reasonSlug` is a short code such as `service_unavailable`. The refund reverses service credits. It does not transfer tokens out of the sink.

### Privacy

`assertNoPrivatePayload` rejects prompts, message bodies, emails, names, phone numbers, secrets, API keys, mnemonics, and private keys anywhere in the object graph. The chain events are `SettlementMinted`, `SettlementReplay`, `QuotePaid`, `QuotePaymentReplay`, `Funded`, and `Released`, plus the OpenZeppelin token events. Their fields are addresses, amounts, and ids.

Public IPFS and public OrbitDB are the wrong place for the same objects. The architecture's IPFS path remains a proposal for code and public assets. Encrypting a backup before Filecoin, as that document already requires for sensitive backups, is a storage-team concern and is not built here.

## 6. Contract skeleton

The behavior is specified in [CONTRACT_OUTLINE.md](CONTRACT_OUTLINE.md) and implemented in `contracts/`. Short form:

| Contract | Upgradeable | Role |
| --- | --- | --- |
| `GalionTokenAlpha` | UUPS | Capped ERC-20, pause, role separation, idempotent mint |
| `GalionTokenAlphaV2` | UUPS successor | Version getter only, used to prove a storage-safe upgrade |
| `GalionQuotePaymentAlpha` | No | Opaque quote receipt and token pull |
| `GalionVestingAlpha` | No | Cliff, then linear release |
| `GalionTokenAlphaIncompatible` | No | Fixture that the upgrade checker must reject |

Every state-changing entry point checks chain id `80002`. Native coin sent to these contracts reverts, so testnet POL cannot sit on them.

## 7. Dependencies, audit status, and limits

Pinned for this package:

| Package | Version | Role |
| --- | --- | --- |
| `@openzeppelin/contracts` | 5.6.1 | ERC-20 interface, `SafeERC20`, `ReentrancyGuard`, ERC-1967 proxy used by the test harness |
| `@openzeppelin/contracts-upgradeable` | 5.6.1 | ERC-20, burn, pause, access control, UUPS |
| `@openzeppelin/hardhat-upgrades` | 3.9.1 | Local deploy-to-memory and storage checks |
| `hardhat` | 2.29.1 | Compiler and in-memory chain |
| `@nomicfoundation/hardhat-toolbox` | 5.0.0 | Test runner |

OpenZeppelin publishes an audit for Contracts v5.6.0 (February 2026, OpenZeppelin Security Research). Release 5.6.1 is the 27 February 2026 patch for `InteroperableAddress` parsing. This package does not call `InteroperableAddress`. The library audit does not cover `GalionTokenAlpha`, `GalionQuotePaymentAlpha`, or `GalionVestingAlpha`. Those three are unaudited. They have no formal verification and no external review.

Limits an owner should treat as open before any future testnet use:

- The upgrader can replace the token rules. There is no timelock.
- Self-administered roles can lock a role forever if its last key is lost.
- Upgradeability means holders do not have an immutable rule set.
- Quote payments are not signed. The ledger, not the sink, decides which quote ids grant credits. A payment for an unknown id moves tokens and grants nothing.
- Vesting is non-upgradeable on purpose. A mistake in a funded schedule cannot be patched in place.
- Integer division leaves dust until the end timestamp, when the contract releases the full remainder.
- Tests run in Hardhat's in-memory chain. They do not touch Amoy.

## 8. How to check the skeleton

From `v2/blockchain/galion-coin-alpha`:

```bash
npx hardhat compile
npx hardhat test
npm run test:chain-guard
npm run deploy
```

`npm run deploy` and `npx hardhat deploy` are supposed to exit non-zero. Results from the run that produced this document are in [DECISION_JOURNAL.md](DECISION_JOURNAL.md).

## 9. Owner decisions still open

The journal lists these in one place. The ones that block any later testnet exercise are: token name and symbol, whether the proposed cap and buckets are accepted, the quote price policy, the finality threshold, reconciliation of float and integer credits, break-glass for lost keys, and whether a timelock is required before an upgrader key exists. This package does not make those decisions, and it cannot deploy them.

## Sources

- Polygon Amoy chain id `80002` and POL as the gas token: [Polygon PoS RPC endpoints](https://docs.polygon.technology/pos/reference/rpc-endpoints) (page current as retrieved 7 November 2026).
- OpenZeppelin Contracts audit index, including v5.6.0 in February 2026: [openzeppelin-contracts audits](https://github.com/OpenZeppelin/openzeppelin-contracts-upgradeable/tree/master/audits).
- OpenZeppelin security center, latest listed contracts version 5.6.1 and v5.6.0 audit dated 27 February 2026: [OpenZeppelin Contracts security](https://contracts.openzeppelin.com/security).
- v5.6.1 patch notes, 27 February 2026: [OpenZeppelin Contracts v5.6.1](https://github.com/OpenZeppelin/openzeppelin-contracts/releases/tag/v5.6.1).
- Local architecture and credit meter: `v2/blockchain/docs/ARCHITECTURE.md`, `v2/backend/models/user.py`, `v2/backend/models/billing.py`, `v2/backend/services/subscription_tiers.py`, `v2/frontend/pages/pricing.tsx`.
