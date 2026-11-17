# Galion coin alpha

Unaudited design and local skeleton for a Polygon Amoy (chain id `80002`) token experiment.

This directory is the whole change. It does not deploy, it does not contain a mainnet network, and it does not choose the token's name. `GLNDEV` / `Galion Alpha Placeholder` is a development placeholder passed into `initialize` by the tests.

| Document | Contents |
| --- | --- |
| [docs/DESIGN.md](docs/DESIGN.md) | Architecture findings, proposed tokenomics, faucet plan, payment interfaces |
| [docs/CONTRACT_OUTLINE.md](docs/CONTRACT_OUTLINE.md) | Contract surface, storage, invariants, test map |
| [docs/DECISION_JOURNAL.md](docs/DECISION_JOURNAL.md) | Decisions, assumptions, test log, open approvals |

## Check locally

```bash
cd v2/blockchain/galion-coin-alpha
npm ci
npx hardhat compile
npx hardhat test
npm run test:chain-guard
```

`npm run deploy` and `npx hardhat deploy` are wired to fail. That is intentional.

Human author of record for the design documents: Maciej Grajczyk
