const canvas = document.getElementById("wheel");
const ctx = canvas.getContext("2d");

const prizes = [0.1, 0.2, 0.5, 0.1, 0.3, 0.7, 0.1, 1.0]; // مقادیر TON
const colors = ["#FF5733", "#33FF57", "#3357FF", "#F1C40F", "#9B59B6", "#1ABC9C", "#E67E22", "#2ECC71"];
let angle = 0;
let spinning = false;

function drawWheel() {
  const radius = canvas.width / 2;
  const segmentAngle = (2 * Math.PI) / prizes.length;

  for (let i = 0; i < prizes.length; i++) {
    ctx.beginPath();
    ctx.moveTo(radius, radius);
    ctx.fillStyle = colors[i % colors.length];
    ctx.arc(radius, radius, radius, angle + i * segmentAngle, angle + (i + 1) * segmentAngle);
    ctx.lineTo(radius, radius);
    ctx.fill();

    ctx.save();
    ctx.translate(radius, radius);
    ctx.rotate(angle + (i + 0.5) * segmentAngle);
    ctx.textAlign = "right";
    ctx.fillStyle = "#fff";
    ctx.font = "bold 16px Arial";
    ctx.fillText(prizes[i].toFixed(1) + " TON", radius - 10, 5);
    ctx.restore();
  }
}

function spinWheel() {
  if (spinning) return;
  spinning = true;

  const randomIndex = Math.floor(Math.random() * prizes.length);
  const selectedPrize = prizes[randomIndex];

  const extraSpins = 5;
  const targetIndex = randomIndex;
  const totalAngle = (extraSpins * 360) + (360 / prizes.length) * (prizes.length - targetIndex - 0.5);

  let currentAngle = 0;
  const duration = 4000;
  const start = performance.now();

  function animate(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const easeOutCubic = 1 - Math.pow(1 - progress, 3);

    angle = (totalAngle * easeOutCubic) * Math.PI / 180;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawWheel();

    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      spinning = false;
      document.getElementById("result").innerText = `🎉 شما ${selectedPrize.toFixed(1)} TON برنده شدید!`;
      fetch('/spin', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ user_id: {{ user_id }}, prize: selectedPrize })
      });
    }
  }

  requestAnimationFrame(animate);
}

drawWheel();