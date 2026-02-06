# Agent Instructions

- Do not open a pull request/merge request without explicit user approval in the current conversation.
- Always use the repo's venv when running Python or pip commands.
- Prefer `uv` (if available) for Python version management and package installs.

## Venv Bootstrap Notes (macOS arm64)

`pybullet` currently needs a local source patch on newer macOS SDKs. Follow this exact order.

1. Ensure OpenSCAD nightly (`openscad@snapshot`) is installed/up to date:
```bash
brew install --cask openscad@snapshot || true
brew upgrade --cask openscad@snapshot
openscad --version
```

2. Recreate a native arm64 venv (do not use Rosetta/x86 Python):
```bash
rm -rf .venv
uv venv --python /opt/homebrew/bin/python3.11 .venv
source .venv/bin/activate
file "$(which python)"   # must show arm64
python -m ensurepip --upgrade
```

3. Build a patched `pybullet` wheel locally:
```bash
source .venv/bin/activate
rm -rf /tmp/pybullet_src_build && mkdir -p /tmp/pybullet_src_build
python -m pip download --no-binary=:all: pybullet==3.2.7 -d /tmp/pybullet_src_build
cd /tmp/pybullet_src_build
tar -xzf pybullet-3.2.7.tar.gz
cd pybullet-3.2.7
sed -i '' 's/^#if defined(MACOS) || defined(TARGET_OS_MAC)$/#if defined(MACOS) || (defined(TARGET_OS_MAC) \&\& !defined(__APPLE__))/' examples/ThirdPartyLibs/zlib/zutil.h
python -m pip wheel . -w /tmp/pybullet_src_build/dist
```

4. Install patched `pybullet`, then the full requirements:
```bash
source .venv/bin/activate
uv pip install /tmp/pybullet_src_build/dist/pybullet-3.2.7-cp311-cp311-macosx_26_0_arm64.whl
uv pip install -r requirements.txt
```

5. Verify both key dependencies:
```bash
source .venv/bin/activate
python -c "import pybullet; print(pybullet.__file__)"
openscad --version
```

## Why this is needed

- `pybullet==3.2.7` has no macOS arm64 wheel on PyPI, so it builds from source.
- On recent macOS SDKs, the bundled zlib header in pybullet conflicts around `fdopen` and fails compilation unless patched.
