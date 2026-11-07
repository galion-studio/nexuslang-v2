import { ethers, upgrades } from "hardhat";
import { DEV_TOKEN_PLACEHOLDER } from "../src/tokenomics/placeholders";

export const WHOLE = 10n ** 18n;

export async function deployAlpha(capWhole = 1_000_000n) {
  const signers = await ethers.getSigners();
  const [admin, pauser, minter, upgrader, alice, bob, sink, beneficiary] = signers;
  const cap = capWhole * WHOLE;
  const factory = await ethers.getContractFactory("GalionTokenAlpha");
  const token = await upgrades.deployProxy(
    factory,
    [
      DEV_TOKEN_PLACEHOLDER.name,
      DEV_TOKEN_PLACEHOLDER.symbol,
      cap,
      admin.address,
      pauser.address,
      minter.address,
      upgrader.address,
    ],
    { initializer: "initialize", kind: "uups" }
  );
  await token.waitForDeployment();
  return { token, admin, pauser, minter, upgrader, alice, bob, sink, beneficiary, cap, factory };
}

export function settlementId(label: string): string {
  return ethers.id(label);
}
