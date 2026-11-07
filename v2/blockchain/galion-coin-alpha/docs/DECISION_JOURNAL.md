# Galion coin alpha — decision journal

**Date of this entry:** 7 November 2026  
**Branch intent:** isolated design and skeleton. No merge, no deployment.

Human author of record: Maciej Grajczyk

Entries are decisions taken while scaffolding, assumptions those decisions rest on, and approvals that still belong to an owner. "Taken" means taken inside this design package. It does not mean an owner has approved the token.

## D1. Isolate the work under `v2/blockchain/galion-coin-alpha`

**Taken:** All new files live in that directory. `v2/blockchain/docs/ARCHITECTURE.md` is unchanged. Nexus Lang backend, frontend, Galion OS, Galion Voice, and Samantha trees are unchanged.

**Assumption:** The architecture document is the Nexus Lang V2 blockchain plan the user named, and the credit meter in `v2/backend` is the implemented accounting this token would eventually sit beside.

**Still needs an owner:** Whether Galion OS credits and the Nexus Lang credit columns are the same product meter or two meters that only share a name.

## D2. Treat the architecture snippets as proposals

**Taken:** IPFS, Filecoin, Ceramic, OrbitDB, Akash, and zkSync stay documented integrations. They are not code in this branch. The on-chain `UserRegistry` credit balance and the native-coin `buyCredits` / `subscribe` sketches are not implemented.

**Assumption:** Those snippets were never compiled. A search of the tree before this branch found no Solidity and no IPFS, Ceramic, or OrbitDB client.

**Why:** Publishing a DID and a credit balance on a public chain fights the architecture document's own rule against personal data on a public chain.

## D3. Polygon Amoy only, and no broadcast

**Taken:** Contracts revert unless `block.chainid` is `80002`. Hardhat's in-memory chain uses `80002` for acceptance tests. `GALION_TEST_CHAIN_ID=31337` is accepted only by the local config, for the negative test, and it has no RPC and no accounts list. `npm run deploy` and the Hardhat `deploy` task exit with an error. There is no deploy script and no private key.

**Assumption:** Polygon PoS public testnet remains Amoy, chain id `80002`, gas token POL, as described by Polygon's RPC endpoint documentation on the day of this entry. See the sources in `DESIGN.md`.

**Still needs an owner:** Reconfirm that chain id immediately before any future deployment. This package cannot perform that deployment.

## D4. Placeholder name, parameterised cap

**Taken:** Tests pass `Galion Alpha Placeholder` and `GLNDEV` into `initialize`. Those strings are not Solidity constants. The proposed cap of 1,000,000,000 whole tokens lives in `src/tokenomics/placeholders.ts` and is not an initializer default.

**Assumption:** The product name is undecided, and a hardcoded cap would turn an unapproved figure into bytecode the moment anyone initialized a proxy.

**Still needs an owner:** Final name, symbol, and whether 1,000,000,000 with the published bucket split is the cap at all.

## D5. Cumulative cap

**Taken:** Burns do not restore minting room. `cumulativeMinted` is the cap meter. `totalSupply` is the circulation meter.

**Assumption:** A cap that refills on burn is easy to mistake for a hard maximum. The proposal is a maximum issuance.

**Still needs an owner:** Confirm cumulative issuance, rather than a circulating cap, before any mint policy is approved.

## D6. Self-administered operational roles

**Taken:** Minter, pauser, and upgrader administer themselves. The default admin cannot mint, pause, upgrade, or grant those roles. Initialization rejects duplicate role addresses.

**Assumption:** Separating the keys is more useful in an alpha than a single owner who can do everything, provided the lockout risk is written down.

**Tradeoff:** A lost minter key stops issuance. A lost upgrader key stops upgrades. The admin cannot repair either. Repair would be a new implementation, which only the upgrader can install. There is no break-glass guardian.

**Still needs an owner:** Accept the lockout, or specify a guardian or timelock before any key is created. The timelock is not in this skeleton.

## D7. UUPS for the token, immutable vesting and quote sink

**Taken:** The token is UUPS because the requested skeleton is upgradeable and the storage layout has to be testable. Vesting is not upgradeable, so a funded cliff stays put. The quote sink is not upgradeable, so its record format stays put.

**Assumption:** Upgradeability of the token is a review tool and a way to fix an unaudited alpha. It is also the largest trust assumption in the token, because the upgrader can change behavior.

**Still needs an owner:** Whether an alpha token should be upgradeable at all once it leaves a local Hardhat process. This package never leaves that process.

## D8. Idempotent settlement ids instead of an open mint

**Taken:** The only mint function is `settleMint`. An identical replay returns false and emits `SettlementReplay`. A conflicting replay reverts. A reverted mint does not consume the id. `payQuote` follows the same pattern. The off-chain ledger treats the same quote and the same usage id as no-ops.

**Assumption:** Duplicate prevention matters more at the logical id than at the raw transaction hash, because an operator retry often builds a new transaction.

## D9. Service credits stay off-chain and integer

**Taken:** The reference ledger posts integer credit atoms after finality, meters them with `consume`, and refunds an unused grant once. It does not move tokens back. It refuses prompts and personal data. Proposed finality is 64 confirmations plus status `finalized`.

**Assumption:** The integer `CREDIT_COSTS` table is the right grain for atoms. The float `user.credits` column is an existing inconsistency to leave untouched.

**Still needs an owner:** Atom size, the 64-confirmation rule, quote expiry (proposed at 10 minutes in the design, enforced only as `expiresAt` on the quote object), and whether a failed delivery ever returns tokens from the sink. Token return is not implemented and is not a holder right in this design.

## D10. No token-to-credit price in the contract

**Taken:** The contract has no oracle and no ratio. Distribution percentages are a TypeScript proposal. The faucet's 100 / 10,000 whole-token drip is a separate testnet policy and is not funded from the community-access bucket.

**Assumption:** Publishing a ratio would be read as a peg or a redemption rate. The user asked to avoid promises of returns or redemption rights.

**Still needs an owner:** The commercial rule the quoter will use when it fills `tokenAmount`. No sample rate is proposed.

## D11. Faucet is a pure policy

**Taken:** `evaluateFaucetClaim` enforces chain, size, per-address, per-IP-hash, global window, and idempotency. It stores no raw IP and holds no key. No wallet is generated in the repo.

**Assumption:** A broadcast script would be the start of a live testnet exercise. The user forbade that.

**Still needs an owner:** Whether a manual Amoy drip is ever run, who holds the minter key, and the drip sizes.

## D12. Pin OpenZeppelin 5.6.1 and say the composition is unaudited

**Taken:** `@openzeppelin/contracts` and `@openzeppelin/contracts-upgradeable` are exact version `5.6.1`. Dev tooling is Hardhat `2.29.1`, toolbox `5.0.0`, upgrades plugin `3.9.1`.

**Assumption:** v5.6.0 is the audited release (February 2026, OpenZeppelin Security Research). v5.6.1 is the 27 February 2026 `InteroperableAddress` parsing patch. This package does not use that type. The audit does not extend to Galion contracts composed on top.

**Still needs an owner:** An independent audit before any network use, including a public testnet.

## D13. What was run

Commands from `v2/blockchain/galion-coin-alpha` on 7 November 2026, Node v22.23.4. No network broadcast.

| Command | Result |
| --- | --- |
| `npx hardhat compile` | First run downloaded solc `0.8.28` and compiled 35 Solidity files, evm target `paris`, and generated 116 typings. A later run reported nothing to compile. |
| `npx hardhat test` | 21 passing, 2 pending. The pending tests are the chain guard, skipped because the in-memory chain is `80002`. Final local run: about 1s. |
| `npm run test:chain-guard` (`GALION_TEST_CHAIN_ID=31337 hardhat test test/ChainGuard.ts`) | 2 passing. Final local run: about 532 ms. |
| `npm run deploy` | Exit 1. Printed `Deployment is disabled. This package must not send testnet or mainnet transactions.` |
| `npx hardhat deploy` | Exit 1. Printed `Deployment is disabled. Refusing to broadcast to any network, including Polygon Amoy.` |

The first compile warned that `_authorizeUpgrade` could be `view`. That mutability was tightened and the following compile was clean.

## Open owner approvals

1. Token name and symbol. Placeholder is `GLNDEV` / `Galion Alpha Placeholder` only.
2. Proposed cap of 1,000,000,000 and the six-bucket split.
3. Cumulative cap rather than a circulating cap.
4. Cliff schedules: contributors 12 months then 36; partnerships 6 months then 24.
5. Quote pricing policy. No rate is proposed.
6. Finality threshold of 64 confirmations, and the 10 minute quote expiry.
7. Integer credit atoms versus the existing float credit column, and whether Galion OS uses this same meter.
8. Faucet sizes and whether a manual Amoy drip should ever happen.
9. Key ceremony, custody, and break-glass for lost minter or upgrader keys.
10. Timelock or a non-upgradeable token before any key exists outside a local test.
11. Whether quote ids should be EIP-712 signed by a quoter.
12. Whether a failed delivery may return tokens from the sink. The ledger refund does not.
13. Independent audit scope before any deployment. Deployment remains disabled until that is a separate, explicit decision.
14. Reconfirmation of Amoy chain id `80002` at that future time.

## What this journal does not decide

It does not authorize a deployment, a listing, a sale, or a redemption. It does not speak for Galion OS, Galion Voice, or Samantha. It does not change their systems.
