const { expect } = require("chai");
const { ethers } = require("hardhat");
const vectors = require("../tests/vectors/audit_vectors.json");

const b32 = (hex) => "0x" + hex;

describe("AuditAnchor", () => {
  let anchor, agent, other;

  beforeEach(async () => {
    [agent, other] = await ethers.getSigners();
    anchor = await (await ethers.getContractFactory("AuditAnchor")).deploy();
  });

  describe("anchoring", () => {
    it("stores batches with contiguous index ranges", async () => {
      await anchor.connect(agent).anchor(b32(vectors[0].root), 10);
      await anchor.connect(agent).anchor(b32(vectors[1].root), 5);
      expect(await anchor.batchCount(agent.address)).to.equal(2);
      const second = await anchor.getBatch(agent.address, 1);
      expect(second.root).to.equal(b32(vectors[1].root));
      expect(second.firstIndex).to.equal(10);
      expect(second.count).to.equal(5);
    });

    it("keeps each agent's batches separate", async () => {
      await anchor.connect(agent).anchor(b32(vectors[0].root), 1);
      expect(await anchor.batchCount(other.address)).to.equal(0);
    });

    it("emits BatchAnchored", async () => {
      await expect(anchor.connect(agent).anchor(b32(vectors[2].root), 3))
        .to.emit(anchor, "BatchAnchored")
        .withArgs(agent.address, 0, b32(vectors[2].root), 0, 3);
    });

    it("rejects empty batches and unknown ids", async () => {
      await expect(anchor.anchor(b32(vectors[0].root), 0)).to.be.revertedWith("empty batch");
      await expect(anchor.getBatch(agent.address, 0)).to.be.revertedWith("no such batch");
    });
  });

  describe("Python/Solidity hash agreement", () => {
    for (const v of vectors) {
      it(`verifies every Python proof on-chain for a tree of ${v.n} entries`, async () => {
        await anchor.connect(agent).anchor(b32(v.root), v.n);
        for (let i = 0; i < v.n; i++) {
          const siblings = v.proofs[i].map((s) => b32(s.hash));
          const sides = v.proofs[i].map((s) => s.right);
          expect(
            await anchor.verifyInclusion(agent.address, 0, b32(v.entry_hashes[i]), siblings, sides)
          ).to.equal(true, `entry ${i}`);
        }
      });
    }

    it("rejects a wrong entry hash, wrong side, or wrong batch", async () => {
      const v = vectors.find((x) => x.n === 8);
      await anchor.connect(agent).anchor(b32(v.root), v.n);
      await anchor.connect(agent).anchor(b32(vectors[1].root), 2);
      const siblings = v.proofs[3].map((s) => b32(s.hash));
      const sides = v.proofs[3].map((s) => s.right);
      expect(await anchor.verifyInclusion(agent.address, 0, b32(v.entry_hashes[4]), siblings, sides)).to.equal(false);
      const flipped = sides.map((s, i) => (i === 0 ? !s : s));
      expect(await anchor.verifyInclusion(agent.address, 0, b32(v.entry_hashes[3]), siblings, flipped)).to.equal(false);
      expect(await anchor.verifyInclusion(agent.address, 1, b32(v.entry_hashes[3]), siblings, sides)).to.equal(false);
    });

    it("rejects mismatched proof arrays", async () => {
      await anchor.connect(agent).anchor(b32(vectors[1].root), 2);
      await expect(
        anchor.verifyInclusion(agent.address, 0, b32(vectors[1].entry_hashes[0]), [b32(vectors[1].entry_hashes[1])], [])
      ).to.be.revertedWith("length mismatch");
    });
  });
});
