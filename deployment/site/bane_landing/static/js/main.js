document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('initiate-btn');
    const overlay = document.getElementById('hacker-overlay');
    const wrapper = document.getElementById('main-wrapper');
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');  // Corrected context

    // --- Matrix Rain Logic ---
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    let columns = width / 20;
    let drops = [];
    for (let i = 0; i < columns; i++) drops[i] = 1;

    function drawMatrix() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = '#0f0';
        ctx.font = '15px monospace';

        for (let i = 0; i < drops.length; i++) {
            let text = String.fromCharCode(Math.floor(Math.random() * 128));
            ctx.fillText(text, i * 20, drops[i] * 20);
            if (drops[i] * 20 > height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        }
    }
    // -------------------------

    // --- Audio Glitch Logic ---
    function playGlitchSound() {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;

        const actx = new AudioContext();
        const osc = actx.createOscillator();
        const gain = actx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(100, actx.currentTime);

        // Random frequency modulation for glitch effect
        for (let i = 0; i < 30; i++) {
            osc.frequency.setValueAtTime(Math.random() * 800 + 100, actx.currentTime + (i * 0.05));
        }

        gain.gain.setValueAtTime(0.1, actx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, actx.currentTime + 1.5);

        osc.connect(gain);
        gain.connect(actx.destination);

        osc.start();
        osc.stop(actx.currentTime + 1.5);
    }
    // -------------------------

    btn.addEventListener('click', () => {
        // 0. Play Sound
        playGlitchSound();

        // 1. Shake Screen
        document.body.classList.add('shake-hard');

        // 2. Glitch Text
        document.querySelector('h1').dataset.text = "SYSTEM BREACH";
        document.querySelector('h1').innerText = "SYSTEM BREACH";
        document.querySelector('.subtitle').innerText = "UNAUTHORIZED ACCESS DETECTED";

        // 3. Delay then Overlay
        setTimeout(() => {
            wrapper.style.display = 'none'; // Hide main content
            overlay.classList.remove('hidden'); // Show Matrix
            document.body.classList.remove('shake-hard'); // Stop shaking

            // Start Matrix Loop
            setInterval(drawMatrix, 50);

            // 4. Redirect
            setTimeout(() => {
                window.location.href = "https://github.com/Jayson056/BANE-ASSISTANT-CORE";
            }, 3000); // 3 seconds of matrix

        }, 1500); // 1.5 seconds of shaking
    });
});
