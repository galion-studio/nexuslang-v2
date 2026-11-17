import { expect } from "chai";
import { readFileSync } from "fs";
import { ethers, upgrades } from "hardhat";
import { DEV_TOKEN_PLACEHOLDER } from "../src/tokenomics/placeholders";
import { deployAlpha, settlementId, WHOLE } from "./helpers";

describe("GalionTokenAlpha", function () {
  before(async function () {
    const net = await ethers.provider.getNetwork();
    if (net.chainId !== 80002n) this.skip();
  });

  it("initializes the placeholder name, separated roles, and a closed cap", async function () {
    const { token, admin, pauser, minter, upgrader, cap } = await deployAlpha(1_000n);
    expect(await token.name()).to.equal(DEV_TOKEN_PLACEHOLDER.name);
    expect(await token.symbol()).to.equal(DEV_TOKEN_PLACEHOLDER.symbol);
    expect(await token.decimals()).to.equal(18);
    expect(await token.cap()).to.equal(cap);
    expect(await token.cumulativeMinted()).to.equal(0n);
    expect(await token.remainingMintable()).to.equal(cap);
    expect(await token.allowedChainId()).to.equal(80002n);
    expect(await token.hasRole(await token.DEFAULT_ADMIN_ROLE(), admin.address)).to.equal(true);
    expect(await token.hasRole(await token.MINTER_ROLE(), minter.address)).to.equal(true);
    expect(await token.getRoleAdmin(await token.MINTER_ROLE())).to.equal(await token.MINTER_ROLE());
    expect(await token.getRoleAdmin(await token.PAUSER_ROLE())).to.equal(await token.PAUSER_ROLE());
    expect(await token.getRoleAdmin(await token.UPGRADER_ROLE())).to.equal(await token.UPGRADER_ROLE());
    expect(await token.hasRole(await token.PAUSER_ROLE(), pauser.address)).to.equal(true);
    expect(await token.hasRole(await token.UPGRADER_ROLE(), upgrader.address)).to.equal(true);

    await expect(token.initialize(
      DEV_TOKEN_PLACEHOLDER.name,
      DEV_TOKEN_PLACEHOLDER.symbol,
      cap,
      admin.address,
      pauser.address,
      minter.address,
      upgrader.address
    )).to.be.revertedWithCustomError(token, "InvalidInitialization");
  });

  it("does not hardcode the placeholder name and disables the implementation initializer", async function () {
    const source = readFileSync("contracts/GalionTokenAlpha.sol", "utf8");
    expect(source.includes(DEV_TOKEN_PLACEHOLDER.symbol)).to.equal(false);
    expect(source.includes(DEV_TOKEN_PLACEHOLDER.name)).to.equal(false);

    const { token, admin, pauser, minter, upgrader, cap } = await deployAlpha();
    const implementation = await upgrades.erc1967.getImplementationAddress(await token.getAddress());
    const bare = await ethers.getContractAt("GalionTokenAlpha", implementation);
    await expect(bare.initialize(
      DEV_TOKEN_PLACEHOLDER.name,
      DEV_TOKEN_PLACEHOLDER.symbol,
      cap,
      admin.address,
      pauser.address,
      minter.address,
      upgrader.address
    )).to.be.revertedWithCustomError(bare, "InvalidInitialization");
  });

  it("rejects a zero cap, a blank name, and collapsed roles", async function () {
    const [admin, pauser, minter, upgrader] = await ethers.getSigners();
    const factory = await ethers.getContractFactory("GalionTokenAlpha");
    const args = [
      DEV_TOKEN_PLACEHOLDER.name,
      DEV_TOKEN_PLACEHOLDER.symbol,
      0n,
      admin.address,
      pauser.address,
      minter.address,
      upgrader.address,
    ];
    await expect(upgrades.deployProxy(factory, args, { initializer: "initialize", kind: "uups" }))
      .to.be.revertedWithCustomError(factory, "CapZero");

    await expect(upgrades.deployProxy(
      factory,
      ["", DEV_TOKEN_PLACEHOLDER.symbol, WHOLE, admin.address, pauser.address, minter.address, upgrader.address],
      { initializer: "initialize", kind: "uups" }
    )).to.be.revertedWithCustomError(factory, "InvalidName");

    await expect(upgrades.deployProxy(
      factory,
      [DEV_TOKEN_PLACEHOLDER.name, DEV_TOKEN_PLACEHOLDER.symbol, WHOLE, admin.address, admin.address, minter.address, upgrader.address],
      { initializer: "initialize", kind: "uups" }
    )).to.be.revertedWithCustomError(factory, "RolesMustBeDistinct");
  });

  it("separates mint, pause, and upgrade from the default admin", async function () {
    const { token, admin, minter, alice } = await deployAlpha();
    const id = settlementId("access-1");
    await expect(token.connect(admin).settleMint(alice.address, WHOLE, id))
      .to.be.revertedWithCustomError(token, "AccessControlUnauthorizedAccount")
      .withArgs(admin.address, await token.MINTER_ROLE());
    await expect(token.connect(admin).pause())
      .to.be.revertedWithCustomError(token, "AccessControlUnauthorizedAccount")
      .withArgs(admin.address, await token.PAUSER_ROLE());
    await expect(token.connect(admin).grantRole(await token.MINTER_ROLE(), admin.address))
      .to.be.revertedWithCustomError(token, "AccessControlUnauthorizedAccount")
      .withArgs(admin.address, await token.MINTER_ROLE());

    await expect(token.connect(minter).settleMint(alice.address, WHOLE, id))
      .to.emit(token, "SettlementMinted")
      .withArgs(id, alice.address, WHOLE);
    expect(await token.balanceOf(alice.address)).to.equal(WHOLE);

    await token.connect(minter).grantRole(await token.MINTER_ROLE(), alice.address);
    expect(await token.hasRole(await token.MINTER_ROLE(), alice.address)).to.equal(true);
  });

  it("enforces the cumulative cap and does not reopen it on burn", async function () {
    const { token, minter, alice, cap } = await deployAlpha(1_000n);
    const first = settlementId("cap-1");
    const second = settlementId("cap-2");
    const third = settlementId("cap-3");
    await token.connect(minter).settleMint(alice.address, cap - WHOLE, first);
    await token.connect(minter).settleMint(alice.address, WHOLE, second);
    expect(await token.totalSupply()).to.equal(cap);
    expect(await token.remainingMintable()).to.equal(0n);

    await expect(token.connect(minter).settleMint(alice.address, 1n, third))
      .to.be.revertedWithCustomError(token, "CapExceeded")
      .withArgs(cap, cap + 1n);
    expect(await token.getSettlement(third)).to.deep.equal([ethers.ZeroAddress, 0n, false]);

    await token.connect(alice).burn(WHOLE);
    expect(await token.totalSupply()).to.equal(cap - WHOLE);
    expect(await token.cumulativeMinted()).to.equal(cap);
    expect(await token.remainingMintable()).to.equal(0n);
    await expect(token.connect(minter).settleMint(alice.address, 1n, third))
      .to.be.revertedWithCustomError(token, "CapExceeded");
  });

  it("treats an identical settlement replay as a no-op and rejects a conflicting one", async function () {
    const { token, minter, alice, bob } = await deployAlpha();
    const id = settlementId("replay-1");
    const first = await token.connect(minter).settleMint(alice.address, 5n * WHOLE, id);
    await expect(first).to.emit(token, "SettlementMinted");
    expect(await first).to.not.equal(undefined);

    const replay = await token.connect(minter).settleMint(alice.address, 5n * WHOLE, id);
    await expect(replay).to.emit(token, "SettlementReplay").withArgs(id, alice.address, 5n * WHOLE);
    expect(await token.balanceOf(alice.address)).to.equal(5n * WHOLE);
    expect(await token.cumulativeMinted()).to.equal(5n * WHOLE);
    expect(await token.getSettlement(id)).to.deep.equal([alice.address, 5n * WHOLE, true]);

    await expect(token.connect(minter).settleMint(alice.address, 6n * WHOLE, id))
      .to.be.revertedWithCustomError(token, "SettlementConflict")
      .withArgs(id);
    await expect(token.connect(minter).settleMint(bob.address, 5n * WHOLE, id))
      .to.be.revertedWithCustomError(token, "SettlementConflict")
      .withArgs(id);
    expect(await token.cumulativeMinted()).to.equal(5n * WHOLE);

    const failedId = settlementId("replay-reverted");
    await expect(token.connect(minter).settleMint(alice.address, 0n, failedId))
      .to.be.revertedWithCustomError(token, "ZeroAmount");
    await token.connect(minter).settleMint(alice.address, WHOLE, failedId);
    expect(await token.balanceOf(alice.address)).to.equal(6n * WHOLE);

    await expect(token.connect(minter).settleMint(alice.address, WHOLE, ethers.ZeroHash))
      .to.be.revertedWithCustomError(token, "EmptySettlementId");
  });

  it("pauses transfers, mints, and burns until the pauser unpauses", async function () {
    const { token, pauser, minter, alice, bob } = await deployAlpha();
    const id = settlementId("pause-1");
    await token.connect(minter).settleMint(alice.address, 10n * WHOLE, id);
    await token.connect(pauser).pause();
    expect(await token.paused()).to.equal(true);

    await expect(token.connect(alice).transfer(bob.address, WHOLE))
      .to.be.revertedWithCustomError(token, "EnforcedPause");
    await expect(token.connect(alice).burn(WHOLE))
      .to.be.revertedWithCustomError(token, "EnforcedPause");
    await expect(token.connect(minter).settleMint(bob.address, WHOLE, settlementId("pause-2")))
      .to.be.revertedWithCustomError(token, "EnforcedPause");
    expect(await token.cumulativeMinted()).to.equal(10n * WHOLE);

    await expect(token.connect(minter).unpause())
      .to.be.revertedWithCustomError(token, "AccessControlUnauthorizedAccount");
    await token.connect(pauser).unpause();
    await token.connect(alice).transfer(bob.address, WHOLE);
    expect(await token.balanceOf(bob.address)).to.equal(WHOLE);
  });

  it("lets only the upgrader move to V2 and keeps supply, pause, and settlements", async function () {
    const { token, admin, pauser, upgrader, minter, alice } = await deployAlpha(1_000n);
    const id = settlementId("upgrade-1");
    await token.connect(minter).settleMint(alice.address, 25n * WHOLE, id);
    await token.connect(pauser).pause();

    const incompatible = await ethers.getContractFactory("GalionTokenAlphaIncompatible");
    await expect(
      upgrades.validateUpgrade(await token.getAddress(), incompatible, { kind: "uups" })
    ).to.be.rejected;

    const asAdmin = await ethers.getContractFactory("GalionTokenAlphaV2", admin);
    await expect(upgrades.upgradeProxy(await token.getAddress(), asAdmin, { kind: "uups" }))
      .to.be.revertedWithCustomError(token, "AccessControlUnauthorizedAccount")
      .withArgs(admin.address, await token.UPGRADER_ROLE());
    expect(await token.balanceOf(alice.address)).to.equal(25n * WHOLE);

    const asUpgrader = await ethers.getContractFactory("GalionTokenAlphaV2", upgrader);
    await upgrades.validateUpgrade(await token.getAddress(), asUpgrader, { kind: "uups" });
    const upgraded = await upgrades.upgradeProxy(await token.getAddress(), asUpgrader, { kind: "uups" });
    expect(await upgraded.contractVersion()).to.equal(2n);
    expect(await upgraded.balanceOf(alice.address)).to.equal(25n * WHOLE);
    expect(await upgraded.cumulativeMinted()).to.equal(25n * WHOLE);
    expect(await upgraded.cap()).to.equal(1_000n * WHOLE);
    expect(await upgraded.paused()).to.equal(true);
    expect(await upgraded.getSettlement(id)).to.deep.equal([alice.address, 25n * WHOLE, true]);
    expect(await upgraded.name()).to.equal(DEV_TOKEN_PLACEHOLDER.name);

    await expect(upgraded.connect(alice).transfer(upgrader.address, 1n))
      .to.be.revertedWithCustomError(upgraded, "EnforcedPause");
    await upgraded.connect(pauser).unpause();
    const replay = await upgraded.connect(minter).settleMint(alice.address, 25n * WHOLE, id);
    await expect(replay).to.emit(upgraded, "SettlementReplay");
    expect(await upgraded.cumulativeMinted()).to.equal(25n * WHOLE);
  });

  it("rejects native coin", async function () {
    const { token, alice } = await deployAlpha();
    await expect(alice.sendTransaction({ to: await token.getAddress(), value: 1n }))
      .to.be.revertedWithCustomError(token, "NativeCoinNotAccepted");
  });
});
