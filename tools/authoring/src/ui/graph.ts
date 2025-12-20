import { RPGraph } from '../lib/chaos-core/graph';
import { RPEntity, RPRelation } from '../lib/chaos-core/types';

interface WorldPack {
  entities?: Array<{
    id: string;
    kind: string;
    label?: string;
    position?: { x: number; y: number; z?: number };
    rp?: Partial<RPEntity>;
  }>;
  relations?: Array<{
    primitive: string;
    source: string;
    target?: string;
    weight?: number;
  }>;
}

interface LayoutNode {
  node: RPEntity;
  x: number;
  y: number;
}

interface Camera {
  x: number;
  y: number;
  zoom: number;
}

interface GraphState {
  nodes: LayoutNode[];
  edges: Array<{ relation: RPRelation; primitive: string }>;
  camera: Camera;
  hoveredNode: LayoutNode | null;
  selectedNode: LayoutNode | null;
  draggingNode: LayoutNode | null;
  panning: boolean;
  lastMouseX: number;
  lastMouseY: number;
}

// Store state per canvas
const graphStates = new WeakMap<HTMLCanvasElement, GraphState>();

function mapPrimitiveToEdgeType(primitive: string): RPRelation['type'] {
  switch (primitive) {
    case 'CONSTRAINT':
      return 'constraint';
    case 'META':
      return 'meta';
    case 'EPISTEMIC':
      return 'info';
    default:
      return 'influence';
  }
}

function edgeColor(primitive: string) {
  switch (primitive) {
    case 'GEOMETRY':
      return '#5ac8fa';
    case 'CONSTRAINT':
      return '#ff9f0a';
    case 'EPISTEMIC':
      return '#64d2ff';
    case 'DYNAMICS':
      return '#34c759';
    case 'META':
      return '#bf5af2';
    default:
      return '#8e8e93';
  }
}

function screenToWorld(screenX: number, screenY: number, camera: Camera, canvas: HTMLCanvasElement) {
  const rect = canvas.getBoundingClientRect();
  return {
    x: (screenX - rect.left - canvas.width / 2) / camera.zoom + camera.x,
    y: (screenY - rect.top - canvas.height / 2) / camera.zoom + camera.y
  };
}

function worldToScreen(worldX: number, worldY: number, camera: Camera, canvas: HTMLCanvasElement) {
  return {
    x: (worldX - camera.x) * camera.zoom + canvas.width / 2,
    y: (worldY - camera.y) * camera.zoom + canvas.height / 2
  };
}

function getNodeAtPosition(nodes: LayoutNode[], x: number, y: number, camera: Camera, canvas: HTMLCanvasElement): LayoutNode | null {
  for (let i = nodes.length - 1; i >= 0; i--) {
    const n = nodes[i];
    const screen = worldToScreen(n.x, n.y, camera, canvas);
    const size = (5 + (n.node.P2_dynamics + n.node.P4_constraints) * 4) * camera.zoom;
    const dx = x - screen.x;
    const dy = y - screen.y;
    if (dx * dx + dy * dy <= size * size) {
      return n;
    }
  }
  return null;
}

function setupInteractivity(canvas: HTMLCanvasElement, state: GraphState, redraw: () => void) {
  // Mouse wheel for zoom
  const handleWheel = (e: WheelEvent) => {
    e.preventDefault();
    
    const worldBefore = screenToWorld(e.clientX, e.clientY, state.camera, canvas);
    
    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    state.camera.zoom = Math.max(0.1, Math.min(5, state.camera.zoom * zoomFactor));
    
    const worldAfter = screenToWorld(e.clientX, e.clientY, state.camera, canvas);
    state.camera.x += worldBefore.x - worldAfter.x;
    state.camera.y += worldBefore.y - worldAfter.y;
    
    redraw();
  };

  // Mouse down - start drag or pan
  const handleMouseDown = (e: MouseEvent) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    state.lastMouseX = e.clientX;
    state.lastMouseY = e.clientY;
    
    const nodeUnderMouse = getNodeAtPosition(state.nodes, mouseX, mouseY, state.camera, canvas);
    
    if (nodeUnderMouse) {
      state.draggingNode = nodeUnderMouse;
      state.selectedNode = nodeUnderMouse;
      canvas.style.cursor = 'grabbing';
    } else {
      state.panning = true;
      state.selectedNode = null;
      canvas.style.cursor = 'grabbing';
    }
    
    redraw();
  };

  // Mouse move - drag node or pan
  const handleMouseMove = (e: MouseEvent) => {
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    if (state.draggingNode) {
      const dx = (e.clientX - state.lastMouseX) / state.camera.zoom;
      const dy = (e.clientY - state.lastMouseY) / state.camera.zoom;
      state.draggingNode.x += dx;
      state.draggingNode.y += dy;
      state.draggingNode.node.position.x = state.draggingNode.x;
      state.draggingNode.node.position.y = state.draggingNode.y;
      redraw();
    } else if (state.panning) {
      const dx = (e.clientX - state.lastMouseX) / state.camera.zoom;
      const dy = (e.clientY - state.lastMouseY) / state.camera.zoom;
      state.camera.x -= dx;
      state.camera.y -= dy;
      redraw();
    } else {
      // Update hover state
      const nodeUnderMouse = getNodeAtPosition(state.nodes, mouseX, mouseY, state.camera, canvas);
      if (nodeUnderMouse !== state.hoveredNode) {
        state.hoveredNode = nodeUnderMouse;
        canvas.style.cursor = nodeUnderMouse ? 'pointer' : 'grab';
        redraw();
      }
    }
    
    state.lastMouseX = e.clientX;
    state.lastMouseY = e.clientY;
  };

  // Mouse up - stop dragging
  const handleMouseUp = () => {
    state.draggingNode = null;
    state.panning = false;
    canvas.style.cursor = state.hoveredNode ? 'pointer' : 'grab';
  };

  // Mouse leave - stop everything
  const handleMouseLeave = () => {
    state.draggingNode = null;
    state.panning = false;
    state.hoveredNode = null;
    canvas.style.cursor = 'grab';
    redraw();
  };

  canvas.addEventListener('wheel', handleWheel, { passive: false });
  canvas.addEventListener('mousedown', handleMouseDown);
  canvas.addEventListener('mousemove', handleMouseMove);
  canvas.addEventListener('mouseup', handleMouseUp);
  canvas.addEventListener('mouseleave', handleMouseLeave);
  canvas.style.cursor = 'grab';
}

function drawGraph(canvas: HTMLCanvasElement, state: GraphState) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const { width, height } = canvas.getBoundingClientRect();
  canvas.width = width;
  canvas.height = height;

  // Clear background
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = '#0e131d';
  ctx.fillRect(0, 0, width, height);

  // Apply camera transform
  ctx.save();
  ctx.translate(width / 2, height / 2);
  ctx.scale(state.camera.zoom, state.camera.zoom);
  ctx.translate(-state.camera.x, -state.camera.y);

  // Draw edges
  ctx.lineWidth = 1 / state.camera.zoom;
  state.edges.forEach((e) => {
    const src = state.nodes.find((n) => n.node.id === e.relation.source);
    const tgt = state.nodes.find((n) => n.node.id === e.relation.target);
    if (!src || !tgt) return;
    
    const isConnectedToSelected = state.selectedNode && 
      (src.node.id === state.selectedNode.node.id || tgt.node.id === state.selectedNode.node.id);
    
    ctx.strokeStyle = edgeColor(e.primitive);
    ctx.globalAlpha = isConnectedToSelected ? 1.0 : 0.5;
    ctx.beginPath();
    ctx.moveTo(src.x, src.y);
    ctx.lineTo(tgt.x, tgt.y);
    ctx.stroke();
    ctx.globalAlpha = 1.0;
  });

  // Draw nodes
  state.nodes.forEach((n) => {
    const size = 5 + (n.node.P2_dynamics + n.node.P4_constraints) * 4;
    const isHovered = state.hoveredNode === n;
    const isSelected = state.selectedNode === n;
    
    // Node circle
    ctx.fillStyle = isSelected ? '#6b7ff8' : isHovered ? '#5a6ff3' : '#4f6af3';
    ctx.beginPath();
    ctx.arc(n.x, n.y, size, 0, Math.PI * 2);
    ctx.fill();
    
    // Highlight ring for hover/select
    if (isHovered || isSelected) {
      ctx.strokeStyle = isSelected ? '#8a9fff' : '#6b7ff8';
      ctx.lineWidth = 2 / state.camera.zoom;
      ctx.beginPath();
      ctx.arc(n.x, n.y, size + 2, 0, Math.PI * 2);
      ctx.stroke();
    }
    
    // Node label
    ctx.fillStyle = '#dfe3ec';
    ctx.font = `${11 / state.camera.zoom}px sans-serif`;
    ctx.fillText(n.node.id, n.x + size + 2, n.y + 4 / state.camera.zoom);
  });

  ctx.restore();

  // Draw tooltip for hovered node
  if (state.hoveredNode) {
    const n = state.hoveredNode;
    const screen = worldToScreen(n.x, n.y, state.camera, canvas);
    
    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.strokeStyle = '#4f6af3';
    ctx.lineWidth = 1;
    
    const lines = [
      `ID: ${n.node.id}`,
      `Type: ${n.node.type}`,
      `P1 Identity: ${n.node.P1_identity.toFixed(2)}`,
      `P2 Dynamics: ${n.node.P2_dynamics.toFixed(2)}`,
      `P3 Geometry: ${n.node.P3_geometry.toFixed(2)}`,
      `P4 Constraints: ${n.node.P4_constraints.toFixed(2)}`,
      `P5 Epistemic: ${n.node.P5_epistemic.toFixed(2)}`,
      `P6 Meta: ${n.node.P6_meta.toFixed(2)}`
    ];
    
    const padding = 8;
    const lineHeight = 16;
    const tooltipWidth = 180;
    const tooltipHeight = lines.length * lineHeight + padding * 2;
    
    let tooltipX = screen.x + 15;
    let tooltipY = screen.y - tooltipHeight / 2;
    
    // Keep tooltip on screen
    if (tooltipX + tooltipWidth > width) tooltipX = screen.x - tooltipWidth - 15;
    if (tooltipY < 0) tooltipY = 0;
    if (tooltipY + tooltipHeight > height) tooltipY = height - tooltipHeight;
    
    ctx.fillRect(tooltipX, tooltipY, tooltipWidth, tooltipHeight);
    ctx.strokeRect(tooltipX, tooltipY, tooltipWidth, tooltipHeight);
    
    ctx.fillStyle = '#dfe3ec';
    ctx.font = '12px monospace';
    lines.forEach((line, i) => {
      ctx.fillText(line, tooltipX + padding, tooltipY + padding + (i + 1) * lineHeight - 4);
    });
  }

  // Draw instructions in corner
  ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
  ctx.font = '11px sans-serif';
  ctx.fillText('🖱️ Scroll: Zoom | Drag: Pan | Drag nodes: Move', 10, height - 10);
}

export function renderGraph(canvas: HTMLCanvasElement, worldText: string) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  let parsed: WorldPack;
  try {
    parsed = JSON.parse(worldText || '{}');
  } catch {
    const { width, height } = canvas.getBoundingClientRect();
    canvas.width = width;
    canvas.height = height;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#0e131d';
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = '#f26d6d';
    ctx.fillText('World pack JSON invalid', 10, 20);
    return;
  }

  // Get or create state
  let state = graphStates.get(canvas);
  const isFirstRender = !state;

  if (!state) {
    state = {
      nodes: [],
      edges: [],
      camera: { x: 0, y: 0, zoom: 1 },
      hoveredNode: null,
      selectedNode: null,
      draggingNode: null,
      panning: false,
      lastMouseX: 0,
      lastMouseY: 0
    };
    graphStates.set(canvas, state);
  }

  // Parse data
  const g = new RPGraph();
  const nodes: LayoutNode[] = [];
  const edges: Array<{ relation: RPRelation; primitive: string }> = [];

  const { width, height } = canvas.getBoundingClientRect();
  
  for (const e of parsed.entities || []) {
    const pos = e.position || { x: Math.random() * width, y: Math.random() * height, z: 0 };
    const rpDefaults = { P1_identity: 0.5, P2_dynamics: 0.5, P3_geometry: 0.5, P4_constraints: 0.5, P5_epistemic: 0.5, P6_meta: 0.5 };
    const entity: RPEntity = {
      id: e.id,
      type: e.kind,
      position: { x: pos.x, y: pos.y, z: pos.z ?? 0 },
      velocity: { x: 0, y: 0, z: 0 },
      ...rpDefaults,
      ...(e.rp || {})
    };
    g.addEntity(entity);
    nodes.push({ node: entity, x: entity.position.x, y: entity.position.y });
  }

  for (const r of parsed.relations || []) {
    if (!r.target) continue;
    const rel: RPRelation = {
      source: r.source,
      target: r.target,
      weight: r.weight ?? 1,
      type: mapPrimitiveToEdgeType(r.primitive)
    };
    edges.push({ relation: rel, primitive: r.primitive });
    try {
      g.addRelation(rel);
    } catch {
      // ignore missing nodes
    }
  }

  // Simple layout: if positions don't exist, use circle layout
  const hasPositions = nodes.every((n) => typeof n.node.position.x === 'number' && typeof n.node.position.y === 'number');
  if (!hasPositions) {
    nodes.forEach((n, idx) => {
      const angle = (idx / nodes.length) * Math.PI * 2;
      const rad = Math.min(width, height) * 0.35;
      n.x = Math.cos(angle) * rad;
      n.y = Math.sin(angle) * rad;
      n.node.position.x = n.x;
      n.node.position.y = n.y;
    });
  } else {
    // Center the graph around origin
    const avgX = nodes.reduce((sum, n) => sum + n.x, 0) / nodes.length;
    const avgY = nodes.reduce((sum, n) => sum + n.y, 0) / nodes.length;
    nodes.forEach(n => {
      n.x -= avgX;
      n.y -= avgY;
    });
  }

  state.nodes = nodes;
  state.edges = edges;

  if (isFirstRender) {
    setupInteractivity(canvas, state, () => {
      const currentState = graphStates.get(canvas);
      if (currentState) drawGraph(canvas, currentState);
    });
  }

  drawGraph(canvas, state);
}
