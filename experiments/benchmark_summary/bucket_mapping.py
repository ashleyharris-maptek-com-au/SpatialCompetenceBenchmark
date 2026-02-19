"""SCBench bucket mapping used in paper notes.

This mapping is defined over the 22 active tasks (non-zero max_score) used in
the SCBench main evaluation.
"""

from __future__ import annotations

BUCKET_ORDER: tuple[str, ...] = ("Axiomatic", "Constructive", "Planning")

# Bucket mapping and paper display names.
#
# Mapping per paper appendix bucket table (285 subtasks total):
# - Axiomatic: Q51, Q52, Q53, Q54, Q57 (N=75).
# - Constructive: includes Delaunay (Q55) alongside mesh/CSG/packing tasks (N=171).
# - Planning: Q7, Q11, Q23, Q28 (N=39).
#
# Order is paper-facing (kept stable) rather than numeric test_index order.
PAPER_TASKS_BY_BUCKET: dict[str, list[tuple[int, str]]] = {
  "Axiomatic": [
    (51, "Topology Enumeration"),
    (52, "Enumerate Edges"),
    (53, "Classify Behaviour"),
    (54, "Half-Subdivision Neighbours"),
    (57, "Two Segments"),
  ],
  "Constructive": [
    (2, "Lego Hemispherical Shell"),
    (3, "CSG Union"),
    (4, "Tetrahedra Shadow Projection"),
    (6, "Voxel Grid Projection"),
    (8, "Polynomial Curve Fitting"),
    (55, "Delaunay Triangulation"),
    (9, "Hamiltonian Loop"),
    (12, "Pipe Loop Fitting"),
    (13, "Hide and Seek"),
    (16, "Pack Rectangular Prisms"),
    (29, "Interlocking Parts"),
    (30, "Largest 3D-Printable Prime"),
    (56, "Shikaku Rectangles"),
  ],
  "Planning": [
    (7, "3D Maze"),
    (11, "Hyper-Snake"),
    (23, "Fluid Simulation"),
    (28, "Terrain Levelling"),
  ],
}

BUCKET_TO_TEST_INDICES: dict[str, list[int]] = {
  bucket: [idx for idx, _label in pairs]
  for bucket, pairs in PAPER_TASKS_BY_BUCKET.items()
}

TEST_INDEX_TO_BUCKET: dict[int, str] = {
  test_index: bucket
  for bucket, test_indices in BUCKET_TO_TEST_INDICES.items()
  for test_index in test_indices
}
