"""
MelodyLoop — Cyber Synthwave / Electric Aurora UI Theme.
Provides high-performance glowing CSS, animated floating particles, audio visualizer bars,
and custom glassmorphism components for Streamlit.
"""

CYBER_SYNTHWAVE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ==============================================================================
   1. GLOBAL PAGE & COSMIC VOID BACKGROUND
   ============================================================================== */
:root {
    --bg-void: #070913;
    --bg-card: rgba(13, 17, 34, 0.72);
    --bg-card-hover: rgba(18, 24, 48, 0.88);
    --cyan-glow: #00f0ff;
    --cyan-dim: rgba(0, 240, 255, 0.25);
    --purple-glow: #b026ff;
    --purple-dim: rgba(176, 38, 255, 0.25);
    --magenta-glow: #ec4899;
    --emerald-glow: #00ffb3;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border-glow: 1px solid rgba(0, 240, 255, 0.22);
}

.stApp {
    background-color: var(--bg-void) !important;
    background-image: 
        radial-gradient(circle at 50% -10%, rgba(176, 38, 255, 0.18), transparent 60%),
        radial-gradient(circle at 5% 30%, rgba(0, 240, 255, 0.10), transparent 45%),
        radial-gradient(circle at 95% 70%, rgba(236, 72, 153, 0.08), transparent 50%),
        radial-gradient(circle at 50% 110%, rgba(0, 240, 255, 0.08), transparent 50%) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Hide default streamlit decoration */
header[data-testid="stHeader"] {
    background: transparent !important;
}
div[data-testid="stDecoration"] {
    background: linear-gradient(90deg, var(--cyan-glow), var(--purple-glow), var(--magenta-glow)) !important;
    height: 2px !important;
}

/* ==============================================================================
   2. FLOATING MUSICAL PARTICLES & BACKGROUND AMBIENCE
   ============================================================================== */
.ambient-particles-layer {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.p-item {
    position: absolute;
    bottom: -60px;
    user-select: none;
    pointer-events: none;
    font-family: 'JetBrains Mono', monospace;
    animation-name: floatParticle;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
}

@keyframes floatParticle {
    0% {
        transform: translateY(0) rotate(0deg) scale(0.7);
        opacity: 0;
    }
    15% {
        opacity: 0.65;
    }
    85% {
        opacity: 0.55;
    }
    100% {
        transform: translateY(-110vh) rotate(360deg) scale(1.1);
        opacity: 0;
    }
}

/* Particle variations */
.p1 { left: 8%; font-size: 22px; color: #00f0ff; text-shadow: 0 0 14px rgba(0,240,255,0.8); animation-duration: 22s; animation-delay: 0s; }
.p2 { left: 18%; width: 6px; height: 6px; border-radius: 50%; background: #b026ff; box-shadow: 0 0 12px #b026ff; animation-duration: 28s; animation-delay: 3s; }
.p3 { left: 28%; font-size: 20px; color: #ec4899; text-shadow: 0 0 14px rgba(236,72,153,0.8); animation-duration: 20s; animation-delay: 7s; }
.p4 { left: 42%; font-size: 16px; color: #00ffb3; text-shadow: 0 0 10px rgba(0,255,179,0.8); animation-duration: 25s; animation-delay: 2s; }
.p5 { left: 55%; width: 8px; height: 8px; border-radius: 50%; background: #00f0ff; box-shadow: 0 0 16px #00f0ff; animation-duration: 30s; animation-delay: 11s; }
.p6 { left: 68%; font-size: 24px; color: #b026ff; text-shadow: 0 0 16px rgba(176,38,255,0.8); animation-duration: 19s; animation-delay: 5s; }
.p7 { left: 78%; font-size: 18px; color: #00f0ff; text-shadow: 0 0 12px rgba(0,240,255,0.8); animation-duration: 24s; animation-delay: 9s; }
.p8 { left: 88%; width: 5px; height: 5px; border-radius: 50%; background: #ec4899; box-shadow: 0 0 10px #ec4899; animation-duration: 27s; animation-delay: 1s; }
.p9 { left: 93%; font-size: 20px; color: #00ffb3; text-shadow: 0 0 12px rgba(0,255,179,0.8); animation-duration: 21s; animation-delay: 14s; }

/* ==============================================================================
   3. HERO BANNER & ORNATE GLOWING DIVIDER
   ============================================================================== */
.hero-container {
    text-align: center;
    padding: 24px 10px 18px 10px;
    margin-bottom: 22px;
    position: relative;
    z-index: 1;
}

/* Audio Visualizer Equalizer */
.hero-eq-bars {
    display: inline-flex;
    align-items: flex-end;
    justify-content: center;
    gap: 4px;
    height: 28px;
    margin-bottom: 10px;
}
.hero-eq-bar {
    width: 3.5px;
    border-radius: 2px;
    background: linear-gradient(180deg, var(--cyan-glow), var(--purple-glow));
    box-shadow: 0 0 8px rgba(0, 240, 255, 0.7);
    animation: eqBounce 1.2s ease-in-out infinite alternate;
}
.hero-eq-bar:nth-child(1) { height: 12px; animation-delay: 0.1s; }
.hero-eq-bar:nth-child(2) { height: 22px; animation-delay: 0.35s; }
.hero-eq-bar:nth-child(3) { height: 28px; animation-delay: 0.0s; }
.hero-eq-bar:nth-child(4) { height: 18px; animation-delay: 0.45s; }
.hero-eq-bar:nth-child(5) { height: 10px; animation-delay: 0.2s; }

@keyframes eqBounce {
    0% { height: 6px; opacity: 0.4; }
    50% { height: 26px; opacity: 1.0; }
    100% { height: 10px; opacity: 0.7; }
}

.hero-title {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 2.85rem !important;
    font-weight: 900 !important;
    letter-spacing: 5px !important;
    margin: 4px 0 8px 0 !important;
    background: linear-gradient(135deg, #ffffff 0%, #00f0ff 40%, #b026ff 80%, #ff2a85 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 25px rgba(0, 240, 255, 0.45));
    text-transform: uppercase;
}

.hero-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
    margin: 0 auto 16px auto;
    max-width: 820px;
    line-height: 1.5;
}

/* Ornate Centerpiece Glowing Divider */
.hero-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    max-width: 580px;
    margin: 0 auto;
}
.hero-divider-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 240, 255, 0.6), rgba(176, 38, 255, 0.4));
    box-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
}
.hero-divider-line.right {
    background: linear-gradient(90deg, rgba(176, 38, 255, 0.4), rgba(0, 240, 255, 0.6), transparent);
}
.hero-divider-diamond {
    color: var(--cyan-glow);
    font-size: 10px;
    text-shadow: 0 0 10px var(--cyan-glow);
    animation: diamondPulse 2.4s ease-in-out infinite;
}
.hero-divider-glyph {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 6px;
    background: rgba(13, 17, 34, 0.9);
    border: 1px solid rgba(0, 240, 255, 0.4);
    box-shadow: 0 0 14px rgba(0, 240, 255, 0.35);
    font-size: 13px;
    color: #ffffff;
}

@keyframes diamondPulse {
    0%, 100% { opacity: 0.5; transform: scale(0.9); }
    50% { opacity: 1.0; transform: scale(1.15); text-shadow: 0 0 15px var(--cyan-glow); }
}

/* ==============================================================================
   4. GLOWING STATUS BADGES & PILLS
   ============================================================================== */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 4px 0 12px 0;
    backdrop-filter: blur(10px);
}
.badge-pill-success {
    background: rgba(0, 255, 179, 0.10);
    border: 1px solid rgba(0, 255, 179, 0.4);
    color: #00ffb3;
    box-shadow: 0 0 16px rgba(0, 255, 179, 0.22);
}
.badge-pill-cyan {
    background: rgba(0, 240, 255, 0.10);
    border: 1px solid rgba(0, 240, 255, 0.4);
    color: #00f0ff;
    box-shadow: 0 0 16px rgba(0, 240, 255, 0.22);
}
.badge-pill-purple {
    background: rgba(176, 38, 255, 0.10);
    border: 1px solid rgba(176, 38, 255, 0.4);
    color: #d946ef;
    box-shadow: 0 0 16px rgba(176, 38, 255, 0.22);
}

.pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px currentColor;
    animation: dotPulse 1.6s ease-in-out infinite;
}
@keyframes dotPulse {
    0%, 100% { transform: scale(0.85); opacity: 0.7; }
    50% { transform: scale(1.25); opacity: 1.0; }
}

/* ==============================================================================
   5. TABS STYLING (GLOWING UNDERLINE & HOVER NEON)
   ============================================================================== */
button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    color: #94a3b8 !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 10px 18px !important;
    transition: all 0.25s ease-in-out !important;
    border-radius: 8px 8px 0 0 !important;
}
button[data-baseweb="tab"]:hover {
    color: #f8fafc !important;
    text-shadow: 0 0 12px rgba(0, 240, 255, 0.6) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #00f0ff !important;
    background: rgba(0, 240, 255, 0.08) !important;
    border-bottom: 2px solid #00f0ff !important;
    box-shadow: 0 4px 18px rgba(0, 240, 255, 0.3) !important;
}
div[data-baseweb="tab-list"] {
    border-bottom: 1px solid rgba(0, 240, 255, 0.18) !important;
    gap: 8px !important;
    margin-bottom: 18px !important;
}

/* ==============================================================================
   6. GLASSMORPHISM CARDS & CONTAINERS
   ============================================================================== */
div[data-testid="stExpander"],
div[data-testid="stMetric"],
.glass-card {
    background: var(--bg-card) !important;
    border: 1px solid rgba(0, 240, 255, 0.18) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(14px) !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
    transition: all 0.28s ease !important;
}
div[data-testid="stExpander"]:hover,
div[data-testid="stMetric"]:hover {
    border-color: rgba(0, 240, 255, 0.4) !important;
    box-shadow: 0 12px 36px rgba(0, 240, 255, 0.15), 0 0 20px rgba(176, 38, 255, 0.1) !important;
    transform: translateY(-1px);
}

/* Metrics Typography */
div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #00f0ff !important;
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    font-size: 1.55rem !important;
    text-shadow: 0 0 16px rgba(0, 240, 255, 0.55) !important;
}

/* ==============================================================================
   7. PULSING NEON BUTTONS
   ============================================================================== */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00f0ff 0%, #8b5cf6 55%, #ec4899 100%) !important;
    color: #ffffff !important;
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    box-shadow: 0 0 18px rgba(0, 240, 255, 0.55), 0 0 35px rgba(139, 92, 246, 0.3) !important;
    transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1) !important;
    text-transform: uppercase !important;
    animation: neonBtnPulse 2.8s infinite alternate !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) scale(1.015) !important;
    box-shadow: 0 0 28px rgba(0, 240, 255, 0.85), 0 0 55px rgba(236, 72, 153, 0.5) !important;
    color: #ffffff !important;
}

@keyframes neonBtnPulse {
    0% {
        box-shadow: 0 0 16px rgba(0, 240, 255, 0.5), 0 0 30px rgba(139, 92, 246, 0.25);
    }
    100% {
        box-shadow: 0 0 26px rgba(0, 240, 255, 0.8), 0 0 45px rgba(139, 92, 246, 0.45);
    }
}

div.stButton > button:not([kind="primary"]) {
    background: rgba(13, 17, 34, 0.85) !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    color: #e2e8f0 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:not([kind="primary"]):hover {
    border-color: #00f0ff !important;
    color: #00f0ff !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.35) !important;
}

/* Download buttons */
div[data-testid="stDownloadButton"] > button {
    background: rgba(13, 17, 34, 0.9) !important;
    border: 1px solid rgba(176, 38, 255, 0.45) !important;
    color: #e879f9 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: #ec4899 !important;
    color: #ffffff !important;
    box-shadow: 0 0 20px rgba(236, 72, 153, 0.45) !important;
    transform: translateY(-1px);
}

/* ==============================================================================
   8. INPUTS, TEXTAREAS & SELECTBOXES
   ============================================================================== */
textarea.stTextArea,
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background: rgba(10, 13, 26, 0.85) !important;
    border: 1px solid rgba(0, 240, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
    transition: all 0.2s ease !important;
}
textarea.stTextArea:focus,
div[data-baseweb="input"]:focus-within > div,
div[data-baseweb="select"]:focus-within > div {
    border-color: #00f0ff !important;
    box-shadow: 0 0 16px rgba(0, 240, 255, 0.35) !important;
}

/* Sliders */
div[data-testid="stSlider"] div[data-baseweb="slider"] {
    margin-top: 8px !important;
}
div[data-testid="stSlider"] div[role="slider"] {
    background: #00f0ff !important;
    box-shadow: 0 0 14px #00f0ff !important;
    border: 2px solid #ffffff !important;
}

/* Radio buttons */
div[data-testid="stRadio"] label {
    color: #cbd5e1 !important;
}

/* ==============================================================================
   AUDIO PLAYER CYBER DECK & NATIVE CONTROLS STYLING
   ============================================================================== */
.audio-eq-wave {
    display: inline-flex;
    align-items: flex-end;
    gap: 3px;
    height: 14px;
    margin-right: 4px;
}
.audio-eq-wave span {
    width: 3px;
    border-radius: 1.5px;
    background: linear-gradient(180deg, #00f0ff, #b026ff);
    box-shadow: 0 0 6px #00f0ff;
    animation: eqMiniBounce 1.1s ease-in-out infinite alternate;
}
.audio-eq-wave span:nth-child(1) { height: 6px; animation-delay: 0.1s; }
.audio-eq-wave span:nth-child(2) { height: 13px; animation-delay: 0.35s; }
.audio-eq-wave span:nth-child(3) { height: 14px; animation-delay: 0.0s; }
.audio-eq-wave span:nth-child(4) { height: 9px; animation-delay: 0.45s; }
.audio-eq-wave span:nth-child(5) { height: 5px; animation-delay: 0.2s; }

@keyframes eqMiniBounce {
    0% { height: 4px; opacity: 0.45; }
    50% { height: 14px; opacity: 1.0; }
    100% { height: 6px; opacity: 0.65; }
}

/* Native audio element enhancements */
audio {
    width: 100% !important;
    height: 46px !important;
    border-radius: 28px !important;
    outline: none !important;
    box-shadow: 0 0 18px rgba(0, 240, 255, 0.35), 0 0 35px rgba(176, 38, 255, 0.15) !important;
    transition: all 0.25s ease !important;
}
audio:hover {
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.55), 0 0 45px rgba(176, 38, 255, 0.3) !important;
}


/* Streamlit Pyplot Frame Enhancement */
div[data-testid="stPyplot"] {
    background: rgba(10, 14, 28, 0.75) !important;
    border: 1px solid rgba(0, 240, 255, 0.28) !important;
    border-radius: 14px !important;
    padding: 10px 14px 6px 14px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(0, 240, 255, 0.12) !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stPyplot"]:hover {
    border-color: rgba(0, 240, 255, 0.5) !important;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 240, 255, 0.22) !important;
}

/* WebKit media controls styling (Chrome, Brave, Edge) */
audio::-webkit-media-controls-panel {
    background: linear-gradient(135deg, rgba(9, 13, 31, 0.98) 0%, rgba(18, 24, 52, 0.95) 100%) !important;
    border: 1px solid rgba(0, 240, 255, 0.35) !important;
    border-radius: 28px !important;
    box-shadow: inset 0 0 15px rgba(0, 240, 255, 0.12) !important;
}

audio::-webkit-media-controls-current-time-display,
audio::-webkit-media-controls-time-remaining-display {
    color: #00f0ff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 11.5px !important;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.7) !important;
}

audio::-webkit-media-controls-play-button {
    filter: invert(1) hue-rotate(170deg) drop-shadow(0 0 8px #00f0ff) !important;
    transform: scale(1.1) !important;
    transition: transform 0.2s ease !important;
}
audio::-webkit-media-controls-play-button:hover {
    transform: scale(1.22) !important;
}

audio::-webkit-media-controls-timeline {
    filter: invert(0.85) sepia(1) saturate(6) hue-rotate(145deg) drop-shadow(0 0 6px rgba(0, 240, 255, 0.6)) !important;
    border-radius: 10px !important;
}

audio::-webkit-media-controls-mute-button {
    filter: invert(1) hue-rotate(170deg) drop-shadow(0 0 4px #00f0ff) !important;
}

audio::-webkit-media-controls-volume-slider {
    filter: invert(0.85) sepia(1) saturate(6) hue-rotate(145deg) drop-shadow(0 0 4px rgba(0, 240, 255, 0.5)) !important;
}

audio::-webkit-media-controls-overflow-button {
    filter: invert(1) hue-rotate(170deg) drop-shadow(0 0 4px #00f0ff) !important;
}

/* ==============================================================================
   9. SIDEBAR STYLING
   ============================================================================== */

/* Sidebar collapsed control toggle button (MuseGuide-inspired glowing pill) */
div[data-testid="stSidebarCollapsedControl"],
div[data-testid="collapsedControl"] {
    display: block !important;
}
div[data-testid="stSidebarCollapsedControl"] button,
div[data-testid="collapsedControl"] button,
button[data-testid="stSidebarCollapseButton"] {
    background: rgba(13, 17, 34, 0.88) !important;
    border: 1px solid rgba(0, 240, 255, 0.45) !important;
    border-radius: 8px !important;
    color: #00f0ff !important;
    box-shadow: 0 0 14px rgba(0, 240, 255, 0.35) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
div[data-testid="stSidebarCollapsedControl"] button:hover,
div[data-testid="collapsedControl"] button:hover,
button[data-testid="stSidebarCollapseButton"]:hover {
    border-color: #00f0ff !important;
    color: #ffffff !important;
    box-shadow: 0 0 22px rgba(0, 240, 255, 0.8), 0 0 35px rgba(176, 38, 255, 0.45) !important;
    transform: scale(1.06);
}

section[data-testid="stSidebar"] {
    background: rgba(8, 10, 20, 0.92) !important;
    border-right: 1px solid rgba(0, 240, 255, 0.15) !important;
    backdrop-filter: blur(20px) !important;
}
section[data-testid="stSidebar"] div[data-testid="stMetric"] {
    background: rgba(13, 17, 34, 0.6) !important;
    border: 1px solid rgba(176, 38, 255, 0.2) !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    background: rgba(13, 17, 34, 0.85) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(12px) !important;
}
</style>
"""

PARTICLES_HTML = """
<div class="ambient-particles-layer">
    <span class="p-item p1">♪</span>
    <span class="p-item p2"></span>
    <span class="p-item p3">♫</span>
    <span class="p-item p4">✦</span>
    <span class="p-item p5"></span>
    <span class="p-item p6">♬</span>
    <span class="p-item p7">♩</span>
    <span class="p-item p8"></span>
    <span class="p-item p9">✧</span>
</div>
"""

HERO_BANNER_HTML = """
<div class="hero-container">
    <div class="hero-eq-bars">
        <span class="hero-eq-bar"></span>
        <span class="hero-eq-bar"></span>
        <span class="hero-eq-bar"></span>
        <span class="hero-eq-bar"></span>
        <span class="hero-eq-bar"></span>
    </div>
    <div class="hero-title">MELODYLOOP</div>
    <div class="hero-subtitle">
        Deep Symbolic Music Generation &bull; Condition-Aware Recurrent Neural Network &bull; Grounded in MAESTRO & MidiCaps Datasets
    </div>
    <div class="hero-divider">
        <span class="hero-divider-line"></span>
        <span class="hero-divider-diamond">◆</span>
        <span class="hero-divider-glyph">🎹</span>
        <span class="hero-divider-diamond">◆</span>
        <span class="hero-divider-line right"></span>
    </div>
</div>
"""


def render_status_pill(text: str, pill_type: str = "cyan", dot: bool = True) -> str:
    """Render a sleek glowing status pill with an animated pulsing dot."""
    dot_html = '<span class="pulse-dot"></span>' if dot else ""
    return f'<div class="badge-pill badge-pill-{pill_type}">{dot_html}<span>{text}</span></div>'


def render_target_conditions_card(mood: str, tempo: str, bpm: int, register: str, dynamics: str) -> str:
    """Render a cyber-styled active conditions target card."""
    return f"""
<div style="background: rgba(13, 17, 34, 0.75); border: 1px solid rgba(0, 240, 255, 0.28); border-radius: 10px; padding: 10px 16px; margin: 10px 0 16px 0; backdrop-filter: blur(12px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);">
    <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between;">
        <div style="font-size: 0.82rem; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; display: flex; align-items: center; gap: 6px;">
            <span style="color: #00f0ff;">◆</span> Active LSTM Conditioning State
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            <span class="badge-pill badge-pill-cyan" style="margin: 0; padding: 3px 10px; font-size: 0.78rem;">Mood: <strong style="color: #ffffff;">{mood.upper()}</strong></span>
            <span class="badge-pill badge-pill-purple" style="margin: 0; padding: 3px 10px; font-size: 0.78rem;">Tempo: <strong style="color: #ffffff;">{tempo.upper()} ({bpm} BPM)</strong></span>
            <span class="badge-pill badge-pill-cyan" style="margin: 0; padding: 3px 10px; font-size: 0.78rem;">Register: <strong style="color: #ffffff;">{register.upper()}</strong></span>
            <span class="badge-pill badge-pill-purple" style="margin: 0; padding: 3px 10px; font-size: 0.78rem;">Dynamics: <strong style="color: #ffffff;">{dynamics.upper()}</strong></span>
        </div>
    </div>
</div>
"""



def render_audio_player_header(title: str = "Audio Playback", subtitle: str = "VELOCITY-AWARE STEREO &bull; 44.1 kHz") -> str:
    """Render a futuristic audio deck header with animated mini equalizer bars."""
    return f"""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
    <div style="font-family: 'Orbitron', sans-serif; font-size: 0.84rem; font-weight: 700; letter-spacing: 1px; color: #00f0ff; display: inline-flex; align-items: center; gap: 8px; text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);">
        <span class="audio-eq-wave">
            <span></span><span></span><span></span><span></span><span></span>
        </span>
        <span>{title.upper()}</span>
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8; background: rgba(0, 240, 255, 0.08); border: 1px solid rgba(0, 240, 255, 0.22); border-radius: 12px; padding: 2px 8px;">
        {subtitle}
    </div>
</div>
"""


def render_piano_roll_header(title: str = "Digital Piano-Roll Visualizer", subtitle: str = "CHROMATIC SPECTRUM &bull; VELOCITY GLOW") -> str:
    """Render a futuristic piano roll display header."""
    return f"""
<div style="display: flex; align-items: center; justify-content: space-between; margin-top: 16px; margin-bottom: 8px;">
    <div style="font-family: 'Orbitron', sans-serif; font-size: 0.88rem; font-weight: 700; letter-spacing: 1px; color: #00f0ff; display: inline-flex; align-items: center; gap: 8px; text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);">
        <span style="color: #b026ff;">◆</span>
        <span>{title.upper()}</span>
    </div>
    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8; background: rgba(176, 38, 255, 0.1); border: 1px solid rgba(176, 38, 255, 0.28); border-radius: 12px; padding: 2px 8px;">
        {subtitle}
    </div>
</div>
"""
