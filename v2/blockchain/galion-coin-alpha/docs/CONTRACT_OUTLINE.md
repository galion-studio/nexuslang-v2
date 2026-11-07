# Galion coin alpha — contract outline

**Status:** unaudited skeleton, matching the code under `contracts/`  
**Date:** 7 November 2026  
**Chain:** Polygon Amoy, chain id `80002`, checked on every state-changing path  
**Deployment:** none. The Hardhat config has an in-memory chain only.

Human author of record: Maciej Grajczyk

The design context, tokenomics, faucet, and payment flow are in [DESIGN.md](DESIGN.md). This file is the contract surface a reviewer can check against the Solidity.

## 1. Layout

```text
contracts/
  GalionTokenAlpha.sol                 UUPS ERC-20
  GalionTokenAlphaV2.sol               upgrade fixture, no new state
  GalionTokenAlphaIncompatible.sol     negative upgrade fixture
  GalionQuotePaymentAlpha.sol          non-upgradeable quote sink
  GalionVestingAlpha.sol               non-upgradeable cliff schedule
  interfaces/IGalionTokenAlpha.sol
```

Compiler: Solidity `0.8.28`, optimizer on, 200 runs. OpenZeppelin Contracts and Contracts Upgradeable are pinned at `5.6.1`. The library is audited upstream at the v5.6.0 line. These contracts are not.

Name and symbol are `initialize` arguments. The development placeholder (`Galion Alpha Placeholder` / `GLNDEV`) is not a constant in Solidity.

## 2. GalionTokenAlpha

UUPS proxy. Implementation constructor calls `_disableInitializers()`, so the implementation contract itself cannot be initialized. The proxy calls `initialize` once.

### Roles

| Role | Constant | Admin of the role | Held at init by |
| --- | --- | --- | --- |
| Default admin | `DEFAULT_ADMIN_ROLE` (`0x00`) | itself | `admin` |
| Pauser | `keccak256("PAUSER_ROLE")` | itself | `pauser` |
| Minter | `keccak256("MINTER_ROLE")` | itself | `minter` |
| Upgrader | `keccak256("UPGRADER_ROLE")` | itself | `upgrader` |

The four addresses are non-zero and pairwise distinct. After initialization the default admin cannot grant minter, pauser, or upgrader. Each operational role grants itself.

`_authorizeUpgrade` is `onlyRole(UPGRADER_ROLE)`. A compromised upgrader can still ship a new implementation that ignores this split. That is the UUPS tradeoff, recorded in the journal. There is no timelock.

### Storage

Custom state uses ERC-7201 namespace `galion.alpha.token.v1`.

```text
slot = keccak256(abi.encode(uint256(keccak256("galion.alpha.token.v1")) - 1)) & ~bytes32(uint256(0xff))
     = 0xe91ac59f6a9f943770313967e20a7bee7810ac50a722b06c89ba9c8f50d8c300
```

```solidity
struct SettlementRecord {
    address account;
    uint256 amount;
    bool used;
}

struct GalionTokenStorage {
    uint256 cap;
    uint256 cumulativeMinted;
    uint64 allowedChainId;
    mapping(bytes32 settlementId => SettlementRecord) settlements;
}
```

OpenZeppelin ERC-20, pausable, and access-control state stay in their own namespaces. `GalionTokenAlphaV2` adds a pure `contractVersion()` and no variables. A later field goes at the end of `GalionTokenStorage`. A linear variable added beside the namespace is the wrong place for new alpha state.

`allowedChainId` is set to `80002` during `initialize` and is checked again on later calls together with `block.chainid`.

### Functions

| Function | Access | Effect |
| --- | --- | --- |
| `initialize(name, symbol, cap, admin, pauser, minter, upgrader)` | once | Checks chain, name length 1–64, symbol length 1–11, non-zero cap, distinct roles. Sets cap and chain. Grants roles. |
| `settleMint(to, amount, settlementId)` | minter | Mints `amount` inside the cumulative cap and records the id. Same id, same `to`, same `amount`: returns `false`, emits `SettlementReplay`, mints nothing. Same id with any other pair: `SettlementConflict`. |
| `pause` / `unpause` | pauser | Blocks mint, transfer, and burn through ERC-20 `_update`. |
| `burn(value)` | token holder | Inherited. Reduces `totalSupply` only. `cumulativeMinted` stays. |
| `grantRole` / `revokeRole` / `renounceRole` | role admin | Chain check, then OpenZeppelin rules. |
| `upgradeToAndCall` | upgrader, via proxy | UUPS. Authorization is `_authorizeUpgrade`. |
| `cap`, `cumulativeMinted`, `remainingMintable`, `allowedChainId`, `getSettlement` | anyone | Views. Intentionally readable so a fork can be inspected. They do not move tokens. |
| `receive` | anyone | Reverts `NativeCoinNotAccepted`. |

There is no open `mint` without a settlement id. A retried issuance uses the same id and does not double-mint.

### Errors

`UnsupportedChain`, `ZeroAddress`, `ZeroAmount`, `InvalidName`, `InvalidSymbol`, `CapZero`, `RolesMustBeDistinct`, `CapExceeded(cap, attemptedCumulative)`, `EmptySettlementId`, `SettlementConflict`, `NativeCoinNotAccepted`, plus OpenZeppelin `InvalidInitialization`, `AccessControlUnauthorizedAccount`, `EnforcedPause`, and the ERC-20 balance errors.

### Events

`SettlementMinted(settlementId, account, amount)` and `SettlementReplay(settlementId, account, amount)`. Standard ERC-20 `Transfer` events come from mint, burn, and transfer. No string payload is emitted beyond the token name and symbol stored by ERC-20 at initialization.

### Invariants

1. `block.chainid == 80002` and `allowedChainId == 80002` before any balance change, role change, pause change, or upgrade authorization.
2. `cumulativeMinted <= cap`.
3. `cumulativeMinted` is unchanged by burn and by transfer.
4. A `settlementId` is unused, or it is bound to exactly one `(account, amount)`.
5. The second successful call with that same triple does not change `totalSupply`.
6. While paused, `_update` reverts, so mint, burn, and transfer revert. A reverted mint does not consume the settlement id.
7. The implementation contract's initializer stays disabled.

### Upgrade

Tests call `upgrades.validateUpgrade` for `GalionTokenAlphaV2` (accepted) and `GalionTokenAlphaIncompatible` (rejected), then `upgradeProxy` with the upgrader signer. Balances, cap, cumulative minted, pause flag, name, and the settlement record survive. The default admin's upgrade attempt reverts `AccessControlUnauthorizedAccount`.

## 3. GalionQuotePaymentAlpha

Not upgradeable. Constructor stores the token and the sink, and reverts unless `block.chainid` is `80002`.

```text
payQuote(quoteId, amount) -> bool recordedFresh
```

| Condition | Result |
| --- | --- |
| First call for `quoteId` | Records payer and amount, then `transferFrom` the payer to the sink. Returns `true`. Emits `QuotePaid`. |
| Same payer and amount | Returns `false`. Emits `QuotePaymentReplay`. Does not pull tokens. |
| Different payer or amount | `QuoteConflict`. |
| Empty id or zero amount | Revert. |
| Token is paused | `transferFrom` reverts and the recording is rolled back. `paymentOf` stays empty. |

State is written before the token transfer, and the function is `nonReentrant`. A reverting transfer rolls the record back with the transaction. The contract does not know which quotes the ledger considers real. Unknown ids can still move tokens if a payer calls it; the off-chain ledger is what posts credits.

`paymentOf(quoteId)` returns `(payer, amount, recorded)`.

## 4. GalionVestingAlpha

Not upgradeable, so a funded cliff cannot be shortened by an upgrade. Constructor arguments are the token, the beneficiary, the total, the start timestamp, the cliff duration, and the vest duration. Vest duration must be non-zero. Chain id must be `80002`.

```text
cliffEnd = start + cliffDuration
end      = cliffEnd + vestDuration
```

| Time | Vested amount, once funded |
| --- | --- |
| Before `cliffEnd` | 0 |
| From `cliffEnd` to `end` | `total * (timestamp - cliffEnd) / (end - cliffEnd)` |
| At and after `end` | `total` |

`fund()` pulls `total` from the caller once. `release()` sends `releasable()` to the beneficiary. A call that is owed nothing returns 0 and emits nothing, including a second call after the schedule is fully released. Anyone may call `release`; tokens always go to the beneficiary.

This schedule is the mechanism behind the contributor and partnership proposals in the design. The month counts are not stored here. Callers pass durations. The contract does not revoke, and it does not pay yield.

## 5. Test map

| Concern | Test |
| --- | --- |
| Access split, role admin, second initialize, disabled implementation initializer | `test/GalionTokenAlpha.ts` |
| Cap, burn does not reopen cap, reverted mint leaves the id free | same |
| Settlement replay and conflict | same |
| Pause blocks transfer, burn, and mint; unpause restores transfer | same |
| Upgrade success, admin upgrade failure, incompatible layout rejected, state kept | same |
| Native coin rejected | same |
| Quote pay, replay, conflict, paused pay leaves no record | `test/GalionQuotePaymentAlpha.ts` |
| Cliff, linear release, full release, second release is a no-op, double fund refused | `test/GalionVestingAlpha.ts` |
| Initialize, quote sink, and vesting revert on chain id 31337 | `test/ChainGuard.ts` (separate Hardhat process) |
| Distribution sums, faucet limits, ledger finality, usage, refund, privacy | `test/policy.ts` |

Chain id `31337` exists only as that negative in-memory fixture. It is not a deployment network. Chain id `137` appears in one ledger assertion that expects rejection. It is not a Hardhat network.

## 6. Known limits of this outline

- No EIP-712 quote signature. Adding one is an owner decision.
- No token-out refund function. Credit reversal is off-chain, in `ServiceCreditLedger`.
- No permit (EIP-2612) and no votes. Those would be new surface.
- Views stay available on a wrong chain so an operator can see why calls revert.
- The sink address can be any non-zero address, including a contract with its own behavior. Alpha tests use an EOA.
