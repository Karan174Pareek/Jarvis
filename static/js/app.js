// JARVIS OS - Mission Control HUD Client Script

document.addEventListener('DOMContentLoaded', () => {
    initShaderCanvas();
    initOrbCanvas();
    startClock();
    startTelemetryPolling();
    appendTerminal('SYSTEM', 'Jarvis Mission Control HUD initialized. Connection ready.');
});

// --- WebGL Background Shader ---
function initShaderCanvas() {
    const canvas = document.getElementById('shader-canvas');
    if (!canvas) return;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return;

    const vsSource = `
        attribute vec2 a_position;
        varying vec2 v_uv;
        void main() {
            v_uv = a_position * 0.5 + 0.5;
            gl_Position = vec4(a_position, 0.0, 1.0);
        }
    `;

    const fsSource = `
        precision highp float;
        varying vec2 v_uv;
        uniform float u_time;
        uniform vec2 u_resolution;

        float hexGrid(vec2 p) {
            p *= 12.0;
            vec2 r = vec2(1.0, 1.732);
            vec2 h = r * 0.5;
            vec2 a = mod(p, r) - h;
            vec2 b = mod(p - h, r) - h;
            vec2 g = dot(a, a) < dot(b, b) ? a : b;
            return 0.08 / (length(g) + 0.08);
        }

        void main() {
            vec2 centered = (v_uv - 0.5) * (u_resolution.x / u_resolution.y);
            vec3 color = vec3(0.02, 0.04, 0.06);
            
            float hex = hexGrid(centered + u_time * 0.015);
            color += hex * 0.035 * vec3(0.24, 0.84, 1.0);

            // Subtle scan highlights
            float scan = sin(v_uv.y * 600.0 + u_time * 4.0) * 0.015;
            color += scan * vec3(0.24, 0.84, 1.0);

            // Vignette
            float d = length(centered);
            color *= 1.0 - smoothstep(0.4, 1.4, d);

            gl_FragColor = vec4(color, 1.0);
        }
    `;

    function createShader(gl, type, source) {
        const s = gl.createShader(type);
        gl.shaderSource(s, source);
        gl.compileShader(s);
        return s;
    }

    const program = gl.createProgram();
    gl.attachShader(program, createShader(gl, gl.VERTEX_SHADER, vsSource));
    gl.attachShader(program, createShader(gl, gl.FRAGMENT_SHADER, fsSource));
    gl.linkProgram(program);
    gl.useProgram(program);

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);

    const posLoc = gl.getAttribLocation(program, 'a_position');
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    const uTimeLoc = gl.getUniformLocation(program, 'u_time');
    const uResLoc = gl.getUniformLocation(program, 'u_resolution');

    let startTime = performance.now();
    function render() {
        gl.viewport(0, 0, canvas.width, canvas.height);
        const elapsed = (performance.now() - startTime) * 0.001;
        gl.uniform1f(uTimeLoc, elapsed);
        gl.uniform2f(uResLoc, canvas.width, canvas.height);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        requestAnimationFrame(render);
    }
    render();
}

// --- Arc Reactor Orb Animation ---
let orbStatus = 'idle'; // idle, listening, speaking, thinking
let orbAngle = 0;
let orbPulse = 0;
let orbPulseDir = 1;

function initOrbCanvas() {
    const canvas = document.getElementById('orb-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const cx = canvas.width / 2;
        const cy = canvas.height / 2;

        orbAngle += (orbStatus === 'thinking' ? 0.08 : 0.03);
        orbPulse += 0.4 * orbPulseDir;
        if (orbPulse > 10 || orbPulse < 0) orbPulseDir *= -1;

        const colors = {
            idle: '#3ed6ff',
            listening: '#34d399',
            speaking: '#f472b6',
            thinking: '#feba39'
        };
        const themeColor = colors[orbStatus] || '#3ed6ff';

        // Outer glow
        ctx.beginPath();
        ctx.arc(cx, cy, 70 + orbPulse, 0, Math.PI * 2);
        ctx.fillStyle = themeColor + '15';
        ctx.fill();

        // Dash outer ring
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(orbAngle * 0.5);
        ctx.beginPath();
        ctx.arc(0, 0, 65, 0, Math.PI * 2);
        ctx.setLineDash([8, 6]);
        ctx.strokeStyle = themeColor + '66';
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.restore();

        // 8 Arc segments
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(orbAngle);
        const numCoils = 8;
        const step = (Math.PI * 2) / numCoils;
        for (let i = 0; i < numCoils; i++) {
            ctx.beginPath();
            ctx.arc(0, 0, 52, i * step, i * step + step * 0.6);
            ctx.strokeStyle = themeColor;
            ctx.lineWidth = 5;
            ctx.stroke();
        }
        ctx.restore();

        // Inner glowing core
        ctx.beginPath();
        ctx.arc(cx, cy, 18, 0, Math.PI * 2);
        ctx.fillStyle = themeColor;
        ctx.fill();

        // Center white dot
        ctx.beginPath();
        ctx.arc(cx, cy, 8, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();

        requestAnimationFrame(animate);
    }
    animate();
}

function toggleOrbState() {
    const states = ['idle', 'listening', 'speaking', 'thinking'];
    const nextIdx = (states.indexOf(orbStatus) + 1) % states.length;
    setOrbState(states[nextIdx]);
}

function setOrbState(state) {
    orbStatus = state;
    const label = document.getElementById('assistant-state-label');
    if (label) {
        label.innerText = `STATE: ${state.toUpperCase()}`;
    }
}

// --- Digital Clock ---
function startClock() {
    function update() {
        const now = new Date();
        const str = now.toTimeString().split(' ')[0];
        const clockEl = document.getElementById('header-clock');
        if (clockEl) clockEl.innerText = str;
    }
    setInterval(update, 1000);
    update();
}

// --- Telemetry Polling ---
function startTelemetryPolling() {
    async function poll() {
        try {
            const res = await fetch('/api/status');
            if (res.ok) {
                const data = await res.json();
                updateTelemetryUI(data);
            }
        } catch (e) {
            // Fallback simulated metrics if server not yet started
            const cpu = Math.floor(10 + Math.random() * 15);
            const ram = Math.floor(35 + Math.random() * 5);
            updateTelemetryUI({ cpu_percent: cpu, ram_percent: ram });
        }
    }
    setInterval(poll, 3000);
    poll();
}

function updateTelemetryUI(data) {
    const cpu = Math.round(data.cpu_percent || 0);
    const ram = Math.round(data.ram_percent || 0);

    const headerCpu = document.getElementById('header-cpu');
    const headerRam = document.getElementById('header-ram');
    if (headerCpu) headerCpu.innerText = `${cpu}%`;
    if (headerRam) headerRam.innerText = `${ram}%`;

    const gaugeCpuVal = document.getElementById('gauge-cpu-val');
    const gaugeCpuBar = document.getElementById('gauge-cpu-bar');
    if (gaugeCpuVal) gaugeCpuVal.innerText = `${cpu}%`;
    if (gaugeCpuBar) gaugeCpuBar.style.width = `${cpu}%`;

    const gaugeRamVal = document.getElementById('gauge-ram-val');
    const gaugeRamBar = document.getElementById('gauge-ram-bar');
    if (gaugeRamVal) gaugeRamVal.innerText = `${ram}%`;
    if (gaugeRamBar) gaugeRamBar.style.width = `${ram}%`;
}

// --- Terminal Log & Command Processing ---
function appendTerminal(sender, message, isUser = false) {
    const feed = document.getElementById('terminal-feed');
    if (!feed) return;

    const timeStr = new Date().toTimeString().split(' ')[0];
    const div = document.createElement('div');
    div.className = 'text-on-surface-variant';

    if (isUser) {
        div.innerHTML = `[${timeStr}] <span class="text-primary font-bold">COMMAND &gt;</span> <span class="text-on-surface">${escapeHtml(message)}</span>`;
    } else {
        div.innerHTML = `[${timeStr}] <span class="text-emerald-400 font-bold">${escapeHtml(sender)} &gt;</span> <span class="text-on-surface">${escapeHtml(message)}</span>`;
    }

    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
}

function escapeHtml(text) {
    return text.replace(/[&<>"']/g, function(m) {
        return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'}[m];
    });
}

async function handleCommandSubmit(event) {
    event.preventDefault();
    const input = document.getElementById('command-input');
    if (!input) return;
    const cmd = input.value.trim();
    if (!cmd) return;

    input.value = '';
    appendTerminal('USER', cmd, true);
    setOrbState('thinking');

    try {
        const res = await fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd })
        });
        if (res.ok) {
            const data = await res.json();
            setOrbState('speaking');
            appendTerminal('JARVIS', data.response || 'Command executed successfully.');
            setTimeout(() => setOrbState('idle'), 2500);
        } else {
            setOrbState('idle');
            appendTerminal('JARVIS', 'Command processed locally.');
        }
    } catch (e) {
        setOrbState('idle');
        // Handle local execution fallback
        processLocalCommand(cmd);
    }
}

function sendQuickCommand(cmd) {
    const input = document.getElementById('command-input');
    if (input) {
        input.value = cmd;
        handleCommandSubmit(new Event('submit'));
    }
}

function processLocalCommand(cmd) {
    const lower = cmd.toLowerCase();
    if (lower.includes('time')) {
        appendTerminal('JARVIS', `Current time: ${new Date().toLocaleTimeString()}`);
    } else if (lower.includes('status')) {
        appendTerminal('JARVIS', 'All systems optimal. WebGL HUD, voice worker, and security monitors active.');
    } else if (lower.includes('help') || lower.includes('protocols')) {
        appendTerminal('JARVIS', 'Available protocols: time, status, note <text>, identify, security, initialize');
    } else if (lower.includes('who are you') || lower.includes('identify')) {
        appendTerminal('JARVIS', 'I am JARVIS — Just A Rather Very Intelligent System. Autonomous AI Command Assistant.');
    } else {
        appendTerminal('JARVIS', `Acknowledged command: "${cmd}". System listening.`);
    }
}

// --- Web Speech API (Voice Command Toggle) ---
let isMicActive = false;
let recognition = null;

function toggleVoice() {
    const micBtn = document.getElementById('mic-toggle-btn');
    const micIcon = document.getElementById('mic-icon');
    const micText = document.getElementById('mic-status-text');

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        appendTerminal('SYSTEM', 'Web Speech API is not supported in this browser. Use text input.');
        return;
    }

    if (!isMicActive) {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onstart = () => {
            isMicActive = true;
            setOrbState('listening');
            if (micText) micText.innerText = 'MIC_LISTENING';
            if (micIcon) micIcon.classList.add('text-emerald-400');
            appendTerminal('SYSTEM', 'Microphone active. Listening for voice command...');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            appendTerminal('VOICE', transcript, true);
            sendQuickCommand(transcript);
        };

        recognition.onerror = (event) => {
            appendTerminal('SYSTEM', `Speech recognition error: ${event.error}`);
            stopVoice();
        };

        recognition.onend = () => {
            stopVoice();
        };

        recognition.start();
    } else {
        stopVoice();
    }
}

function stopVoice() {
    isMicActive = false;
    if (recognition) {
        try { recognition.stop(); } catch(e) {}
    }
    setOrbState('idle');
    const micText = document.getElementById('mic-status-text');
    const micIcon = document.getElementById('mic-icon');
    if (micText) micText.innerText = 'MIC_ACTIVE';
    if (micIcon) micIcon.classList.remove('text-emerald-400');
}
