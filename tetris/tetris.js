// === TETRIS ENGINE ===

const COLS = 10;
const ROWS = 20;
const BLOCK = 30; // px per cell on main canvas

// Tetromino shapes
const TETROMINOES = {
  I: { shape: [[1,1,1,1]], color: '#22d3ee' },
  J: { shape: [[1,0,0],[1,1,1]], color: '#60a5fa' },
  L: { shape: [[0,0,1],[1,1,1]], color: '#fb923c' },
  O: { shape: [[1,1],[1,1]], color: '#facc15' },
  S: { shape: [[0,1,1],[1,1,0]], color: '#34d399' },
  T: { shape: [[0,1,0],[1,1,1]], color: '#a78bfa' },
  Z: { shape: [[1,1,0],[0,1,1]], color: '#f472b6' },
};

const SCORE_TABLE = { 1: 100, 2: 300, 3: 500, 4: 800 };
const LEVEL_SPEED = (level) => Math.max(80, 800 - (level - 1) * 70); // ms per drop

// === STATE ===
let board, currentPiece, nextPiece, holdPiece, canHold;
let score, best, level, lines;
let dropTimer, lastTime, animFrame;
let gameRunning, gamePaused;
let lineFlashRows = [];
let lineFlashFrame = 0;
let particles = [];
let scorePopTimer = 0;

// === CANVAS SETUP ===
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const nextCanvas = document.getElementById('nextCanvas');
const nextCtx = nextCanvas.getContext('2d');
const holdCanvas = document.getElementById('holdCanvas');
const holdCtx = holdCanvas.getContext('2d');

// === HELPERS ===
function randomPiece() {
  const keys = Object.keys(TETROMINOES);
  const key = keys[Math.floor(Math.random() * keys.length)];
  const t = TETROMINOES[key];
  return {
    shape: t.shape.map(r => [...r]),
    color: t.color,
    x: Math.floor((COLS - t.shape[0].length) / 2),
    y: 0,
  };
}

function rotate(shape) {
  const rows = shape.length, cols = shape[0].length;
  const rotated = Array.from({ length: cols }, () => Array(rows).fill(0));
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++)
      rotated[c][rows - 1 - r] = shape[r][c];
  return rotated;
}

function isValid(shape, ox, oy) {
  for (let r = 0; r < shape.length; r++)
    for (let c = 0; c < shape[r].length; c++)
      if (shape[r][c]) {
        const nx = ox + c, ny = oy + r;
        if (nx < 0 || nx >= COLS || ny >= ROWS) return false;
        if (ny >= 0 && board[ny][nx]) return false;
      }
  return true;
}

function place(piece) {
  for (let r = 0; r < piece.shape.length; r++)
    for (let c = 0; c < piece.shape[r].length; c++)
      if (piece.shape[r][c] && piece.y + r >= 0)
        board[piece.y + r][piece.x + c] = piece.color;
}

function clearLines() {
  const full = [];
  for (let r = 0; r < ROWS; r++)
    if (board[r].every(c => c)) full.push(r);

  if (!full.length) return 0;

  // flash effect
  lineFlashRows = full;
  lineFlashFrame = 8;

  // spawn particles on cleared lines
  for (const row of full) {
    for (let c = 0; c < COLS; c++) {
      const color = board[row][c] || '#fff';
      spawnParticles(c * BLOCK + BLOCK / 2, row * BLOCK + BLOCK / 2, color, 4);
    }
  }

  // remove rows
  for (const row of full) {
    board.splice(row, 1);
    board.unshift(Array(COLS).fill(0));
  }

  return full.length;
}

// === PARTICLES ===
function spawnParticles(x, y, color, count) {
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 2 + Math.random() * 4;
    particles.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 2,
      color,
      alpha: 1,
      size: 3 + Math.random() * 4,
      life: 30 + Math.random() * 20,
    });
  }
}

function updateParticles() {
  particles = particles.filter(p => p.life > 0);
  for (const p of particles) {
    p.x += p.vx; p.y += p.vy;
    p.vy += 0.3; // gravity
    p.alpha = p.life / 50;
    p.life--;
  }
}

function drawParticles() {
  for (const p of particles) {
    ctx.save();
    ctx.globalAlpha = Math.max(0, p.alpha);
    ctx.fillStyle = p.color;
    ctx.shadowColor = p.color;
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

// === GHOST PIECE ===
function getGhostY() {
  let gy = currentPiece.y;
  while (isValid(currentPiece.shape, currentPiece.x, gy + 1)) gy++;
  return gy;
}

// === DRAW FUNCTIONS ===
function drawBlock(ctx, x, y, color, size = BLOCK, alpha = 1) {
  const pad = 2;
  ctx.save();
  ctx.globalAlpha = alpha;
  // Main fill with gradient
  const grad = ctx.createLinearGradient(x * size + pad, y * size + pad, x * size + size - pad, y * size + size - pad);
  grad.addColorStop(0, lighten(color, 40));
  grad.addColorStop(1, color);
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.roundRect(x * size + pad, y * size + pad, size - pad * 2, size - pad * 2, 4);
  ctx.fill();
  // Glow
  ctx.shadowColor = color;
  ctx.shadowBlur = 10;
  ctx.strokeStyle = lighten(color, 60);
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.restore();
}

function lighten(hex, amount) {
  let r = parseInt(hex.slice(1, 3), 16);
  let g = parseInt(hex.slice(3, 5), 16);
  let b = parseInt(hex.slice(5, 7), 16);
  r = Math.min(255, r + amount);
  g = Math.min(255, g + amount);
  b = Math.min(255, b + amount);
  return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`;
}

function drawGrid() {
  ctx.save();
  ctx.strokeStyle = 'rgba(255,255,255,0.03)';
  ctx.lineWidth = 1;
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      ctx.strokeRect(c * BLOCK, r * BLOCK, BLOCK, BLOCK);
    }
  }
  ctx.restore();
}

function drawBoard() {
  for (let r = 0; r < ROWS; r++) {
    const isFlash = lineFlashRows.includes(r) && lineFlashFrame > 0;
    for (let c = 0; c < COLS; c++) {
      if (board[r][c]) {
        const alpha = isFlash ? (lineFlashFrame % 2 === 0 ? 1 : 0.3) : 1;
        drawBlock(ctx, c, r, board[r][c], BLOCK, alpha);
      }
    }
  }
}

function drawCurrentPiece() {
  if (!currentPiece) return;
  // Ghost
  const gy = getGhostY();
  for (let r = 0; r < currentPiece.shape.length; r++)
    for (let c = 0; c < currentPiece.shape[r].length; c++)
      if (currentPiece.shape[r][c])
        drawBlock(ctx, currentPiece.x + c, gy + r, currentPiece.color, BLOCK, 0.2);
  // Actual
  for (let r = 0; r < currentPiece.shape.length; r++)
    for (let c = 0; c < currentPiece.shape[r].length; c++)
      if (currentPiece.shape[r][c])
        drawBlock(ctx, currentPiece.x + c, currentPiece.y + r, currentPiece.color);
}

function drawPreview(pCtx, piece, canvasSize) {
  pCtx.clearRect(0, 0, canvasSize, canvasSize);
  if (!piece) return;
  const rows = piece.shape.length, cols = piece.shape[0].length;
  const blockSize = Math.min(Math.floor((canvasSize - 20) / Math.max(rows, cols)), 28);
  const ox = Math.floor((canvasSize - cols * blockSize) / 2) / blockSize;
  const oy = Math.floor((canvasSize - rows * blockSize) / 2) / blockSize;
  for (let r = 0; r < rows; r++)
    for (let c = 0; c < cols; c++)
      if (piece.shape[r][c])
        drawBlock(pCtx, ox + c, oy + r, piece.color, blockSize);
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  drawBoard();
  drawCurrentPiece();
  drawParticles();
}

// === GAME LOGIC ===
function initBoard() {
  board = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
}

function spawnPiece() {
  currentPiece = nextPiece || randomPiece();
  nextPiece = randomPiece();
  canHold = true;

  drawPreview(nextCtx, nextPiece, 120);

  if (!isValid(currentPiece.shape, currentPiece.x, currentPiece.y)) {
    endGame();
  }
}

function lockPiece() {
  place(currentPiece);
  const cleared = clearLines();
  if (cleared > 0) {
    const gained = (SCORE_TABLE[cleared] || 0) * level;
    score += gained;
    lines += cleared;
    const newLevel = Math.floor(lines / 10) + 1;
    if (newLevel > level) level = newLevel;
    updateUI();
    triggerScorePop();
  }
  spawnPiece();
}

function softDrop() {
  if (isValid(currentPiece.shape, currentPiece.x, currentPiece.y + 1)) {
    currentPiece.y++;
    score += 1;
    updateScoreDisplay();
  } else {
    lockPiece();
  }
}

function hardDrop() {
  const gy = getGhostY();
  const dist = gy - currentPiece.y;
  score += dist * 2;
  currentPiece.y = gy;
  spawnParticles(
    (currentPiece.x + currentPiece.shape[0].length / 2) * BLOCK,
    (currentPiece.y + currentPiece.shape.length) * BLOCK,
    currentPiece.color, 10
  );
  lockPiece();
  updateScoreDisplay();
}

function hold() {
  if (!canHold) return;
  if (holdPiece) {
    const tmp = holdPiece;
    holdPiece = { shape: TETROMINOES[getPieceKey(currentPiece)].shape.map(r=>[...r]), color: currentPiece.color };
    currentPiece = { ...tmp, x: Math.floor((COLS - tmp.shape[0].length) / 2), y: 0 };
  } else {
    holdPiece = { shape: TETROMINOES[getPieceKey(currentPiece)].shape.map(r=>[...r]), color: currentPiece.color };
    spawnPiece();
  }
  drawPreview(holdCtx, holdPiece, 120);
  canHold = false;
}

function getPieceKey(piece) {
  const c = piece.color;
  return Object.keys(TETROMINOES).find(k => TETROMINOES[k].color === c) || 'T';
}

// === GAME LOOP ===
let accumulator = 0;

function gameLoop(timestamp) {
  if (!gameRunning || gamePaused) return;
  if (!lastTime) lastTime = timestamp;
  const delta = timestamp - lastTime;
  lastTime = timestamp;

  if (lineFlashFrame > 0) lineFlashFrame--;
  updateParticles();

  accumulator += delta;
  const speed = LEVEL_SPEED(level);
  if (accumulator >= speed) {
    accumulator = 0;
    if (!lineFlashFrame) {
      if (isValid(currentPiece.shape, currentPiece.x, currentPiece.y + 1)) {
        currentPiece.y++;
      } else {
        lockPiece();
      }
    }
  }

  render();
  drawPreview(nextCtx, nextPiece, 120);
  drawPreview(holdCtx, holdPiece, 120);

  animFrame = requestAnimationFrame(gameLoop);
}

// === UI UPDATES ===
function updateUI() {
  updateScoreDisplay();
  document.getElementById('levelDisplay').textContent = level;
  document.getElementById('linesDisplay').textContent = lines;
  const linesInLevel = lines % 10;
  document.getElementById('linesLeft').textContent = 10 - linesInLevel;
  document.getElementById('levelBar').style.width = (linesInLevel * 10) + '%';

  if (score > best) {
    best = score;
    localStorage.setItem('tetris_best', best);
    document.getElementById('bestDisplay').textContent = best;
  }
}

function updateScoreDisplay() {
  document.getElementById('scoreDisplay').textContent = score;
}

function triggerScorePop() {
  const el = document.getElementById('scoreDisplay');
  el.classList.remove('score-pop');
  void el.offsetWidth;
  el.classList.add('score-pop');
}

// === GAME START / END ===
function startGame() {
  initBoard();
  score = 0; level = 1; lines = 0;
  holdPiece = null; lineFlashRows = []; particles = [];
  accumulator = 0; lastTime = 0;
  gameRunning = true; gamePaused = false;

  document.getElementById('startOverlay').classList.add('hidden');
  document.getElementById('gameOverOverlay').classList.add('hidden');
  document.getElementById('pauseOverlay').classList.add('hidden');

  updateUI();
  holdCtx.clearRect(0, 0, 120, 120);
  nextPiece = randomPiece();
  spawnPiece();

  cancelAnimationFrame(animFrame);
  animFrame = requestAnimationFrame(gameLoop);
}

function endGame() {
  gameRunning = false;
  cancelAnimationFrame(animFrame);
  document.getElementById('finalScore').textContent = '점수: ' + score;
  document.getElementById('gameOverOverlay').classList.remove('hidden');
  if (score > best) {
    best = score;
    localStorage.setItem('tetris_best', best);
    document.getElementById('bestDisplay').textContent = best;
  }
}

function togglePause() {
  if (!gameRunning) return;
  gamePaused = !gamePaused;
  if (gamePaused) {
    document.getElementById('pauseOverlay').classList.remove('hidden');
    cancelAnimationFrame(animFrame);
  } else {
    document.getElementById('pauseOverlay').classList.add('hidden');
    lastTime = 0;
    animFrame = requestAnimationFrame(gameLoop);
  }
}

// === INPUT ===
document.addEventListener('keydown', (e) => {
  if (!gameRunning || gamePaused) {
    if (e.code === 'KeyP') togglePause();
    return;
  }
  switch (e.code) {
    case 'ArrowLeft':
      e.preventDefault();
      if (isValid(currentPiece.shape, currentPiece.x - 1, currentPiece.y)) currentPiece.x--;
      break;
    case 'ArrowRight':
      e.preventDefault();
      if (isValid(currentPiece.shape, currentPiece.x + 1, currentPiece.y)) currentPiece.x++;
      break;
    case 'ArrowDown':
      e.preventDefault();
      softDrop();
      break;
    case 'ArrowUp':
    case 'KeyX':
      e.preventDefault();
      {
        const r = rotate(currentPiece.shape);
        // wall kick attempts
        const kicks = [0, -1, 1, -2, 2];
        for (const kick of kicks) {
          if (isValid(r, currentPiece.x + kick, currentPiece.y)) {
            currentPiece.shape = r;
            currentPiece.x += kick;
            break;
          }
        }
      }
      break;
    case 'Space':
      e.preventDefault();
      hardDrop();
      break;
    case 'KeyC':
      e.preventDefault();
      hold();
      break;
    case 'KeyP':
    case 'Escape':
      e.preventDefault();
      togglePause();
      break;
  }
});

// === TOUCH CONTROLS (mobile swipe) ===
let touchStartX = 0, touchStartY = 0;
canvas.addEventListener('touchstart', e => {
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
}, { passive: true });
canvas.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - touchStartX;
  const dy = e.changedTouches[0].clientY - touchStartY;
  const absDx = Math.abs(dx), absDy = Math.abs(dy);
  if (absDx < 10 && absDy < 10) {
    // tap → rotate
    const r = rotate(currentPiece.shape);
    const kicks = [0, -1, 1, -2, 2];
    for (const kick of kicks) {
      if (isValid(r, currentPiece.x + kick, currentPiece.y)) {
        currentPiece.shape = r; currentPiece.x += kick; break;
      }
    }
  } else if (absDx > absDy) {
    if (dx > 20 && isValid(currentPiece.shape, currentPiece.x + 1, currentPiece.y)) currentPiece.x++;
    else if (dx < -20 && isValid(currentPiece.shape, currentPiece.x - 1, currentPiece.y)) currentPiece.x--;
  } else {
    if (dy > 20) hardDrop();
  }
}, { passive: true });

// === BUTTONS ===
document.getElementById('startBtn').addEventListener('click', startGame);
document.getElementById('resumeBtn').addEventListener('click', togglePause);
document.getElementById('restartBtn').addEventListener('click', startGame);

// === LOAD BEST SCORE ===
best = parseInt(localStorage.getItem('tetris_best') || '0');
document.getElementById('bestDisplay').textContent = best;

// === INITIAL RENDER (draw empty board) ===
initBoard();
render();
