import { expect } from "chai";
import { ethers, upgrades } from "hardhat";
import { DEV_TOKEN_PLACEHOLDER } from "../src/tokenomics/placeholders";
import { WHOLE } from "./helpers";

describe("chain guard", function () {
  before(async function () {
    const net = await ethers.provider.getNetwork();
    if (net.chainId !== 31337n) this.skip();
  });

  it("refuses to initialize the token outside Polygon Amoy", async function () {
    const [admin, pauser, minter, upgrader] = await ethers.getSigners();
    const factory = await ethers.getContractFactory("GalionTokenAlpha");
    await expect(upgrades.deployProxy(
      factory,
      [
        DEV_TOKEN_PLACEHOLDER.name,
        DEV_TOKEN_PLACEHOLDER.symbol,
        1_000n * WHOLE,
        admin.address,
        pauser.address,
        minter.address,
        upgrader.address,
      ],
      { initializer: "initialize", kind: "uups" }
    )).to.be.revertedWithCustomError(factory, "UnsupportedChain").withArgs(31337n);
  });

  it("refuses the quote sink and the vesting schedule outside Polygon Amoy", async function () {
    const [admin, beneficiary] = await ethers.getSigners();
    const token = ethers.Wallet.createRandom().address;
    const payments = await ethers.getContractFactory("GalionQuotePaymentAlpha");
    await expect(payments.deploy(token, admin.address))
      .to.be.revertedWithCustomError(payments, "UnsupportedChain")
      .withArgs(31337n);

    const vesting = await ethers.getContractFactory("GalionVestingAlpha");
    await expect(vesting.deploy(token, beneficiary.address, WHOLE, 1, 1, 10))
      .to.be.revertedWithCustomError(vesting, "UnsupportedChain")
      .withArgs(31337n);
  });
});
