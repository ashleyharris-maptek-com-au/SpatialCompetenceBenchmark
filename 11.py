title = "Hyper-snake Challenge"

promptChangeSummary = "Dimensions increase from 3D to 6D"

problems = [{
  "dim": 2,
  "size": [8, 8],
  "start": [0, 0],
  "walls": [],
  "food": [[1, 1]]
}, {
  "dim": 2,
  "size": (8, 8),
  "start": (0, 0),
  "walls": [(5, 5), (6, 6), (0, 1)],
  "food": [[7, 7]]
}, {
  "dim": 3,
  "size": [4, 4, 4],
  "start": [1, 0, 1],
  "walls": [[1, 1, 1]],
  "food": [[1, 2, 1]]
}, {
  "dim": 3,
  "size": [4, 4, 4],
  "start": [1, 1, 1],
  "walls": [(0, 0, 1)],
  "food": [(0, 0, 0)]
}, {
  "dim": 4,
  "size": [5, 5, 5, 5],
  "start": [4, 4, 4, 4],
  "walls": [(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0)],
  "food": [(0, 0, 0, 0)]
}, {
  "dim": 4,
  "size": [5, 3, 3, 5],
  "start": [4, 1, 1, 4],
  "walls": [(0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0)],
  "food": [(0, 0, 0, 0)]
}, {
  "dim": 5,
  "size": [4, 4, 4, 4, 4],
  "start": [0, 0, 1, 1, 1],
  "walls": [(3, 3, 3, 3, 3)],
  "food": [(3, 0, 3, 0, 3), (0, 3, 0, 3, 0)]
}, {
  "dim": 6,
  "size": [4, 4, 4, 4, 4, 2],
  "start": [0, 0, 0, 0, 0, 0],
  "walls": [(0, 0, 1, 0, 0, 0)],
  "food": [(0, 0, 3, 0, 0, 1), (0, 0, 0, 0, 0, 1)]
}, {
  "dim": 6,
  "size": [3, 3, 3, 3, 3, 3],
  "start": [0, 0, 1, 0, 0, 0],
  "walls": [(0, 0, 1, 2, 0, 0)],
  "food": [(0, 0, 2, 0, 0, 0), (0, 0, 0, 0, 0, 0)]
}, {
  "dim": 7,
  "size": [3, 3, 3, 3, 3, 3, 3],
  "start": [0, 0, 0, 0, 0, 0, 0],
  "walls": [(0, 0, 1, 2, 0, 0, 0), (0, 2, 1, 0, 0, 0, 0)],
  "food": [(0, 0, 0, 0, 0, 1, 1), (0, 0, 0, 1, 1, 0, 0)]
}, {
  "dim": 8,
  "size": [3, 3, 3, 2, 2, 2, 3, 3],
  "start": [0, 0, 0, 0, 0, 0, 0, 0],
  "walls": [(0, 0, 1, 1, 0, 0, 0, 0), (0, 1, 1, 0, 0, 0, 0, 0)],
  "food": [(0, 0, 0, 0, 0, 1, 1, 1), (0, 0, 0, 1, 1, 0, 0, 0)]
}, {
  "dim": 9,
  "size": [2, 2, 2, 2, 2, 2, 8, 2, 2],
  "start": [0, 0, 0, 0, 0, 0, 5, 0, 0],
  "walls": [(0, 0, 0, 0, 0, 0, 4, 0, 0), (0, 1, 1, 0, 0, 0, 4, 0, 0)],
  "food": [(0, 0, 0, 0, 0, 1, 1, 1, 1), (0, 0, 0, 1, 1, 0, 0, 0, 0)]
}, {
  "dim": 10,
  "size": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
  "start": [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
  "walls": [(0, 0, 1, 0, 0, 0, 0, 0, 0, 0), (0, 1, 1, 0, 0, 0, 0, 0, 0, 0)],
  "food": [(0, 0, 0, 0, 0, 1, 1, 1, 1, 1), (0, 0, 0, 1, 1, 0, 0, 0, 0, 0)]
}]

subpassParamSummary = []

for p in problems:
  dim, size, start, walls, foods = p.values()
  subpassParamSummary.append(f"{dim}D snake in {size} grid.")
  if walls:
    subpassParamSummary[-1] += f" with {walls} walls."
  if foods:
    subpassParamSummary[-1] += f" with {foods} food."

promptChangeSummary = "Dimensions increase from 3D to 10D"

prompt = """
Do you remember the snake game, where you have to direct a snake around a 2D space to avoid hitting itself? This is hyper-snake!

You are a snake in a {dim}D space grid of size {size}. You can move to any adjacent cell in the grid, along any of the
available {dim} dimensions, but you can not move to a cell which you have visited before, nor can you move "diagonally",
that is, you can not move in more than one dimension at a time.

The game ends when you run out of space to move, when you hit the boundary, or when you run into yourself.

{wallString}

{foodString}

Return the path of the snake as a list of cells, the first element of which is {start} (where you must start), and going for as long as you can.
"""

structure = {
  "type": "object",
  "properties": {
    "path": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "pos": {
            "type": "array",
            "items": {
              "type": "integer"
            }
          }
        },
        "propertyOrdering": ["pos"],
        "additionalProperties": False,
        "required": ["pos"]
      }
    }
  },
  "propertyOrdering": ["path"],
  "additionalProperties": False,
  "required": ["path"]
}


def prepareSubpassPrompt(index):
  if index == len(problems): raise StopIteration
  dim, size, start, walls, foods = problems[index].values()

  wallString = ""
  if walls:
    wallString = "You need to avoid the obstacles at: " + str(walls) + "."

  foodString = ""
  if foods:
    foodString = "You also need to collect the food at: " + str(foods) + "."

  return prompt.format(dim=dim,
                       size=size,
                       start=start,
                       wallString=wallString,
                       foodString=foodString)


def gradeAnswer(answer: dict, subPassIndex: int, aiEngineName: str):
  # Define test parameters based on subPassIndex
  dimRef, size, start, walls, foods = problems[subPassIndex].values()

  # Extract path from answer
  if "path" not in answer:
    return 0, "No path in answer"

  path = answer["path"]

  # Path must have at least one position
  if not path or len(path) == 0:
    return 0, "Empty path"

  # Check first position matches start
  if len(path[0]["pos"]) != dimRef:
    return 0, f"First position has wrong dimensions: {len(path[0]['pos'])} != {dimRef}"

  if list(path[0]["pos"]) != list(start):
    return 0, f"First position doesn't match start: {path[0]['pos']} != {start}"

  # Track visited cells to detect repeats
  visited = set()
  visited.add(tuple(path[0]["pos"]))

  food = set()
  for foodEntry in foods:
    food.add(tuple(foodEntry))

  # Validate each move
  for i in range(1, len(path)):
    curr_pos = path[i]["pos"]
    prev_pos = path[i - 1]["pos"]

    # Check dimensionality
    if len(curr_pos) != dimRef:
      return 0, f"Position {i} has wrong dimensions"

    # Count how many dimensions changed
    changes = []
    for dim in range(dimRef):
      if curr_pos[dim] != prev_pos[dim]:
        changes.append((dim, curr_pos[dim] - prev_pos[dim]))

    # Must change exactly one dimension
    if len(changes) != 1:
      return 0, f"Move {i} changed {len(changes)} dimensions (must be 1). From {prev_pos} to {curr_pos}"

    # Must be a single cell move (+1 or -1)
    dim, delta = changes[0]
    if abs(delta) != 1:
      return 0, f"Move {i} moved {abs(delta)} cells (must be 1) from {prev_pos} to {curr_pos}"

    # Check bounds
    for dim in range(dimRef):
      if curr_pos[dim] < 0 or curr_pos[dim] >= size[dim]:
        return 0, f"Position {i} is out of bounds"

    # Check for repeats
    pos_tuple = tuple(curr_pos)
    if pos_tuple in visited:
      return 0, f"Position {pos_tuple} visited more than once"

    if pos_tuple in walls:
      return 0, f"Position {pos_tuple} is a wall"

    visited.add(pos_tuple)

    if pos_tuple in food:
      food.remove(pos_tuple)

  # Score is the fraction of cells occupied
  total_cells = 1
  for s in size:
    total_cells *= s

  if walls:
    total_cells -= len(walls)

  score = len(path) / total_cells

  if walls:
    # Adding a wall can make perfect solutions impossible and makes the problem
    # NP-Hard, because of this we don't chase perfection with the grading - 1 or 2
    # missing holes is good enough, and typically indicates a solution wasn't possible.
    score = min(1, score / 0.98)

  explanation = f"Visited {len(path)}/{total_cells} cells ({score*100:.1f}%)"

  if food:
    score /= (len(food) + 1)
    explanation += f" (food not eaten: {len(food)})"

  return score, explanation


def resultToNiceReport(answer, subPassIndex, aiEngineName):
  """Generate interactive Three.js visualization for N-dimensional snake paths."""
  import hashlib
  import json

  dimensions, grid_size, start_pos, walls, food = problems[subPassIndex].values()

  # Extract path coordinates
  path_coords = []
  if answer and "path" in answer:
    for step in answer["path"]:
      if "pos" in step:
        path_coords.append(list(step["pos"]))

  total_cells = 1
  for s in grid_size:
    total_cells *= s

  total_cells -= len(walls)

  # Generate unique viewer ID
  viewer_id = f"snake-{hashlib.md5(f'{aiEngineName}_{subPassIndex}'.encode()).hexdigest()[:10]}"

  # Prepare data for JS
  config = {
    "dimensions": dimensions,
    "gridSize": grid_size,
    "startPos": start_pos,
    "walls": walls,
    "food": food,
    "path": path_coords,
  }

  html = f'''
<div id="{viewer_id}" style="width:100%;max-width:600px;margin:0 auto;">
  <div id="{viewer_id}-canvas" style="width:100%;height:400px;border:1px solid #444;background:#1a1a2e;"></div>
  <div id="{viewer_id}-controls" style="padding:8px;background:#2a2a3e;color:#ddd;font-size:12px;border-radius:0 0 4px 4px;">
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:center;">
      <span><b>{dimensions}D Grid</b> ({" × ".join(map(str, grid_size))})</span>
      <span>Path: <b style="color:#0f8">{len(path_coords)}/{total_cells}</b> cells</span>
      <label style="cursor:pointer;"><input type="checkbox" id="{viewer_id}-animate" checked> Animate</label>
      <label style="cursor:pointer;"><input type="checkbox" id="{viewer_id}-showgrid" checked> Grid</label>
    </div>
    <div id="{viewer_id}-sliders" style="margin-top:8px;"></div>
    <div style="margin-top:4px;font-size:11px;color:#888;">
      Drag to rotate • Scroll to zoom • Sliders project higher dims to 3D
    </div>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
// Global coordinator - only animate one viewer at a time (closest to viewport center)
if (!window.snakeViewerCoordinator) {{
  window.snakeViewerCoordinator = {{
    viewers: {{}},
    activeId: null,
    updateActive: function() {{
      const viewportCenter = window.innerHeight / 2;
      let closestId = null;
      let closestDist = Infinity;
      for (const [id, v] of Object.entries(this.viewers)) {{
        if (!v.visible) continue;
        const rect = v.container.getBoundingClientRect();
        const elemCenter = rect.top + rect.height / 2;
        const dist = Math.abs(elemCenter - viewportCenter);
        if (dist < closestDist) {{
          closestDist = dist;
          closestId = id;
        }}
      }}
      this.activeId = closestId;
    }},
    register: function(id, container) {{
      this.viewers[id] = {{ container, visible: false }};
      const observer = new IntersectionObserver((entries) => {{
        entries.forEach(e => {{
          this.viewers[id].visible = e.isIntersecting;
          this.updateActive();
        }});
      }}, {{ threshold: 0.1 }});
      observer.observe(container);
    }},
    isActive: function(id) {{
      return this.activeId === id;
    }}
  }};
  // Update on scroll
  let scrollTimeout;
  window.addEventListener('scroll', () => {{
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => window.snakeViewerCoordinator.updateActive(), 50);
  }}, {{ passive: true }});
}}
</script>
<script>
(function() {{
  const viewerId = '{viewer_id}';
  const config = {json.dumps(config)};
  const container = document.getElementById('{viewer_id}-canvas');
  if (!container) {{ console.error('Container not found'); return; }}
  window.snakeViewerCoordinator.register(viewerId, container);
  
  const dims = config.dimensions;
  // Ensure gridSize is padded to at least 3 dimensions
  const gridSize = [...config.gridSize];
  while (gridSize.length < 3) gridSize.push(1);
  
  const path = config.path;
  const walls = config.walls;
  const food = config.food;

  // Scene setup
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a2e);

  // Use fallback dimensions if container not yet laid out
  let width = container.clientWidth || 600;
  let height = container.clientHeight || 400;
  const camera = new THREE.PerspectiveCamera(50, width/height, 0.1, 1000);

  const renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setSize(width, height);
  container.appendChild(renderer.domElement);

  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  // Lighting
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
  dirLight.position.set(10, 20, 15);
  scene.add(dirLight);

  // Projection weights for dims > 3 (sliders control these)
  const projectionWeights = [];
  for (let d = 3; d < dims; d++) {{
    projectionWeights.push(0.5); // default middle slice
  }}

  // Create sliders for higher dimensions
  const sliderContainer = document.getElementById('{viewer_id}-sliders');
  if (dims > 3) {{
    const dimLabels = ['W', 'V', 'U', 'T', 'S', 'R', 'Q'];
    for (let d = 3; d < dims; d++) {{
      const idx = d - 3;
      const label = dimLabels[idx] || `D${{d}}`;
      const div = document.createElement('div');
      div.style.cssText = 'display:flex;align-items:center;gap:8px;margin:4px 0;';
      div.innerHTML = `
        <span style="width:80px;">Dim ${{d+1}} (${{label}}):</span>
        <input type="range" id="{viewer_id}-dim${{d}}" min="0" max="1" step="0.01" value="0.5" style="flex:1;">
        <span id="{viewer_id}-dim${{d}}-val" style="width:40px;">0.50</span>
      `;
      sliderContainer.appendChild(div);
      const slider = div.querySelector('input');
      const valSpan = div.querySelector('span:last-child');
      slider.addEventListener('input', () => {{
        projectionWeights[idx] = parseFloat(slider.value);
        valSpan.textContent = slider.value;
        rebuildVisualization();
      }});
    }}
  }}

  // Project N-dimensional point to 3D
  function projectTo3D(point) {{
    if (dims <= 3) {{
      // Pad to 3D if needed
      const p = [...point];
      while (p.length < 3) p.push(0);
      return p.slice(0, 3);
    }}
    // For dims > 3, use weighted projection
    // Base 3D coords are first 3 dims
    let x = point[0], y = point[1], z = point[2];
    // Higher dims influence position based on weights
    for (let d = 3; d < dims; d++) {{
      const weight = projectionWeights[d - 3];
      const coord = point[d] / (gridSize[d] - 1 || 1);
      // Project higher dims as offsets/rotations
      const angle = (d - 3) * Math.PI / 4 + coord * Math.PI * 0.3;
      const influence = (coord - weight) * 2;
      x += influence * Math.cos(angle) * 0.5;
      y += influence * Math.sin(angle) * 0.5;
      z += influence * 0.3;
    }}
    return [x, y, z];
  }}

  // Calculate alpha (visibility) based on higher-dim distance from slice
  function calcAlpha(point) {{
    if (dims <= 3) return 1.0;
    let totalDist = 0;
    for (let d = 3; d < dims; d++) {{
      const coord = point[d] / (gridSize[d] - 1 || 1);
      const weight = projectionWeights[d - 3];
      totalDist += Math.abs(coord - weight);
    }}
    return Math.max(0.1, 1.0 - totalDist * 0.5);
  }}

  // Groups for different elements
  let gridGroup = new THREE.Group();
  let pathGroup = new THREE.Group();
  let markerGroup = new THREE.Group();
  scene.add(gridGroup);
  scene.add(pathGroup);
  scene.add(markerGroup);

  // Materials
  const gridMaterial = new THREE.LineBasicMaterial({{ color: 0x404060, transparent: true, opacity: 0.3 }});
  const pathMaterial = new THREE.MeshPhongMaterial({{ color: 0x00ff88, emissive: 0x004422 }});
  const wallMaterial = new THREE.MeshPhongMaterial({{ color: 0xff4444, transparent: true, opacity: 0.8 }});
  const foodMaterial = new THREE.MeshPhongMaterial({{ color: 0x44ff44, emissive: 0x114411 }});
  const startMaterial = new THREE.MeshPhongMaterial({{ color: 0x4488ff, emissive: 0x112244 }});
  const headMaterial = new THREE.MeshPhongMaterial({{ color: 0xffff00, emissive: 0x444400 }});

  let animProgress = 0;
  let showGrid = true;
  let isLoaded = false;
  const MAX_VISIBLE_NODES = 500; // Only render last N nodes for performance

  // Shared geometries to avoid recreating
  let sharedSphereGeom = null;
  let sharedHeadGeom = null;
  let sharedStartGeom = null;

  function unloadGeometry() {{
    gridGroup.clear();
    pathGroup.clear();
    markerGroup.clear();
    isLoaded = false;
    cameraInitialized = false; // Allow camera reinit when reactivated
  }}

  function rebuildVisualization() {{
    // Clear old geometry
    gridGroup.clear();
    pathGroup.clear();
    markerGroup.clear();
    isLoaded = true;

    // Create shared geometries once
    if (!sharedSphereGeom) {{
      sharedSphereGeom = new THREE.SphereGeometry(0.2, 4, 4);
      sharedHeadGeom = new THREE.SphereGeometry(0.35, 6, 6);
      sharedStartGeom = new THREE.SphereGeometry(0.3, 4, 4);
    }}

    // Calculate center for camera
    const center = gridSize.slice(0, 3).map((s, i) => (s - 1) / 2);
    while (center.length < 3) center.push(0);

    // Draw grid edges (merged into single buffer)
    if (showGrid) {{
      const edges = [];
      function addEdgesRecursive(pos, dim) {{
        if (dim === Math.min(dims, 3)) {{
          for (let d = 0; d < Math.min(dims, 4); d++) {{
            if (pos[d] < gridSize[d] - 1) {{
              const p1 = projectTo3D([...pos, ...Array(Math.max(0, dims-3)).fill(0).map((_, i) => 
                Math.round(projectionWeights[i] * (gridSize[3+i]-1)))]);
              const nextPos = [...pos];
              nextPos[d]++;
              const p2 = projectTo3D([...nextPos, ...Array(Math.max(0, dims-3)).fill(0).map((_, i) => 
                Math.round(projectionWeights[i] * (gridSize[3+i]-1)))]);
              edges.push(...p1, ...p2);
            }}
          }}
          return;
        }}
        for (let i = 0; i < gridSize[dim]; i++) {{
          pos[dim] = i;
          addEdgesRecursive(pos, dim + 1);
        }}
      }}
      addEdgesRecursive(Array(dims).fill(0), 0);

      if (edges.length > 0) {{
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(edges), 3));
        gridGroup.add(new THREE.LineSegments(geometry, gridMaterial));
      }}
    }}

    // Draw walls (use instancing concept - but simpler: just fewer segments)
    walls.forEach(wall => {{
      const pos = projectTo3D(wall);
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.8, 0.8), wallMaterial);
      mesh.position.set(pos[0], pos[1], pos[2]);
      markerGroup.add(mesh);
    }});

    // Draw food
    food.forEach(f => {{
      const pos = projectTo3D(f);
      const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 8), foodMaterial);
      mesh.position.set(pos[0], pos[1], pos[2]);
      markerGroup.add(mesh);
    }});

    // Draw path - only last MAX_VISIBLE_NODES with fade
    if (path.length > 0) {{
      const totalVisible = Math.min(path.length, Math.floor(animProgress * path.length) + 1);
      const startIdx = Math.max(0, totalVisible - MAX_VISIBLE_NODES);
      const fadeWindow = MAX_VISIBLE_NODES;
      
      // Collect line segments into single merged buffer with vertex colors
      const linePositions = [];
      const lineColors = [];
      
      for (let i = startIdx; i < totalVisible; i++) {{
        const pos = projectTo3D(path[i]);
        const alpha = calcAlpha(path[i]);
        const isStart = i === 0;
        const isHead = i === totalVisible - 1;
        
        // Fade based on distance from head
        const distFromHead = totalVisible - 1 - i;
        const fadeFactor = Math.max(0, 1 - distFromHead / fadeWindow);
        const finalAlpha = alpha * fadeFactor;
        
        // Only draw node spheres for head, start
        if (isHead || isStart) {{
          const geom = isHead ? sharedHeadGeom : (isStart ? sharedStartGeom : sharedSphereGeom);
          const mat = (isHead ? headMaterial : (isStart ? startMaterial : pathMaterial)).clone();
          mat.transparent = true;
          mat.opacity = finalAlpha;
          const mesh = new THREE.Mesh(geom, mat);
          mesh.position.set(pos[0], pos[1], pos[2]);
          pathGroup.add(mesh);
        }}
        
        // Add line segment to merged buffer
        if (i < totalVisible - 1 && fadeFactor > 0.1) {{
          const p1 = pos;
          const p2 = projectTo3D(path[i + 1]);
          
          // Color gradient along path
          const t = i / Math.max(1, path.length - 1);
          let r, g, b;
          if (t < 0.5) {{
            r = 0; g = t * 2; b = 1 - t * 2;
          }} else {{
            r = (t - 0.5) * 2; g = 1; b = 0;
          }}
          
          linePositions.push(p1[0], p1[1], p1[2], p2[0], p2[1], p2[2]);
          // Vertex colors for both endpoints
          lineColors.push(r * fadeFactor, g * fadeFactor, b * fadeFactor);
          lineColors.push(r * fadeFactor, g * fadeFactor, b * fadeFactor);
        }}
      }}
      
      // Create single merged line geometry
      if (linePositions.length > 0) {{
        const lineGeom = new THREE.BufferGeometry();
        lineGeom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(linePositions), 3));
        lineGeom.setAttribute('color', new THREE.BufferAttribute(new Float32Array(lineColors), 3));
        const lineMat = new THREE.LineBasicMaterial({{ vertexColors: true, transparent: true, opacity: 0.8 }});
        pathGroup.add(new THREE.LineSegments(lineGeom, lineMat));
      }}
    }}
  }}

  // Initial camera setup (only once)
  let cameraInitialized = false;
  function initCamera() {{
    if (cameraInitialized) return;
    cameraInitialized = true;
    const center = gridSize.slice(0, 3).map((s) => (s - 1) / 2);
    const maxSize = Math.max(...gridSize.slice(0, 3), 1);
    camera.position.set(center[0] + maxSize * 2, center[1] + maxSize * 1.5, center[2] + maxSize * 2);
    controls.target.set(center[0], center[1], center[2]);
    controls.update();
  }}

  rebuildVisualization();
  initCamera();

  // Animation checkbox
  const animCheckbox = document.getElementById('{viewer_id}-animate');
  const gridCheckbox = document.getElementById('{viewer_id}-showgrid');
  
  gridCheckbox.addEventListener('change', () => {{
    showGrid = gridCheckbox.checked;
    rebuildVisualization();
  }});

  // Animation loop - only animate if this viewer is active (closest to viewport center)
  let lastTime = 0;
  let wasActive = false;
  function animate(time) {{
    requestAnimationFrame(animate);
    
    const isActive = window.snakeViewerCoordinator.isActive(viewerId);
    
    // If becoming inactive, unload geometry to save memory
    if (wasActive && !isActive) {{
      unloadGeometry();
      renderer.clear();
    }}
    
    // Only do work if active
    if (isActive) {{
      // Rebuild if just became active or animating
      if (!wasActive) {{
        rebuildVisualization();
        initCamera();
      }} else if (animCheckbox.checked && path.length > 1) {{
        const dt = (time - lastTime) / 100 / path.length;
        lastTime = time;
        animProgress += dt * 0.3;
        if (animProgress > 1.5) animProgress = 0;
        rebuildVisualization();
      }} else if (!animCheckbox.checked && animProgress < 1) {{
        animProgress = 1;
        rebuildVisualization();
      }}
      
      controls.update();
      renderer.render(scene, camera);
    }}
    
    wasActive = isActive;
  }}
  animate(0);

  // Handle resize
  const resizeObserver = new ResizeObserver(() => {{
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }});
  resizeObserver.observe(container);
}})();
</script>
'''

  return html


highLevelSummary = """
Think Snake on a Nokia Phone, but in higher dimensions.
<br><br>
It's interesting to graph the dimensions vs score of LLMs - Eg: why on earth does
ChatGPT manage to play Snake in 3D, 4D, 6D, but not 5D?

"""
