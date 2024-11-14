// SPDX-License-Identifier: MIT

pragma solidity ^0.8.20;

import "wake/console.sol";

contract Stage1 {
    error BugFound();

    // wake-disable-next-line 2018
    function f(uint256 x, uint256 y, uint256 z) public {
        console.log("x", x);
        console.log("y", y);
        console.log("z", z);

        if (x > 114999999000000000000000000000000000000000000000000000000000000000000000000000) {
            if (
                y >= x - 100000000000000000000000000000000000000000000000000000000000000000000000000000 &&
                y < 16474011154664524427946373126085988481683748083205070504932198000989141204992
            ) {
                if (z >= y * 2 && z <= y * 4) {
                    revert BugFound();
                }
            }
        }
    }
}