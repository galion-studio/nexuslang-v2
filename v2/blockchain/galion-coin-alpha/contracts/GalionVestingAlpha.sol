// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/// @title GalionVestingAlpha
/// @notice UNAUDITED, non-upgradeable vesting schedule for the token alpha on Polygon Amoy.
/// @dev Nothing is releasable before `cliffEnd`. After the cliff, tokens vest linearly until `end`.
///      Calling {release} when nothing is due returns zero and does not transfer. This schedule
///      does not promise yield, interest, or a right to exchange vested tokens for service credits.
///      The contract is intentionally not upgradeable so a later implementation cannot shorten the cliff.
contract GalionVestingAlpha is ReentrancyGuard {
    using SafeERC20 for IERC20;

    uint256 public constant POLYGON_AMOY_CHAIN_ID = 80002;

    IERC20 public immutable token;
    address public immutable beneficiary;
    uint256 public immutable total;
    uint64 public immutable start;
    uint64 public immutable cliffEnd;
    uint64 public immutable end;

    uint256 public released;
    bool public funded;

    error UnsupportedChain(uint256 chainId);
    error ZeroAddress();
    error ZeroAmount();
    error InvalidSchedule();
    error AlreadyFunded();
    error NotFunded();
    error NativeCoinNotAccepted();

    event Funded(address indexed from, uint256 amount);
    event Released(address indexed beneficiary, uint256 amount);

    constructor(
        address token_,
        address beneficiary_,
        uint256 total_,
        uint64 start_,
        uint64 cliffDuration_,
        uint64 vestDuration_
    ) {
        if (block.chainid != POLYGON_AMOY_CHAIN_ID) revert UnsupportedChain(block.chainid);
        if (token_ == address(0) || beneficiary_ == address(0)) revert ZeroAddress();
        if (total_ == 0) revert ZeroAmount();
        if (vestDuration_ == 0) revert InvalidSchedule();

        uint64 cliffEnd_ = start_ + cliffDuration_;
        uint64 end_ = cliffEnd_ + vestDuration_;
        if (end_ <= cliffEnd_) revert InvalidSchedule();

        token = IERC20(token_);
        beneficiary = beneficiary_;
        total = total_;
        start = start_;
        cliffEnd = cliffEnd_;
        end = end_;
    }

    function fund() external nonReentrant {
        if (block.chainid != POLYGON_AMOY_CHAIN_ID) revert UnsupportedChain(block.chainid);
        if (funded) revert AlreadyFunded();
        funded = true;
        token.safeTransferFrom(msg.sender, address(this), total);
        emit Funded(msg.sender, total);
    }

    /// @notice Vested amount at `timestamp`. Unfunded schedules report zero.
    function vestedAmount(uint64 timestamp) public view returns (uint256) {
        if (!funded || timestamp < cliffEnd) return 0;
        if (timestamp >= end) return total;
        return (total * (uint256(timestamp) - uint256(cliffEnd))) / uint256(end - cliffEnd);
    }

    function releasable() public view returns (uint256) {
        return vestedAmount(uint64(block.timestamp)) - released;
    }

    /// @return amount Tokens transferred on this call. Zero when the call is a replay or nothing is due.
    function release() external nonReentrant returns (uint256 amount) {
        if (block.chainid != POLYGON_AMOY_CHAIN_ID) revert UnsupportedChain(block.chainid);
        if (!funded) revert NotFunded();
        amount = releasable();
        if (amount == 0) return 0;
        released += amount;
        token.safeTransfer(beneficiary, amount);
        emit Released(beneficiary, amount);
    }

    receive() external payable {
        revert NativeCoinNotAccepted();
    }
}
