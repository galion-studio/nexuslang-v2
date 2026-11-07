// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// @notice External surface of the unaudited Galion token alpha.
/// @dev Name and symbol are initializer arguments. This interface does not choose them.
interface IGalionTokenAlpha {
    function initialize(
        string memory name_,
        string memory symbol_,
        uint256 cap_,
        address admin,
        address pauser,
        address minter,
        address upgrader
    ) external;

    function settleMint(address to, uint256 amount, bytes32 settlementId) external returns (bool mintedFresh);

    function pause() external;

    function unpause() external;

    function cap() external view returns (uint256);

    function cumulativeMinted() external view returns (uint256);

    function remainingMintable() external view returns (uint256);

    function allowedChainId() external view returns (uint64);

    function getSettlement(bytes32 settlementId) external view returns (address account, uint256 amount, bool used);
}
