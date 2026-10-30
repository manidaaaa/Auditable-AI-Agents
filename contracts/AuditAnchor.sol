// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AuditAnchor
/// @notice Stores Merkle roots of agent log batches. Only hashes are stored, never raw logs.
/// Hashing matches the Python side: leaf = sha256(0x00 || entryHash), node = sha256(0x01 || left || right).
contract AuditAnchor {
    struct Batch {
        bytes32 root;
        uint64 firstIndex;
        uint64 count;
        uint64 timestamp;
    }

    mapping(address => Batch[]) private batches;

    event BatchAnchored(address indexed agent, uint256 indexed batchId, bytes32 root, uint64 firstIndex, uint64 count);

    /// @notice Anchor the next batch for the calling agent. Batches must be contiguous.
    function anchor(bytes32 root, uint64 count) external returns (uint256 batchId) {
        require(count > 0, "empty batch");
        Batch[] storage own = batches[msg.sender];
        uint64 firstIndex = own.length == 0 ? 0 : own[own.length - 1].firstIndex + own[own.length - 1].count;
        own.push(Batch(root, firstIndex, count, uint64(block.timestamp)));
        batchId = own.length - 1;
        emit BatchAnchored(msg.sender, batchId, root, firstIndex, count);
    }

    function batchCount(address agent) external view returns (uint256) {
        return batches[agent].length;
    }

    function getBatch(address agent, uint256 batchId) external view returns (Batch memory) {
        require(batchId < batches[agent].length, "no such batch");
        return batches[agent][batchId];
    }

    /// @notice Check on-chain that an entry hash belongs to an anchored batch.
    /// @param sides For each proof step, true if the sibling is on the right.
    function verifyInclusion(
        address agent,
        uint256 batchId,
        bytes32 entryHash,
        bytes32[] calldata siblings,
        bool[] calldata sides
    ) external view returns (bool) {
        require(siblings.length == sides.length, "length mismatch");
        require(batchId < batches[agent].length, "no such batch");
        bytes32 current = sha256(abi.encodePacked(bytes1(0x00), entryHash));
        for (uint256 i = 0; i < siblings.length; i++) {
            current = sides[i]
                ? sha256(abi.encodePacked(bytes1(0x01), current, siblings[i]))
                : sha256(abi.encodePacked(bytes1(0x01), siblings[i], current));
        }
        return current == batches[agent][batchId].root;
    }
}
