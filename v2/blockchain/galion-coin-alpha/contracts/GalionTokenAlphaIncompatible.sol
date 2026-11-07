// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

/// @title GalionTokenAlphaIncompatible
/// @notice Negative fixture for the upgrade checker. This layout is not a successor of GalionTokenAlpha.
contract GalionTokenAlphaIncompatible {
    address public replacedAdmin;
    uint256 public unrelated;
}
