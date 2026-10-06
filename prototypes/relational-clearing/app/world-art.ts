import {
  OBSERVATION_RADIUS,
  WORLD_HEIGHT,
  WORLD_WIDTH,
  type Agent,
  type Decoration,
  type Point,
  type SignalOverlay,
  type WorldState,
  signalAt,
} from "./simulation";

type DrawContext = CanvasRenderingContext2D;

function roundedRect(ctx: DrawContext, x: number, y: number, width: number, height: number, radius: number) {
  ctx.beginPath();
  ctx.roundRect(x, y, width, height, radius);
}

function drawLeaf(ctx: DrawContext, length: number, width: number, fill: string) {
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.bezierCurveTo(length * 0.35, -width, length * 0.8, -width * 0.65, length, 0);
  ctx.bezierCurveTo(length * 0.7, width * 0.68, length * 0.25, width * 0.72, 0, 0);
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.strokeStyle = "rgba(228, 231, 184, .2)";
  ctx.lineWidth = 1;
  ctx.stroke();
}

function drawDecoration(ctx: DrawContext, item: Decoration) {
  ctx.save();
  ctx.translate(item.x, item.y);
  ctx.rotate(item.rotation);
  ctx.scale(item.scale, item.scale);
  if (item.kind === "grass") {
    ctx.strokeStyle = item.variant % 2 ? "#345947" : "#41614c";
    ctx.lineWidth = 1.4;
    for (let index = -2; index <= 2; index += 1) {
      ctx.beginPath();
      ctx.moveTo(index * 2, 5);
      ctx.quadraticCurveTo(index * 4, -4, index * 3 + (index % 2) * 5, -14 - Math.abs(index));
      ctx.stroke();
    }
  } else if (item.kind === "fern") {
    ctx.strokeStyle = "#50705a";
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(0, 7);
    ctx.quadraticCurveTo(2, -5, 0, -22);
    ctx.stroke();
    for (let y = -2; y > -20; y -= 4) {
      ctx.save();
      ctx.translate(0, y);
      drawLeaf(ctx, 8, 2.6, "#486b52");
      ctx.scale(-1, 1);
      drawLeaf(ctx, 7, 2.3, "#3d624a");
      ctx.restore();
    }
  } else if (item.kind === "stone") {
    ctx.fillStyle = item.variant % 2 ? "#344b43" : "#43564d";
    ctx.beginPath();
    ctx.ellipse(0, 1, 8, 5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgba(172, 195, 170, .16)";
    ctx.stroke();
  } else {
    ctx.strokeStyle = "#425f4c";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 7);
    ctx.lineTo(0, -14);
    ctx.stroke();
    for (const rotation of [-2.4, -0.8, 0.2, 1.6]) {
      ctx.save();
      ctx.translate(0, -7);
      ctx.rotate(rotation);
      drawLeaf(ctx, 10, 3.5, "#55725a");
      ctx.restore();
    }
  }
  ctx.restore();
}

function drawBackdrop(ctx: DrawContext, world: WorldState) {
  const night = Math.min(1, world.beat / 144);
  const gradient = ctx.createLinearGradient(0, 0, 0, WORLD_HEIGHT);
  gradient.addColorStop(0, night > 0.55 ? "#102a2b" : "#173936");
  gradient.addColorStop(0.52, night > 0.55 ? "#0e2522" : "#15332c");
  gradient.addColorStop(1, "#0a1c19");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, WORLD_WIDTH, WORLD_HEIGHT);

  ctx.save();
  ctx.globalAlpha = 0.22;
  ctx.fillStyle = "#759076";
  ctx.beginPath();
  ctx.ellipse(460, 365, 345, 178, -0.08, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  ctx.save();
  const pool = ctx.createRadialGradient(835, 123, 4, 835, 123, 120);
  pool.addColorStop(0, "rgba(67, 139, 135, .42)");
  pool.addColorStop(1, "rgba(20, 68, 66, .08)");
  ctx.fillStyle = pool;
  ctx.beginPath();
  ctx.ellipse(833, 126, 128, 72, -0.18, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(142, 200, 182, .16)";
  ctx.stroke();
  ctx.restore();

  ctx.save();
  ctx.strokeStyle = "rgba(165, 177, 128, .1)";
  ctx.lineWidth = 26;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(477, 620);
  ctx.bezierCurveTo(460, 530, 520, 471, 454, 405);
  ctx.bezierCurveTo(381, 332, 398, 242, 462, 176);
  ctx.stroke();
  ctx.restore();

  world.decorations.forEach((item) => drawDecoration(ctx, item));
}

function drawSignalOverlay(ctx: DrawContext, world: WorldState, overlay: Exclude<SignalOverlay, "none">) {
  const colors = {
    resource: [222, 192, 101],
    distress: [206, 89, 80],
    bond: [104, 205, 188],
  } as const;
  const [r, g, b] = colors[overlay];
  const cell = 32;
  ctx.save();
  for (let y = 64; y < WORLD_HEIGHT; y += cell) {
    for (let x = 0; x < WORLD_WIDTH; x += cell) {
      const value = signalAt(world, { x: x + cell / 2, y: y + cell / 2 }, overlay);
      if (value < 0.04) continue;
      ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${value * 0.3})`;
      ctx.fillRect(x, y, cell + 1, cell + 1);
    }
  }
  ctx.globalAlpha = 0.45;
  ctx.strokeStyle = `rgb(${r}, ${g}, ${b})`;
  ctx.setLineDash([3, 8]);
  ctx.lineWidth = 1;
  for (let y = 80; y < WORLD_HEIGHT; y += 64) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(WORLD_WIDTH, y);
    ctx.stroke();
  }
  ctx.restore();
}

function drawResource(ctx: DrawContext, world: WorldState, node: WorldState["resources"][number]) {
  ctx.save();
  ctx.translate(node.x, node.y);
  const pulse = 1 + Math.sin(world.beat * 0.28 + node.x) * 0.05;
  ctx.scale(pulse, pulse);
  const glow = ctx.createRadialGradient(0, 0, 3, 0, 0, 36);
  glow.addColorStop(0, `rgba(232, 211, 124, ${0.25 * node.vitality})`);
  glow.addColorStop(1, "rgba(232, 211, 124, 0)");
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(0, 0, 36, 0, Math.PI * 2);
  ctx.fill();
  if (node.kind === "dewbell") {
    for (let index = -2; index <= 2; index += 1) {
      ctx.strokeStyle = "#66866c";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(index * 7, 10);
      ctx.quadraticCurveTo(index * 6, -2, index * 8, -13 - Math.abs(index) * 2);
      ctx.stroke();
      ctx.fillStyle = index % 2 ? "#d6c36e" : "#a6c993";
      ctx.beginPath();
      ctx.ellipse(index * 8, -14 - Math.abs(index) * 2, 5, 7, index * 0.12, 0, Math.PI * 2);
      ctx.fill();
    }
  } else if (node.kind === "starcap") {
    for (let index = 0; index < 5; index += 1) {
      const angle = (Math.PI * 2 * index) / 5;
      ctx.save();
      ctx.rotate(angle);
      ctx.translate(9, 0);
      ctx.fillStyle = "#9dc2ac";
      ctx.beginPath();
      ctx.moveTo(-7, 4);
      ctx.lineTo(0, -9);
      ctx.lineTo(7, 4);
      ctx.quadraticCurveTo(0, 8, -7, 4);
      ctx.fill();
      ctx.restore();
    }
  } else {
    for (let index = -2; index <= 2; index += 1) {
      ctx.strokeStyle = "#5c7a5c";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(index * 6, 12);
      ctx.lineTo(index * 7, -15 + Math.abs(index) * 3);
      ctx.stroke();
      ctx.fillStyle = "#cf8a61";
      ctx.beginPath();
      ctx.ellipse(index * 7, -10 + Math.abs(index) * 3, 4, 7, 0.2 * index, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  ctx.fillStyle = "rgba(5, 17, 14, .55)";
  roundedRect(ctx, -19, 17, 38, 4, 2);
  ctx.fill();
  ctx.fillStyle = "#d8c97a";
  roundedRect(ctx, -19, 17, 38 * node.vitality, 4, 2);
  ctx.fill();
  ctx.restore();
}

function drawHazard(ctx: DrawContext, world: WorldState, hazard: WorldState["hazards"][number]) {
  ctx.save();
  ctx.translate(hazard.x, hazard.y);
  const breathe = 0.84 + Math.sin(world.beat * 0.22 + hazard.x) * 0.12;
  const glow = ctx.createRadialGradient(0, 0, 4, 0, 0, hazard.radius);
  glow.addColorStop(0, `rgba(193, 88, 77, ${0.21 * breathe})`);
  glow.addColorStop(1, "rgba(193, 88, 77, 0)");
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(0, 0, hazard.radius, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(210, 113, 91, .52)";
  ctx.lineWidth = 2;
  if (hazard.kind === "spore-knot") {
    for (let index = 0; index < 7; index += 1) {
      const angle = (Math.PI * 2 * index) / 7 + 0.2;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.quadraticCurveTo(Math.cos(angle + 0.5) * 18, Math.sin(angle + 0.5) * 18, Math.cos(angle) * 27, Math.sin(angle) * 27);
      ctx.stroke();
      ctx.fillStyle = "#925c4c";
      ctx.beginPath();
      ctx.arc(Math.cos(angle) * 27, Math.sin(angle) * 27, 3, 0, Math.PI * 2);
      ctx.fill();
    }
  } else {
    for (let index = 0; index < 6; index += 1) {
      ctx.save();
      ctx.rotate((Math.PI * 2 * index) / 6);
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(30, -5);
      ctx.lineTo(21, 4);
      ctx.stroke();
      ctx.restore();
    }
  }
  ctx.restore();
}

function drawBrambleback(ctx: DrawContext, agent: Agent, bob: number) {
  ctx.save();
  ctx.translate(0, bob);
  ctx.fillStyle = "rgba(4, 11, 9, .45)";
  ctx.beginPath();
  ctx.ellipse(-2, 15, 33, 9, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "#263e30";
  ctx.lineWidth = 6;
  ctx.lineCap = "round";
  for (const legX of [-19, -6, 10, 23]) {
    ctx.beginPath();
    ctx.moveTo(legX, 8);
    ctx.lineTo(legX - 2, 20);
    ctx.stroke();
  }
  ctx.fillStyle = agent.color;
  ctx.beginPath();
  ctx.ellipse(0, 0, 34, 20, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(222, 231, 190, .25)";
  ctx.lineWidth = 1.4;
  ctx.stroke();
  for (let index = -2; index <= 2; index += 1) {
    ctx.save();
    ctx.translate(index * 10 - 2, -12 - (2 - Math.abs(index)) * 2);
    ctx.rotate(-1.35 + index * 0.08);
    drawLeaf(ctx, 20, 6, index % 2 ? agent.accent : "#6d8258");
    ctx.restore();
  }
  ctx.fillStyle = agent.color;
  ctx.beginPath();
  ctx.ellipse(31, -3, 15, 13, -0.18, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = agent.accent;
  ctx.beginPath();
  ctx.moveTo(29, -14);
  ctx.lineTo(33, -27);
  ctx.lineTo(38, -12);
  ctx.fill();
  ctx.fillStyle = "#13231b";
  ctx.beginPath();
  ctx.arc(38, -6, 2.3, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = agent.accent;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(-31, 0);
  ctx.quadraticCurveTo(-43, -10, -47, -1);
  ctx.stroke();
  ctx.restore();
}

function drawWickwing(ctx: DrawContext, agent: Agent, bob: number) {
  ctx.save();
  ctx.translate(0, bob - 6);
  const glow = ctx.createRadialGradient(0, 0, 2, 0, 0, 37);
  glow.addColorStop(0, `${agent.accent}66`);
  glow.addColorStop(1, `${agent.accent}00`);
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(0, 0, 37, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = `${agent.color}c9`;
  for (const side of [-1, 1]) {
    ctx.save();
    ctx.scale(1, side);
    ctx.beginPath();
    ctx.moveTo(-3, -2);
    ctx.bezierCurveTo(-18, -31, -44, -29, -39, -4);
    ctx.bezierCurveTo(-26, 8, -11, 7, -3, 2);
    ctx.fill();
    ctx.strokeStyle = "rgba(218, 230, 225, .3)";
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.restore();
  }
  ctx.fillStyle = "#263d42";
  ctx.beginPath();
  ctx.ellipse(5, 0, 18, 10, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = agent.accent;
  ctx.beginPath();
  ctx.ellipse(1, 0, 7, 6, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = agent.color;
  ctx.beginPath();
  ctx.arc(21, -2, 8, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#edf0cf";
  ctx.beginPath();
  ctx.arc(24, -4, 1.8, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = agent.accent;
  ctx.lineWidth = 1.5;
  for (const bend of [-1, 1]) {
    ctx.beginPath();
    ctx.moveTo(20, -8);
    ctx.quadraticCurveTo(26, -20, 31, -17 + bend * 3);
    ctx.stroke();
  }
  ctx.restore();
}

function drawMirehorn(ctx: DrawContext, agent: Agent, bob: number) {
  ctx.save();
  ctx.translate(0, bob);
  ctx.fillStyle = "rgba(4, 11, 9, .45)";
  ctx.beginPath();
  ctx.ellipse(-2, 15, 32, 9, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = agent.color;
  ctx.lineWidth = 11;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(-23, 4);
  ctx.quadraticCurveTo(-42, 12, -48, 1);
  ctx.stroke();
  ctx.fillStyle = agent.color;
  ctx.beginPath();
  ctx.ellipse(0, 2, 31, 18, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = `${agent.accent}55`;
  ctx.beginPath();
  ctx.ellipse(-5, 5, 21, 10, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = agent.color;
  ctx.beginPath();
  ctx.ellipse(27, -3, 15, 13, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = agent.accent;
  ctx.lineWidth = 2.6;
  for (const y of [-9, 2]) {
    ctx.beginPath();
    ctx.moveTo(28, y);
    ctx.bezierCurveTo(33, y - 18, 49, y - 11, 43, y + 1);
    ctx.bezierCurveTo(39, y + 8, 34, y + 3, 38, y - 1);
    ctx.stroke();
  }
  ctx.fillStyle = "#edf0cf";
  ctx.beginPath();
  ctx.arc(33, -6, 2, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "#315f59";
  ctx.lineWidth = 5;
  for (const legX of [-16, 13]) {
    ctx.beginPath();
    ctx.moveTo(legX, 11);
    ctx.lineTo(legX + 3, 21);
    ctx.stroke();
  }
  ctx.restore();
}

function drawAgent(ctx: DrawContext, world: WorldState, agent: Agent, selected: boolean, hovered: boolean) {
  ctx.save();
  ctx.translate(agent.x, agent.y);
  ctx.rotate(agent.angle);
  if (selected || hovered) {
    ctx.strokeStyle = selected ? "#f4d992" : "rgba(244, 217, 146, .55)";
    ctx.lineWidth = selected ? 2 : 1;
    ctx.setLineDash(selected ? [4, 5] : [2, 6]);
    ctx.beginPath();
    ctx.ellipse(0, 4, 54, 38, 0, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]);
  }
  const bob = Math.sin(world.beat * 0.45 + agent.x) * (agent.species === "wickwing" ? 4 : 1.5);
  if (agent.species === "brambleback") drawBrambleback(ctx, agent, bob);
  if (agent.species === "wickwing") drawWickwing(ctx, agent, bob);
  if (agent.species === "mirehorn") drawMirehorn(ctx, agent, bob);
  ctx.restore();

  ctx.save();
  ctx.font = "600 12px ui-sans-serif, system-ui";
  ctx.textAlign = "center";
  const width = ctx.measureText(agent.name).width + 18;
  ctx.fillStyle = "rgba(7, 23, 19, .78)";
  roundedRect(ctx, agent.x - width / 2, agent.y - 54, width, 24, 12);
  ctx.fill();
  ctx.fillStyle = "#e9e5c8";
  ctx.fillText(agent.name, agent.x, agent.y - 38);
  ctx.restore();
}

function drawObserver(ctx: DrawContext, world: WorldState) {
  ctx.save();
  const glow = ctx.createRadialGradient(world.observer.x, world.observer.y, 4, world.observer.x, world.observer.y, OBSERVATION_RADIUS);
  glow.addColorStop(0, "rgba(246, 219, 142, .12)");
  glow.addColorStop(0.6, "rgba(246, 219, 142, .045)");
  glow.addColorStop(1, "rgba(246, 219, 142, 0)");
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(world.observer.x, world.observer.y, OBSERVATION_RADIUS, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(246, 219, 142, .22)";
  ctx.setLineDash([4, 9]);
  ctx.beginPath();
  ctx.arc(world.observer.x, world.observer.y, OBSERVATION_RADIUS, 0, Math.PI * 2);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.translate(world.observer.x, world.observer.y);
  ctx.fillStyle = "rgba(6, 18, 15, .7)";
  ctx.beginPath();
  ctx.ellipse(0, 12, 20, 7, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "#d7bd76";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(0, -4, 11, Math.PI, 0);
  ctx.stroke();
  ctx.fillStyle = "#e9cb72";
  roundedRect(ctx, -9, -5, 18, 24, 5);
  ctx.fill();
  ctx.fillStyle = "#fff0ad";
  roundedRect(ctx, -4, 0, 8, 13, 3);
  ctx.fill();
  ctx.restore();
}

function drawTopBand(ctx: DrawContext, world: WorldState, overlay: SignalOverlay) {
  const dusk = Math.min(1, world.beat / 144);
  ctx.save();
  const sky = ctx.createLinearGradient(0, 0, WORLD_WIDTH, 0);
  sky.addColorStop(0, "rgba(8, 25, 22, .94)");
  sky.addColorStop(0.6, `rgba(${19 + dusk * 10}, ${45 - dusk * 8}, ${41 + dusk * 15}, .94)`);
  sky.addColorStop(1, "rgba(8, 25, 22, .94)");
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, WORLD_WIDTH, 64);
  ctx.fillStyle = "#d9d4b5";
  ctx.font = "600 13px ui-sans-serif, system-ui";
  ctx.fillText(`FIELD BEAT ${String(world.beat).padStart(3, "0")} / 144`, 22, 27);
  ctx.fillStyle = "rgba(217, 212, 181, .56)";
  ctx.font = "11px ui-sans-serif, system-ui";
  ctx.fillText(overlay === "none" ? "PLAYABLE VIEW · SIGNALS HIDDEN" : `${overlay.toUpperCase()} FIELD · LAB VIEW`, 22, 46);
  const timeLabel = world.beat < 48 ? "LATE AFTERNOON" : world.beat < 100 ? "BLUE DUSK" : "FIRST NIGHT";
  ctx.textAlign = "right";
  ctx.fillStyle = "#d9d4b5";
  ctx.fillText(timeLabel, WORLD_WIDTH - 22, 28);
  ctx.fillStyle = "rgba(217, 212, 181, .5)";
  ctx.fillText("CLICK GROUND TO MOVE · CLICK CREATURE TO READ", WORLD_WIDTH - 22, 47);
  ctx.restore();
}

export function drawWorld(
  ctx: DrawContext,
  world: WorldState,
  selectedId: string | null,
  hoveredId: string | null,
  overlay: SignalOverlay,
) {
  ctx.clearRect(0, 0, WORLD_WIDTH, WORLD_HEIGHT);
  drawBackdrop(ctx, world);
  if (overlay !== "none") drawSignalOverlay(ctx, world, overlay);
  world.hazards.forEach((hazard) => drawHazard(ctx, world, hazard));
  world.resources.forEach((node) => drawResource(ctx, world, node));
  drawObserver(ctx, world);
  [...world.agents]
    .sort((a, b) => a.y - b.y)
    .forEach((agent) => drawAgent(ctx, world, agent, selectedId === agent.id, hoveredId === agent.id));
  drawTopBand(ctx, world, overlay);
}

export function canvasPoint(canvas: HTMLCanvasElement, clientX: number, clientY: number): Point {
  const rect = canvas.getBoundingClientRect();
  return {
    x: ((clientX - rect.left) / rect.width) * WORLD_WIDTH,
    y: ((clientY - rect.top) / rect.height) * WORLD_HEIGHT,
  };
}

export function agentAtPoint(world: WorldState, point: Point) {
  return [...world.agents]
    .map((agent) => ({ agent, distance: Math.hypot(agent.x - point.x, agent.y - point.y) }))
    .sort((a, b) => a.distance - b.distance)
    .find((entry) => entry.distance < 45)?.agent ?? null;
}
