import { HardhatUserConfig, task } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "@openzeppelin/hardhat-upgrades";

/**
 * In-memory chain id only. There is no RPC URL, no account list, and no
 * mainnet network in this package. Deployment tasks refuse to broadcast.
 */
function localChainId(): number {
  const raw = process.env.GALION_TEST_CHAIN_ID;
  if (raw === undefined || raw === "") {
    return 80002;
  }
  if (raw === "31337") {
    return 31337;
  }
  throw new Error(
    `Refusing GALION_TEST_CHAIN_ID=${raw}. This package configures no RPC and no mainnet. ` +
      "Leave the variable unset for the in-memory Polygon Amoy chain id 80002, " +
      "or set 31337 only for the negative chain-guard test."
  );
}

task(
  "deploy",
  "Disabled. This package must not broadcast to Polygon Amoy or any other network."
).setAction(async () => {
  throw new Error(
    "Deployment is disabled. Refusing to broadcast to any network, including Polygon Amoy."
  );
});

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.28",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },
  networks: {
    hardhat: {
      chainId: localChainId(),
    },
  },
};

export default config;
