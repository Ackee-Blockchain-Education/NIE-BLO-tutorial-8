// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

import "wake/console.sol";
import "./IComet.sol";
import "./IERC20.sol";

library SafeERC20 {
    function safeApprove(address token, address spender, uint amount) internal {
        (bool success, bytes memory data) = token.call(abi.encodeWithSignature("approve(address,uint256)", spender, amount));
        require(success && (data.length == 0 || abi.decode(data, (bool))), "Approve failed");
    }

    function safeTransferFrom(address token, address from, address to, uint amount) internal {
        (bool success, bytes memory data) = token.call(abi.encodeWithSignature("transferFrom(address,address,uint256)", from, to, amount));
        require(success && (data.length == 0 || abi.decode(data, (bool))), "TransferFrom failed");
    }
}

contract Stage2 {
    using SafeERC20 for address;

    IERC20 public immutable USDC = IERC20(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48);
    IERC20 public immutable USDT = IERC20(0xdAC17F958D2ee523a2206206994597C13D831ec7);

    address public owner;

    mapping(address => IComet) public comets;

    constructor() {
        owner = msg.sender;

        // USDC
        comets[address(USDC)] = IComet(0xc3d688B66703497DAA19211EEdff47f25384cdc3);

        // USDT
        comets[address(USDT)] = IComet(0x3Afdc9BCA9213A35503b077a6072F3D0d5AB0840);
    }

    function deposit(address token, uint amount) public {
        require(msg.sender == owner, "Only owner can deposit");
        require(comets[token] != IComet(address(0)), "Token not registered");

        token.safeTransferFrom(msg.sender, address(this), amount);

        IComet comet = comets[token];

        token.safeApprove(address(comet), amount);
        comet.supply(token, amount);
    }

    function swap(address tokenIn, address tokenOut, uint amount) public {
        require(comets[tokenIn] != IComet(address(0)), "TokenIn not registered");
        require(comets[tokenOut] != IComet(address(0)), "TokenOut not registered");

        IComet cometIn = comets[tokenIn];
        IComet cometOut = comets[tokenOut];

        tokenIn.safeTransferFrom(msg.sender, address(this), amount);

        cometOut.withdraw(tokenOut, amount);

        tokenIn.safeApprove(address(cometIn), amount);
        cometIn.supply(tokenIn, amount);

        tokenOut.safeApprove(msg.sender, amount + IERC20(tokenOut).allowance(address(this), msg.sender));
    }
}