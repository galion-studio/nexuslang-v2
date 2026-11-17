import { expect } from "chai";
import { ethers } from "hardhat";
import { deployAlpha, settlementId, WHOLE } from "./helpers";

describe("GalionQuotePaymentAlpha", function () {
  before(async function () {
    const net = await ethers.provider.getNetwork();
    if (net.chainId !== 80002n) this.skip();
  });

  async function fixture() {
    const deployed = await deployAlpha();
    const { token, minter, alice, bob, sink } = deployed;
    const paymentsFactory = await ethers.getContractFactory("GalionQuotePaymentAlpha");
    const payments = await paymentsFactory.deploy(await token.getAddress(), sink.address);
    await payments.waitForDeployment();
    const amount = 7n * WHOLE;
    await token.connect(minter).settleMint(alice.address, amount, settlementId("quote-fund"));
    await token.connect(alice).approve(await payments.getAddress(), amount);
    return { ...deployed, payments, amount };
  }

  it("pulls tokens once for an opaque quote id", async function () {
    const { token, payments, alice, sink, amount } = await fixture();
    const quoteId = settlementId("quote-1");
    const paid = await payments.connect(alice).payQuote(quoteId, amount);
    await expect(paid).to.emit(payments, "QuotePaid").withArgs(quoteId, alice.address, amount);
    expect(await token.balanceOf(sink.address)).to.equal(amount);
    expect(await token.balanceOf(alice.address)).to.equal(0n);
    expect(await payments.paymentOf(quoteId)).to.deep.equal([alice.address, amount, true]);

    const replay = await payments.connect(alice).payQuote(quoteId, amount);
    await expect(replay).to.emit(payments, "QuotePaymentReplay").withArgs(quoteId, alice.address, amount);
    expect(await token.balanceOf(sink.address)).to.equal(amount);
  });

  it("rejects a conflicting replay and does not record a paused payment", async function () {
    const { token, payments, pauser, minter, alice, bob, amount } = await fixture();
    const quoteId = settlementId("quote-conflict");
    await payments.connect(alice).payQuote(quoteId, amount);
    await token.connect(minter).settleMint(bob.address, amount, settlementId("quote-bob"));
    await token.connect(bob).approve(await payments.getAddress(), amount);
    await expect(payments.connect(bob).payQuote(quoteId, amount))
      .to.be.revertedWithCustomError(payments, "QuoteConflict")
      .withArgs(quoteId);
    await expect(payments.connect(alice).payQuote(quoteId, amount - 1n))
      .to.be.revertedWithCustomError(payments, "QuoteConflict")
      .withArgs(quoteId);

    const fresh = settlementId("quote-paused");
    await token.connect(pauser).pause();
    await expect(payments.connect(bob).payQuote(fresh, amount)).to.be.revertedWithCustomError(token, "EnforcedPause");
    expect(await payments.paymentOf(fresh)).to.deep.equal([ethers.ZeroAddress, 0n, false]);
  });

  it("rejects an empty quote id", async function () {
    const { payments, alice, amount } = await fixture();
    await expect(payments.connect(alice).payQuote(ethers.ZeroHash, amount))
      .to.be.revertedWithCustomError(payments, "EmptyQuoteId");
  });
});
