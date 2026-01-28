def get_response(subPass: int):
  return """
## Purpose and constraints

You’re capturing **raw-ish sensor-domain** data from a mechanically scanned LiDAR + co‑axial panoramic RGBA imaging. The primary constraint is **minimum on-disk size** for *very large* captures, with loss that is **never worse than** the sensor’s own quantisation:

* **Angles:** 20-bit azimuth and elevation (encoder resolution).
* **Range / time-of-flight:** quantised to **16 GHz ticks** (≈ 62.5 ps; ≈ 9.37 mm one-way range resolution for ToF/2).
* **Return signal strength:** 12-bit.
* Per emitted beam: **0..N returns**, usually 0 or 1, sometimes more.

The file is **immutable once written**, so you can afford:

* two-pass coding (collect statistics, then compress),
* building multiple indices and previews,
* expensive predictors and entropy coding,
* post‑processing.

You also want to optimise for **typical terrestrial infrastructure scans**:

* 90% stationary scanner (a near-ideal case for angular grid compression),
* large contiguous “sky” regions with no returns,
* lots of smooth surfaces (walls, roads),
* relatively sparse multi‑return events (glass, foliage, fog etc.).

The rest of this report compares approaches, lists optimisations (good and bad), and recommends what to adopt.

---

## Three viable “big picture” representations

### Option A — Sensor-domain “range image” (recommended primary)

**Store what the scanner actually measures:** (azimuth, elevation, time-of-flight, intensity), plus a pose stream if moving.

**Pros**

* Exploits the *strongest structure you have*: near-regular 2D sampling in angle/time.
* Enables extremely compact encoding: angles are predictable, ranges are locally smooth.
* Keeps multi-return semantics natural.
* Lets you align colour imagery naturally in the same 2D parameterisation.

**Cons**

* Less interoperable than point-cloud formats.
* Spatial queries (give me points in this 3D box) need an index or a transform step.

**Verdict:** Best for “edge over competitors” on size.

---

### Option B — Cartesian point cloud (XYZ + attributes), e.g. LAS/LAZ style

**Pros**

* Great interoperability and tooling (PDAL etc.).
* Simple conceptual model.

**Cons**

* You throw away the scanner’s 2D sampling structure.
* You pay for 3 coordinates per point (plus scaling/offset), and you lose “no return” beams unless you separately represent them.
* Compression ratios can be good (LAZ is strong), but you’re starting from a “fluffier” representation. LASzip/LAZ is lossless and typically shrinks LAS substantially (often down to a small fraction). ([GitHub][1])

**Verdict:** Excellent *export* format, poor *primary archive* if compactness is the priority.

---

### Option C — Hybrid: sensor-domain primary + optional derived products

Store the sensor-domain stream as the **truth**, and optionally include:

* a decimated point cloud (preview / quick-load),
* a spatial index (for region queries),
* a multi-resolution LOD pyramid,
* optionally an LAZ export chunk set.

**Pros**

* Keeps best compression and preserves raw measurement model.
* Still supports fast visualisation / spatial access without reprocessing.

**Cons**

* More engineering.
* Some duplication (but you can bound it).

**Verdict:** Best overall product strategy.

---

## Recommended file architecture

Borrow two proven ideas from existing formats:

1. **Chunked, independently-compressed blocks + explicit index**

   * Ouster’s OSF is a chunk-based binary format with an internal index mapping timestamps to chunks for random access. ([static.ouster.dev][2])
   * Apache Parquet writes metadata (locations of column chunks, etc.) at the end to allow single-pass writing. ([Parquet][3])
     Apply the same pattern to LiDAR: write blocks sequentially, then write a footer index.

2. **Columnar / “structure-of-arrays” layout**

   * Store each attribute stream separately (range, intensity, return count, etc.), because:

     * it compresses better,
     * it vectorises well on decode,
     * readers can skip unneeded streams.

### Top-level layout (practical and compact)

**Header (small, fixed)**

* Magic, version, endianness.
* Scanner model ID + calibration hash.
* Global coordinate frame metadata.
* Flags for presence of optional streams (imagery, GPS/IMU, waveform, etc.).
* Offset to **footer index** (or 0 placeholder if streaming; filled at end).

**Data region**

* Sequence of **Blocks** (each block independent for random access).

**Footer**

* Block directory (offset/length, compression codec ids, beam grid sizes, time range).
* Optional spatial summaries (AABB, min/max range, histogram summaries).
* Optional LOD directory.
* CRC / checksum of directory.

This “footer index” pattern is well-understood and scales to enormous files because a reader can open the file, seek to the end, read the index, then jump directly to needed blocks. ([Parquet][3])

---

## Block granularity and partitioning

### What to chunk by

Chunking should align with *predictability* and *seeking patterns*:

* **Primary axis:** slow mirror motion (azimuth/time)
* **Secondary axis:** vertical sweep samples (elevation)

A good block is a **rectangular patch in (scanline, sample)** space, e.g.:

* 256–2048 scanlines per block (tunable),
* full vertical resolution for each scanline (all samples).

#### Why rectangular?

It lets you treat key streams as 2D arrays:

* first-return range map,
* first-return intensity map,
* validity mask,
* colour tiles.

That unlocks strong 2D predictors (image-like compression) and also makes GPU pipelines easier later.

### Block size target

Even with “infinite processing”, you still want practical random access:

* Aim for **compressed block sizes** in the ~1–16 MiB range.

  * Too small ⇒ overhead, weaker entropy context, bigger index.
  * Too large ⇒ poor seeking and cache behaviour.

### Adapt blocks on parameter changes

Whenever any of these change, start a new block:

* vertical sample count / capture rate,
* slow mirror mode (arc vs full rotation),
* calibration update,
* compression settings,
* “moving vs fixed” mode switch.

---

## Data model inside a block

Think of each emitted beam as living at integer coordinates:

* `u = scanline index` (slow axis)
* `v = sample index within the vertical sweep` (fast axis)

For each beam you need:

* **ReturnCount(u,v)**: 0..N
* For each return k:

  * **ToFTicks(u,v,k)**: integer ticks @ 16 GHz (quantised)
  * **Intensity(u,v,k)**: integer 0..4095 (12-bit)

Optionally:

* return flags (first/last/strongest),
* confidence / saturation bits,
* classification hints (if computed on board).

Imagery:

* either store the raw RGBA panorama in a separate image stream,
* or store colour already resampled to the (u,v) grid (often smaller to use).

Pose:

* if fixed: a single static pose record.
* if moving: a pose trajectory time series; each scanline references time.

---

## Compression pipeline (recommended baseline)

A reliable baseline that tends to get near-optimal results on structured numeric data is:

1. **Quantise to sensor limits** (loss within your acceptable bounds)
2. **Predict / delta encode** (make residuals small and centred around 0)
3. **Entropy compress** each stream independently, per block
4. Optional: second-pass “global” compression is usually unnecessary if (2) is good.

This mirrors how high-performing LiDAR compressors work: LASzip-like approaches predict fields from previous points and compress residuals with arithmetic coding. ([lastools.github.io][4])

You don’t have to literally use arithmetic coding, but the principle is key: **predict then entropy-code residuals**.

---

## Specific optimisations: wise, risky, and unwise

Below is a catalogue of optimisations, including your list. For each one I’ve included:

* **What it buys you**
* **Risks / costs**
* **Recommendation**

### 1) Angles: store implicitly + small residuals (very wise)

#### A) Don’t store 20-bit azimuth/elevation per beam

Your scanning mechanism already provides a deterministic *expected* angle per sample index.

Store per block (or per scanline):

* `ElevModel`: one of:

  * constant step: `elev0 + v*elevStep`
  * small LUT: `elev[v]` if you truly need it
* `AziModel` per scanline `u`:

  * `aziStart[u]` + **tilt term** `aziSlope[u] * v`
  * (or `aziStart + v*slope` using fixed-point)

Then store **residual corrections** only when needed:

* residuals are typically tiny (encoder noise, mechanical jitter),
* encode residuals as small signed ints (zig-zag), RLE runs of zero.

**Why this is big:** it often removes *40 bits per beam* from the payload.

**Your suggestion coverage**

* “Store fixed resolution angle data tightly packed - 20-bits” ✅ but better: store *models + residuals* instead of raw.
* “Store x data less frequently than y” ✅ yes: store per scanline or per block.
* “Store y implicitly or delta from expected” ✅ exactly.
* “Vertical scanlines are fractionally tilted” ✅ encode a slope term.

**Recommendation:** Adopt.

---

### 2) ReturnCount encoding: optimise for 0/1 returns (very wise)

Most beams are:

* no return (sky),
* exactly one return (solid surface).

**Best practice**

* Store a **HitMask** bitset: 1 bit/beam indicates at least one return.
* Optionally also store an **ExtraMask** bitset for “has 2+ returns”.
* Store actual return data in packed arrays only for hits.

This is a classic sparse representation:

* If sky is large, HitMask compresses extremely well with RLE or bitmap codecs.
* It avoids storing dummy range/intensity for no-return beams.

Alternative (also good):

* store 2 bits per beam for {0,1,2,escape}, plus an escape stream for 3+.

**Recommendation:** Adopt, with adaptive choice per block:

* if hits are dense: 2-bit returncount grid may be smaller/easier,
* if hits are sparse: masks + packed arrays win.

---

### 3) Range/ToF: store in ticks, predict in 2D, entropy-code residuals (very wise)

#### A) Store ToF as integer ticks (not float)

This is exactly your “no loss beyond 16 GHz” constraint.

Avoid:

* metres as floats,
* seconds as floats.

If you want a physical unit, store **scale metadata**:

* `RangeMetres = ToFTicks * (c / 2) / 16e9`
  …but keep the stored values integer.

**Recommendation:** Adopt.

#### B) 2D predictors like image codecs

Because your data is a 2D angular grid, treat first-return range as a “depth image”.

Good predictors (in order of increasing complexity):

* 1D delta along v (vertical), reset each scanline
* 1D delta along u (between scanlines) for same v
* 2D “median of neighbours” predictor (JPEG-LS/LOCO-I style)
* plane predictor: predict using a small local plane fit to neighbours

After prediction:

* residuals are small signed integers,
* encode with:

  * Rice/Golomb (great for Laplacian-ish residuals),
  * rANS/FSE,
  * or zstd after packing.

**Recommendation:** Adopt (at least 1D+2D median predictor).

---

### 4) Secondary returns: delta-from-first and sparse indices (very wise)

Your suggestion:

* “Store secondary beam impacts as a delta from the first return” ✅

Implement it as:

* For beams with extra returns:

  * store `extraCount` (often 1),
  * store `deltaTicks[i] = ToFTicks(return i) - ToFTicks(previous return)`

    * deltas are non-negative and usually small.

Also store secondary intensities:

* either raw 12-bit values,
* or delta from first intensity if correlated (often not as correlated as range).

**Recommendation:** Adopt.

---

### 5) Bit packing vs “let zstd compress the zeros” (wise, but subtle)

Your suggestion:

* “Store 20-bit angles tightly packed”
* “Store 12-bit strengths tightly packed”

Bit packing absolutely reduces raw size. But there is a nuance:

* If you plan to apply a strong compressor afterwards (zstd, etc.), sometimes leaving values padded to 16 bits can still compress well because high bits are often zero.
* However, with *hundreds of billions* of samples, a guaranteed 33% overhead on a major stream is too expensive to gamble on.

**Recommendation**

* Pack to the native bit widths **inside each block**, but keep decoding simple:

  * pack 12-bit into 3-byte pairs,
  * pack 20-bit into 5-byte pairs or 10-byte groups, etc.
* Then apply prediction/entropy coding; don’t rely on generic compression alone.

---

### 6) “Store like data with like data” (very wise)

Structure-of-arrays beats array-of-structures for compression and for selective reading.

**Recommended internal streams**

* `HitMask`
* `FirstRangeTicks[]`
* `FirstIntensity[]`
* `ExtraMask` (optional)
* `ExtraCounts[]` (for beams with extras)
* `ExtraRangeDeltas[]`
* `ExtraIntensity[]`
* Optional per-beam flags stream
* Optional classification stream

**Recommendation:** Adopt.

---

### 7) Image data: store as image, tile it, and align tiles with LiDAR blocks (wise)

Your suggestion:

* “Separate RGBA arrays from beam data”
* “Compress image data using an established image algorithm”
* “Allow image data for missing beams”
  All ✅.

**Key decision:** keep imagery **logically independent** from LiDAR returns:

* store camera calibration + projection model,
* store image in its own coordinate system,
* colourisation is a mapping step at read time.

**Tiling**

* Store image in tiles that correspond to your LiDAR blocks (same azimuth span).
* That allows:

  * partial read,
  * reuse of block index,
  * small working sets.

**Codec choice**

* PNG is safe and ubiquitous; OSF uses PNG-based lossless compression for per-channel LiDAR frames by default. ([GitHub][5])
* If size is king and you control the ecosystem, consider:

  * JPEG XL lossless / near-lossless,
  * AVIF lossless (implementation maturity varies),
  * WebP lossless.

**Recommendation**

* Adopt tiling and separate storage.
* Start with PNG or zstd-compressed raw tiles for simplicity.
* Consider JPEG XL as an “ultra” option if size dominates and you can ship a decoder.

---

### 8) Use block-based compression and support seeking (very wise)

Your suggestion:

* “Use a streaming / block based compression algorithm to allow fast seeking”

Yes. Two common ways:

#### A) Independent compressed frames per block

* Each block is a self-contained compressed blob.
* Reader seeks using the footer index.

#### B) Use a defined “seekable” compressed container

Zstandard has a documented seekable framing idea: a series of independent frames plus a seek table at the end. ([Android Gooblesource][6])

**Recommendation**

* Do (A) as the base (it’s format-agnostic and simplest).
* Optionally provide a codec id that means “zstd seekable frames” if you want that ecosystem.

---

### 9) Two-pass “static codebooks per block” (wise, because immutable)

Because the file is immutable, you can do what real-time formats often can’t:

* pass 1: collect histograms of residuals,
* pass 2: encode with a near-optimal static code (Huffman, arithmetic, rANS).

This is one reason LAZ-style compressors do well: they exploit predictability and encode residuals efficiently (often with arithmetic coding). ([IET Research Journal][7])

**Recommendation:** Adopt if you’re chasing maximum ratios. It’s complexity, but not conceptually risky.

---

### 10) Store motion separately (very wise)

Your suggestion:

* “When motion happens, store the path separately to keep polar form”

Exactly.

For moving vehicle mode, don’t store full pose per beam:

* Store pose as a **time-indexed trajectory**:

  * piecewise linear position,
  * piecewise slerp quaternion,
  * quantised to the sensor’s practical pose accuracy.
* Store per scanline:

  * a timestamp (or tick index),
  * optionally a small correction term if scanline timing jitter matters.

Then beam times within the scanline are implicit from sample index and known mirror timing.

**Recommendation:** Adopt.

---

### 11) Preview / thumbnail / LOD pyramid (wise, optional but valuable)

Your suggestion:

* “Store a thumbnail, low res preview, or part of the data at the start”

This is often worth a small overhead because it makes the product *feel* fast.

Options:

* **Header preview:** a decimated scan (e.g., every 32nd scanline and every 16th vertical sample).
* **Low-res panoramic image** thumbnail.
* **Hierarchy:** multi-resolution pyramid in blocks (Potree-style concept).

**Size impact**

* If you keep it to ~0.1–1% of the full data, it’s almost always worth it.

**Recommendation:** Adopt a decimated preview + thumbnail. Consider full LOD pyramid as an “enterprise / massive data” feature.

---

## Higher-risk / “edge” optimisations (potentially wise, but easy to get wrong)

These are the things that can win benchmarks but also create maintenance debt.

### A) Explicit planar/primitive surface modelling

Your suggestion:

* “Optimisation for flat surfaces when encountered?”

In principle:

* segment planes (walls/roads),
* store plane parameters,
* store small residual per beam.

**Why it can help**

* Large planar regions compress extremely well with a plane model (residuals near 0).

**Risks**

* Segmentation errors are catastrophic if you must stay within strict error bounds.
* Encoding the segmentation map can cost a lot.
* Scenes are not *only* planar; clutter breaks it.

**Recommendation**

* Don’t make this the baseline.
* Make it an optional per-block codec mode:

  * encoder can choose it only when it measurably wins.

---

### B) Reordering beams for compression (Morton/Z-order)

Reordering can improve locality for some predictors but can break the natural scanline model, complicate mapping to imagery, and complicate incremental decoding.

**Recommendation**

* Avoid by default.
* If you do it, do it only within block and store the reorder as implicit (e.g., fixed Morton traversal), not as a huge permutation table.

---

### C) ML-based or “semantic” compression

E.g., compress by storing detected objects, meshes, or a learned latent code.

**Risks**

* Violates your “no extra loss beyond sensor limits” in practice.
* Massive complexity and long-term brittleness.
* Hard to validate correctness.

**Recommendation:** Avoid for the core archive format.

---

## Unwise optimisations (your “bad” list plus more)

### 1) Store Cartesian XYZ as primary

You already flagged this as bad, and I agree for a size-first archive:

* you spend 3 numbers per point,
* you lose the perfect 2D sampling structure,
* it’s harder to represent “no return beams” and multi-return cleanly.

**Better**

* store polar + ToF and compute XYZ when needed.

**Recommendation:** Avoid as primary. Offer as export.

---

### 2) Voxelise as primary storage

Also flagged as bad:

* you impose a grid resolution that will either explode size or lose detail,
* awkward for multiple returns and intensity.

Voxelisation is a **derived product** (for rendering, collision, occupancy), not a measurement archive.

**Recommendation:** Avoid as primary; optional derived LOD.

---

### 3) Store distances in metres as floats / store time as float seconds

Floats are bad here:

* they waste bits relative to your quantised integer resolution,
* they introduce non-uniform quantisation and rounding ambiguity,
* they complicate exact “within sensor limits” guarantees.

**Recommendation:** Avoid.

---

### 4) One giant compressed stream for the whole file (unwise)

It may compress slightly better, but:

* kills seeking,
* makes corruption catastrophic,
* makes parallel decode hard.

**Recommendation:** Avoid.

---

### 5) Per-beam variable-length records with lots of tiny headers (unwise)

It *feels* natural (“each beam is a record”), but it bloats:

* varints, tags, alignment, and per-record overhead add up enormously at 10^8–10^11 scale.

**Recommendation:** Avoid. Keep overhead per beam at the bit level, amortised per block.

---

## Concrete recommendation: what to adopt now vs later

### Adopt now (high ROI, low regret)

1. **Sensor-domain primary representation** (angles model + ToF ticks + intensity).
2. **Block / chunk structure** with independent compression and a footer index (Parquet-style). ([Parquet][3])
3. **SoA/columnar streams** inside each block.
4. **Implicit angles + slope (“tilt”) per scanline** and residual corrections.
5. **Sparse handling of no-returns** (HitMask) + “extra returns are sparse”.
6. **Delta/predictive coding** of first-return ToF in 2D + entropy coding.
7. **Secondary returns as deltas** from previous return.
8. **Image stream separated + tiled**, compressed with a standard codec.
9. **Motion path stream** separate and time-indexed.
10. **Preview payload** (decimated scan + thumbnail).

### Adopt as optional codec modes (if you’re chasing the last %)

* Plane/primitive modelling per block (only when it wins).
* Two-pass codebooks per block (static Huffman/rANS).
* More aggressive context modelling (different predictors for ground vs facade, etc.).

### Avoid

* Cartesian primary storage, voxel primary storage, float metres/seconds, monolithic compression.

---

## Notes on “use zlib/zstd/lzma2 vs arithmetic coding”

* **zstd** is an excellent baseline for block compression (fast, strong, widely available). ([facebook.github.io][8])
* “Seekable zstd” framing exists conceptually as multiple frames + seek table. ([Android Gooblesource][6])
* For *numeric residuals* after prediction, a purpose-built entropy coder (Rice/rANS/arithmetic) can beat general LZ in ratio.
* LASzip-style results come from *prediction + entropy coding*, not “just zip it”. ([IET Research Journal][7])

Pragmatically:

* Start with **predict + zstd per stream per block**.
* Add an “entropy-only” codec id later if you want the last 5–15% savings.

---

## Where existing formats land (and why you can beat them)

* **E57** is a vendor-neutral format that can store point clouds, imagery, and metadata (standardised by ASTM). ([ASTM International | ASTM][9])
  It is designed for interoperability and flexibility, not necessarily maximum compactness for *your* scanning geometry.

* **LAZ/LASzip** is a highly effective lossless compression of LAS, often yielding very large reductions, by predicting attributes and entropy coding residuals. ([GitHub][1])
  But it operates on a point-cloud record model rather than your natural range-image domain.

* **OSF** (Ouster) demonstrates the practical value of a chunked, indexed time-series container and per-channel compression. ([static.ouster.dev][2])
  You can take the same philosophy but use predictors/codecs tailored to your mirror-scanned range image.

* **Draco / MPEG PCC (G‑PCC)** target general 3D geometry compression (often for graphics / immersive media) and can be excellent, but they’re not naturally aligned with your “beam grid + multi-return” sensor model and can bring complexity or unwanted loss. ([Google GitHub][10])

That’s the core opportunity: **you have more structure than generic point clouds**—use it.

---

## Mapping your list to decisions

Here’s your list, with my “adopt / adjust / avoid”:

### Your “good”

* Chunk/split coherently ✅ **Adopt** (rectangular blocks in scanline/sample space).
* Separate RGBA from beam data ✅ **Adopt** (tiled imagery stream).
* Optimise for flat surfaces ✅ **Optional** (codec mode; don’t baseline).
* Store in polar form ✅ **Adopt** (primary).
* Bit-pack 20-bit angles ✅ **Adjust**: prefer implicit models + residuals; pack residuals.
* Store 12-bit strengths tightly ✅ **Adopt** (pack; then compress).
* Optimise for 0/1 returns ✅ **Adopt** (HitMask + sparse extras).
* Secondary impacts as delta ✅ **Adopt**.
* Store x less frequently than y ✅ **Adopt** (per scanline azimuth model).
* Tilted scanlines encode slope ✅ **Adopt**.
* Compress image using established codec ✅ **Adopt** (tile).
* Post-process with zlib/zstd/lzma2/arithmetic ✅ **Adopt** (predict+zstd baseline; entropy later).
* Streaming/block compression for seek ✅ **Adopt**.
* Store y implicitly/delta ✅ **Adopt**.
* Image data for missing beams ✅ **Adopt** (imagery independent).
* Thumbnail/preview ✅ **Adopt** (bounded overhead).
* Adjacent ranges similar ✅ **Adopt** (2D predictor).
* Motion path separately ✅ **Adopt**.
* SoA over AoS ✅ **Adopt**.

### Your “bad”

* Cartesian coordinates primary ✅ **Avoid** (export only).
* Voxelise primary ✅ **Avoid** (derived only).
* Distances in metres ✅ **Avoid if float**; **OK if fixed-point**, but ticks are better.
* Floating point seconds ✅ **Avoid**.

---

## Final “best bet” design in one paragraph

A compact, future-proof format for this scanner should be a **chunked, indexed, columnar sensor-domain container**: store beams on a 2D grid (scanline × vertical sample), encode angles as **implicit models + tiny residuals**, represent returns with **bitmasks + packed arrays**, encode first-return range/intensity with **2D prediction + entropy coding**, treat extra returns as **sparse deltas**, store motion as a separate **pose trajectory**, store imagery as separately tiled compressed images, and write a **footer directory** for fast seeking and partial reads—optionally with a small preview at the start.

If you want, I can turn this into a more formal mini-spec (field-by-field binary layout, exact bit packing, block header design, and suggested codec IDs) and include a worked example of predicted residual coding for first-return ToF/intensity.

[1]: https://github.com/LASzip/LASzip/blob/master/README.md?utm_source=chatgpt.com "LASzip/README.md at master · LASzip/LASzip · GitHub"
[2]: https://static.ouster.dev/sdk-docs/reference/osf.html?utm_source=chatgpt.com "Open Sensor Format — Ouster Sensor SDK 0.16.0 documentation"
[3]: https://parquet.apache.org/docs/file-format/?utm_source=chatgpt.com "File Format - Apache Parquet"
[4]: https://lastools.github.io/download/laszip.pdf?utm_source=chatgpt.com "laszip.dvi - GitHub Pages"
[5]: https://github.com/ouster-lidar/ouster-sdk/blob/master/docs/reference/osf.rst?utm_source=chatgpt.com "ouster-sdk/docs/reference/osf.rst at master · ouster-lidar ... - GitHub"
[6]: https://android.googlesource.com/platform/external/zstd/%2B/refs/heads/main/contrib/seekable_format/zstd_seekable_compression_format.md?utm_source=chatgpt.com "Zstandard Seekable Format - android.googlesource.com"
[7]: https://ietresearch.onlinelibrary.wiley.com/doi/pdf/10.1049/el.2013.2585?utm_source=chatgpt.com "Improving LiDAR compression efficiency on small packets"
[8]: https://facebook.github.io/zstd/zstd_manual.html?utm_source=chatgpt.com "zstd 1.5.1 Manual - GitHub Pages"
[9]: https://www.astm.org/e2807-11r19.html?utm_source=chatgpt.com "Standard Specification for 3D Imaging Data Exchange, Version 1.0"
[10]: https://google.github.io/draco/?utm_source=chatgpt.com "Draco 3D Graphics Compression - GitHub"
""", "This was made by pasting my own list of ideas, classified into good and bad, and asking chatGPT5.2pro to turn it into a report."


def get_always_wrong(subPass: int):
  """Get an always-wrong response for this question."""
  filler = "This report intentionally avoids specific optimization ideas and offers no actionable guidance. "
  return (filler * 30).strip(), "Always-wrong placeholder"


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  paragraphs = []
  for idx in range(6):
    paragraphs.append(
      f"Paragraph {idx + 1}: This is a speculative compression idea about chunking,\n"
      f"entropy coding, and sensor-domain encoding. Seed={rng.random():.5f}.")
  return "\n\n".join(paragraphs), "Random guess"
