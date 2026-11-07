// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title GalionQuotePaymentAlpha
/// @notice UNAUDITED sink for opaque quote payments on Polygon Amoy (chain id 80002).
/// @dev The quote id is a bytes32 chosen off-chain. This contract stores the payer,
///      the token amount, and that id. It does not store prompts, account profiles,
///      credit balances, or any other personal data. Replaying the same quote with the
///      same payer and amount does not pull tokens again. A conflicting replay reverts.
///      This contract is not a redemption reserve and does not price service credits.
contract GalionQuotePaymentAlpha is ReentrancyGuard {
    using SafeERC20 for IERC20;

    uint256 public constant POLYGON_AMOY_CHAIN_ID = 80002;

    IERC20 public immutable token;
    address public immutable sink;

    struct Payment {
        address payer;
        uint256 amount;
        bool recorded;
    }

    mapping(bytes32 quoteId => Payment) private _payments;

    error UnsupportedChain(uint256 chainId);
    error ZeroAddress();
    error EmptyQuoteId();
    error ZeroAmount();
    error QuoteConflict(bytes32 quoteId);
    error NativeCoinNotAccepted();

    event QuotePaid(bytes32 indexed quoteId, address indexed payer, uint256 amount);
    event QuotePaymentReplay(bytes32 indexed quoteId, address indexed payer, uint256 amount);

    constructor(address token_, address sink_) {
        if (block.chainid != POLYGON_AMOY_CHAIN_ID) revert UnsupportedChain(block.chainid);
        if (token_ == address(0) || sink_ == address(0)) revert ZeroAddress();
        token = IERC20(token_);
        sink = sink_;
    }

    function payQuote(bytes32 quoteId, uint256 amount) external nonReentrant returns (bool recordedFresh) {
        if (block.chainid != POLYGON_AMOY_CHAIN_ID) revert UnsupportedChain(block.chainid);
        if (quoteId == bytes32(0)) revert EmptyQuoteId();
        if (amount == 0) revert ZeroAmount();

        Payment storage payment = _payments[quoteId];
        if (payment.recorded) {
            if (payment.payer != msg.sender || payment.amount != amount) revert QuoteConflict(quoteId);
            emit QuotePaymentReplay(quoteId, msg.sender, amount);
            return false;
        }

        payment.payer = msg.sender;
        payment.amount = amount;
        payment.recorded = true;
        token.safeTransferFrom(msg.sender, sink, amount);
        emit QuotePaid(quoteId, msg.sender, amount);
        return true;
    }

    function paymentOf(bytes32 quoteId) external view returns (address payer, uint256 amount, bool recorded) {
        Payment storage payment = _payments[quoteId];
        return (payment.payer, payment.amount, payment.recorded);
    }

    receive() external payable {
        revert NativeCoinNotAccepted();
    }
}
