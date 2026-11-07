// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {GalionTokenAlpha} from "./GalionTokenAlpha.sol";

/// @title GalionTokenAlphaV2
/// @notice Upgrade fixture. Adds a version getter and no state variables.
/// @dev New alpha state belongs inside the ERC-7201 `GalionTokenStorage` struct,
///      appended after the existing fields. Do not add linear storage here.
contract GalionTokenAlphaV2 is GalionTokenAlpha {
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function contractVersion() external pure returns (uint256) {
        return 2;
    }
}
