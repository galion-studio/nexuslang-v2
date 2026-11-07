import { expect } from "chai";
import { ethers } from "hardhat";
import { time } from "@nomicfoundation/hardhat-network-helpers";
import { deployAlpha, settlementId, WHOLE } from "./helpers";

describe("GalionVestingAlpha", function () {
  before(async function () {
    const net = await ethers.provider.getNetwork();
    if (net.chainId !== 80002n) this.skip();
  });

  it("releases nothing during the cliff, then linearly, and a second call is a no-op", async function () {
    const { token, minter, alice, beneficiary } = await deployAlpha();
    const total = 1_000n * WHOLE;
    const cliff = 1_000;
    const vest = 1_000;
    const start = (await time.latest()) + 10;
    await token.connect(minter).settleMint(alice.address, total, settlementId("vest-fund"));

    const vestingFactory = await ethers.getContractFactory("GalionVestingAlpha");
    const vesting = await vestingFactory.deploy(
      await token.getAddress(),
      beneficiary.address,
      total,
      start,
      cliff,
      vest
    );
    await vesting.waitForDeployment();
    await token.connect(alice).approve(await vesting.getAddress(), total);
    await vesting.connect(alice).fund();

    const cliffEnd = BigInt(start + cliff);
    await time.increaseTo(cliffEnd - 5n);
    expect(await vesting.releasable()).to.equal(0n);
    await expect(vesting.release()).to.not.emit(vesting, "Released");
    expect(await token.balanceOf(beneficiary.address)).to.equal(0n);

    const halfwayAt = cliffEnd + BigInt(vest) / 2n;
    const expectedHalf = (total * (halfwayAt - cliffEnd)) / BigInt(vest);
    await time.setNextBlockTimestamp(halfwayAt);
    await expect(vesting.release()).to.emit(vesting, "Released").withArgs(beneficiary.address, expectedHalf);
    expect(await token.balanceOf(beneficiary.address)).to.equal(expectedHalf);

    const end = cliffEnd + BigInt(vest);
    await time.setNextBlockTimestamp(end);
    await expect(vesting.release()).to.emit(vesting, "Released");
    expect(await token.balanceOf(beneficiary.address)).to.equal(total);
    expect(await vesting.released()).to.equal(total);
    expect(await vesting.release.staticCall()).to.equal(0n);
    await expect(vesting.release()).to.not.emit(vesting, "Released");
    expect(await token.balanceOf(beneficiary.address)).to.equal(total);
  });

  it("refuses a second funding and a zero-length vest", async function () {
    const { token, minter, alice, beneficiary } = await deployAlpha();
    const total = 10n * WHOLE;
    await token.connect(minter).settleMint(alice.address, total, settlementId("vest-twice"));
    const start = (await time.latest()) + 5;
    const vesting = await (await ethers.getContractFactory("GalionVestingAlpha")).deploy(
      await token.getAddress(),
      beneficiary.address,
      total,
      start,
      0,
      100
    );
    await token.connect(alice).approve(await vesting.getAddress(), total * 2n);
    await vesting.connect(alice).fund();
    await expect(vesting.connect(alice).fund()).to.be.revertedWithCustomError(vesting, "AlreadyFunded");

    const latest = await time.latest();
    await expect((await ethers.getContractFactory("GalionVestingAlpha")).deploy(
      await token.getAddress(),
      beneficiary.address,
      total,
      latest,
      10,
      0
    )).to.be.revertedWithCustomError(vesting, "InvalidSchedule");
  });
});
