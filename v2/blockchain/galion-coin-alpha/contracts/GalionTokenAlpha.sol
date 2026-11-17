// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import {ERC20Upgradeable} from "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import {ERC20BurnableUpgradeable} from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20BurnableUpgradeable.sol";
import {ERC20PausableUpgradeable} from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PausableUpgradeable.sol";
import {AccessControlUpgradeable} from "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import {UUPSUpgradeable} from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import {IGalionTokenAlpha} from "./interfaces/IGalionTokenAlpha.sol";

/// @title GalionTokenAlpha
/// @notice UNAUDITED ERC-20 skeleton for local tests against Polygon Amoy (chain id 80002).
/// @dev This repository does not deploy the contract and has no mainnet configuration.
///      The token name and symbol are supplied to {initialize}. They are not chosen here.
///      Service credits, quotes, prompts, and personal data are not stored in this contract.
///
///      Issuance is cumulative. Burning reduces balances and totalSupply, and it does not
///      reopen the cap. Every mint requires a fresh settlement id. Replaying the same id
///      with the same recipient and amount is a no-op. A replay with different parameters reverts.
///
///      Operational roles are self-administered. The default admin cannot mint, pause, upgrade,
///      or grant those roles. The upgrader can still replace the implementation, so that key
///      remains the root of future code. There is no timelock in this alpha.
contract GalionTokenAlpha is
    Initializable,
    ERC20Upgradeable,
    ERC20BurnableUpgradeable,
    ERC20PausableUpgradeable,
    AccessControlUpgradeable,
    UUPSUpgradeable,
    IGalionTokenAlpha
{
    uint256 public constant POLYGON_AMOY_CHAIN_ID = 80002;

    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant UPGRADER_ROLE = keccak256("UPGRADER_ROLE");

    struct SettlementRecord {
        address account;
        uint256 amount;
        bool used;
    }

    /// @custom:storage-location erc7201:galion.alpha.token.v1
    struct GalionTokenStorage {
        uint256 cap;
        uint256 cumulativeMinted;
        uint64 allowedChainId;
        mapping(bytes32 settlementId => SettlementRecord) settlements;
    }

    // keccak256(abi.encode(uint256(keccak256("galion.alpha.token.v1")) - 1)) & ~bytes32(uint256(0xff))
    bytes32 private constant GALION_TOKEN_STORAGE_LOCATION =
        0xe91ac59f6a9f943770313967e20a7bee7810ac50a722b06c89ba9c8f50d8c300;

    error UnsupportedChain(uint256 chainId);
    error ZeroAddress();
    error ZeroAmount();
    error InvalidName();
    error InvalidSymbol();
    error CapZero();
    error RolesMustBeDistinct();
    error CapExceeded(uint256 cap_, uint256 attemptedCumulative);
    error EmptySettlementId();
    error SettlementConflict(bytes32 settlementId);
    error NativeCoinNotAccepted();

    event SettlementMinted(bytes32 indexed settlementId, address indexed account, uint256 amount);
    event SettlementReplay(bytes32 indexed settlementId, address indexed account, uint256 amount);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /// @inheritdoc IGalionTokenAlpha
    function initialize(
        string memory name_,
        string memory symbol_,
        uint256 cap_,
        address admin,
        address pauser,
        address minter,
        address upgrader
    ) public initializer {
        if (block.chainid != POLYGON_AMOY_CHAIN_ID) revert UnsupportedChain(block.chainid);
        if (bytes(name_).length == 0 || bytes(name_).length > 64) revert InvalidName();
        if (bytes(symbol_).length == 0 || bytes(symbol_).length > 11) revert InvalidSymbol();
        if (cap_ == 0) revert CapZero();
        if (admin == address(0) || pauser == address(0) || minter == address(0) || upgrader == address(0)) {
            revert ZeroAddress();
        }
        if (
            admin == pauser || admin == minter || admin == upgrader || pauser == minter || pauser == upgrader
                || minter == upgrader
        ) {
            revert RolesMustBeDistinct();
        }

        __ERC20_init(name_, symbol_);
        __ERC20Burnable_init();
        __ERC20Pausable_init();
        __AccessControl_init();

        GalionTokenStorage storage $ = _getGalionTokenStorage();
        $.cap = cap_;
        $.allowedChainId = uint64(POLYGON_AMOY_CHAIN_ID);

        _setRoleAdmin(PAUSER_ROLE, PAUSER_ROLE);
        _setRoleAdmin(MINTER_ROLE, MINTER_ROLE);
        _setRoleAdmin(UPGRADER_ROLE, UPGRADER_ROLE);

        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(PAUSER_ROLE, pauser);
        _grantRole(MINTER_ROLE, minter);
        _grantRole(UPGRADER_ROLE, upgrader);
    }

    /// @inheritdoc IGalionTokenAlpha
    function settleMint(address to, uint256 amount, bytes32 settlementId)
        external
        onlyRole(MINTER_ROLE)
        returns (bool mintedFresh)
    {
        _requireAllowedChain();
        if (to == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        if (settlementId == bytes32(0)) revert EmptySettlementId();

        GalionTokenStorage storage $ = _getGalionTokenStorage();
        SettlementRecord storage record = $.settlements[settlementId];
        if (record.used) {
            if (record.account != to || record.amount != amount) revert SettlementConflict(settlementId);
            emit SettlementReplay(settlementId, to, amount);
            return false;
        }

        _mintWithinCap(to, amount);
        record.account = to;
        record.amount = amount;
        record.used = true;
        emit SettlementMinted(settlementId, to, amount);
        return true;
    }

    /// @inheritdoc IGalionTokenAlpha
    function pause() external onlyRole(PAUSER_ROLE) {
        _requireAllowedChain();
        _pause();
    }

    /// @inheritdoc IGalionTokenAlpha
    function unpause() external onlyRole(PAUSER_ROLE) {
        _requireAllowedChain();
        _unpause();
    }

    /// @inheritdoc IGalionTokenAlpha
    function cap() public view returns (uint256) {
        return _getGalionTokenStorage().cap;
    }

    /// @inheritdoc IGalionTokenAlpha
    function cumulativeMinted() public view returns (uint256) {
        return _getGalionTokenStorage().cumulativeMinted;
    }

    /// @inheritdoc IGalionTokenAlpha
    function remainingMintable() public view returns (uint256) {
        GalionTokenStorage storage $ = _getGalionTokenStorage();
        return $.cap - $.cumulativeMinted;
    }

    /// @inheritdoc IGalionTokenAlpha
    function allowedChainId() public view returns (uint64) {
        return _getGalionTokenStorage().allowedChainId;
    }

    /// @inheritdoc IGalionTokenAlpha
    function getSettlement(bytes32 settlementId) external view returns (address account, uint256 amount, bool used) {
        SettlementRecord storage record = _getGalionTokenStorage().settlements[settlementId];
        return (record.account, record.amount, record.used);
    }

    function grantRole(bytes32 role, address account) public override {
        _requireAllowedChain();
        super.grantRole(role, account);
    }

    function revokeRole(bytes32 role, address account) public override {
        _requireAllowedChain();
        super.revokeRole(role, account);
    }

    function renounceRole(bytes32 role, address callerConfirmation) public override {
        _requireAllowedChain();
        super.renounceRole(role, callerConfirmation);
    }

    /// @dev Native coin is not a payment rail for this token. Reject it so testnet gas cannot sit here.
    receive() external payable {
        revert NativeCoinNotAccepted();
    }

    function _mintWithinCap(address to, uint256 amount) internal {
        GalionTokenStorage storage $ = _getGalionTokenStorage();
        uint256 next = $.cumulativeMinted + amount;
        if (next > $.cap) revert CapExceeded($.cap, next);
        $.cumulativeMinted = next;
        _mint(to, amount);
    }

    function _requireAllowedChain() internal view {
        if (block.chainid != POLYGON_AMOY_CHAIN_ID || _getGalionTokenStorage().allowedChainId != POLYGON_AMOY_CHAIN_ID)
        {
            revert UnsupportedChain(block.chainid);
        }
    }

    function _authorizeUpgrade(address newImplementation) internal view override onlyRole(UPGRADER_ROLE) {
        _requireAllowedChain();
        if (newImplementation == address(0)) revert ZeroAddress();
    }

    function _update(address from, address to, uint256 value)
        internal
        override(ERC20Upgradeable, ERC20PausableUpgradeable)
    {
        _requireAllowedChain();
        super._update(from, to, value);
    }

    function _getGalionTokenStorage() private pure returns (GalionTokenStorage storage $) {
        bytes32 slot = GALION_TOKEN_STORAGE_LOCATION;
        assembly {
            $.slot := slot
        }
    }
}
