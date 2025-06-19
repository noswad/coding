// Game configuration
const config = {
    type: Phaser.AUTO,
    width: 640,
    height: 640,
    parent: 'game',
    backgroundColor: '#222',
    physics: {
        default: 'matter',
        matter: {
            gravity: { x: 0, y: 1 },
            debug: true
        }
    },
    scene: { preload, create, update }
};

const tileSize = 64;
// 10x10 grid: 0 empty, 1 wall, 2 target
const mapData = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,2,1],
    [1,1,1,1,1,1,1,1,1,1]
];

let player;
let enemyBlock;
let obstacles = [];
let target;
let lastGravity = 'down';
let enemyPrediction = 'right';
let rightStreak = 0;
const gravityDirText = document.getElementById('gravityDir');

function preload() {
    // No external assets needed
}

function create() {
    const graphics = this.add.graphics();
    graphics.fillStyle(0x666666, 1);

    // Build map
    for (let row = 0; row < 10; row++) {
        for (let col = 0; col < 10; col++) {
            const value = mapData[row][col];
            const x = col * tileSize + tileSize / 2;
            const y = row * tileSize + tileSize / 2;

            if (value === 1) {
                // Static wall
                const wall = this.matter.add.rectangle(x, y, tileSize, tileSize, { isStatic: true });
                graphics.fillRect(col * tileSize, row * tileSize, tileSize, tileSize);
                obstacles.push(wall);
            } else if (value === 2) {
                // Target location
                target = this.add.rectangle(x, y, tileSize, tileSize, 0x00ff00);
                this.matter.add.gameObject(target, { isStatic: true });
            }
        }
    }

    // Player ball
    player = this.matter.add.circle(tileSize * 1.5, tileSize * 1.5, tileSize / 4, { restitution: 0.1 });
    this.add.existing(player);

    // Enemy block (static red block)
    enemyBlock = this.matter.add.rectangle(tileSize * 5.5, tileSize * 5.5, tileSize, tileSize, { isStatic: true });
    this.add.rectangle(tileSize * 5.5, tileSize * 5.5, tileSize, tileSize, 0xff0000);

    // Keyboard input
    this.input.keyboard.on('keydown', handleInput, this);
}

function update() {
    // Check win condition
    if (Phaser.Math.Distance.Between(player.position.x, player.position.y, target.x, target.y) < tileSize / 2) {
        gravityDirText.textContent = 'Win!';
        this.scene.pause();
    }
}

function handleInput(event) {
    const gravity = this.matter.world.gravity;
    switch (event.code) {
        case 'ArrowUp':
            gravity.x = 0; gravity.y = -1; lastGravity = 'up';
            break;
        case 'ArrowDown':
            gravity.x = 0; gravity.y = 1; lastGravity = 'down';
            break;
        case 'ArrowLeft':
            gravity.x = -1; gravity.y = 0; lastGravity = 'left';
            break;
        case 'ArrowRight':
            gravity.x = 1; gravity.y = 0; lastGravity = 'right';
            rightStreak++;
            break;
        case 'Space':
            enemyMove.call(this);
            break;
        default:
            return;
    }
    gravityDirText.textContent = lastGravity;

    // Very simple predictive behavior
    if (lastGravity === 'right' && rightStreak >= 2) {
        enemyPrediction = 'right';
        enemyMove.call(this);
        rightStreak = 0;
    }
}

function enemyMove() {
    // If prediction is right, place obstacle to the right of player
    if (enemyPrediction === 'right') {
        const x = player.position.x + tileSize;
        const y = player.position.y;
        const obstacle = this.matter.add.rectangle(x, y, tileSize, tileSize, { isStatic: true });
        this.add.rectangle(x, y, tileSize, tileSize, 0x880000);
        obstacles.push(obstacle);
        enemyPrediction = null;
        this.add.text(10, 610, 'Enemy blocks right!', { fontSize: '16px', fill: '#fff' });
    }
}

new Phaser.Game(config);
