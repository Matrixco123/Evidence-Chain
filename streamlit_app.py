"""
EvidenceChain — Premium Storytelling Product Website
Built with Streamlit + Custom HTML/CSS

Architecture:
    Scene 1 — Hero (full viewport)
    Scene 2 — Problem → Solution
    Scene 3 — Certify Evidence (functional)
    Scene 4 — Verify Integrity (functional)
    Scene 5 — Features
    Scene 6 — About + Footer
"""

import requests
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="EvidenceChain — Digital Evidence Verification",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLES — injected as a single <style> block
#
# Organization:
#   1. Reset & Globals
#   2. Animations
#   3. Navbar
#   4. Hero (Scene 1)
#   5. Scenes shared
#   6. Problem/Solution (Scene 2)
#   7. Cards & Inputs
#   8. Steps UI
#   9. Features grid
#  10. Footer
#  11. Responsive
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ==========================================================================
   1. RESET & GLOBALS
   ========================================================================== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* Remove every piece of default Streamlit UI */
[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
.stDeployButton,
#MainMenu,
footer { display: none !important; }

html {
    scroll-behavior: smooth;
    overflow-y: auto !important;
    height: auto !important;
}
body {
    overflow-y: auto !important;
    height: auto !important;
    min-height: 100vh;
}

.stApp {
    background: #060d19;
    font-family: 'Inter', -apple-system, system-ui, sans-serif;
    color: #cbd5e1;
    overflow-x: hidden;
    overflow-y: auto !important;
    height: auto !important;
    min-height: 100vh;
}
/* Force Streamlit internal wrappers to allow scroll */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.stMainBlockContainer,
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlockBorderWrapper"],
section[data-testid="stMain"] {
    overflow: visible !important;
    height: auto !important;
    min-height: auto !important;
    max-height: none !important;
}

/* Noise overlay — adds subtle film-grain texture */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    opacity: 0.018;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 128px; pointer-events: none; z-index: 0;
}
.stApp > * { position: relative; z-index: 1; }

.block-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 0 clamp(20px, 4vw, 48px) !important;
    box-sizing: border-box !important;
}
/* Streamlit columns — prevent overflow */
[data-testid="stHorizontalBlock"] {
    max-width: 100%;
    box-sizing: border-box;
}
[data-testid="stColumn"] {
    overflow: hidden;
    min-width: 0;
}
/* Streamlit elements — full width within container */
[data-testid="stVerticalBlock"] {
    width: 100%;
}

/* Typography base */
h1,h2,h3,h4 { font-family:'Inter',sans-serif!important; color:#f1f5f9!important; }
p,span,label,li,div { font-family:'Inter',sans-serif!important; }


/* ==========================================================================
   2. ANIMATIONS
   ========================================================================== */
@keyframes bgShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes scrollReveal {
    from { opacity: 0; transform: translateY(40px); }
    to   { opacity: 1; transform: translateY(0); }
}
/* Scroll-triggered animation class */
.scroll-reveal {
    animation: scrollReveal ease both;
    animation-timeline: view();
    animation-range: entry 0% entry 35%;
}
/* Fallback for browsers without scroll-timeline */
@supports not (animation-timeline: view()) {
    .scroll-reveal {
        animation: fadeIn 0.7s ease both;
    }
}
@keyframes float1 {
    0%   { transform: translate(0,0) scale(1); }
    33%  { transform: translate(35px,-25px) scale(1.05); }
    66%  { transform: translate(-15px,20px) scale(0.97); }
    100% { transform: translate(0,0) scale(1); }
}
@keyframes float2 {
    0%   { transform: translate(0,0) scale(1); }
    50%  { transform: translate(-30px,20px) scale(1.07); }
    100% { transform: translate(0,0) scale(1); }
}
@keyframes ringRotate {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes ringBreath {
    0%,100% {
        box-shadow: inset 0 0 60px rgba(59,130,246,0.05),
                    0 0 80px rgba(99,102,241,0.06),
                    0 0 180px rgba(59,130,246,0.03);
    }
    50% {
        box-shadow: inset 0 0 90px rgba(59,130,246,0.09),
                    0 0 140px rgba(99,102,241,0.12),
                    0 0 240px rgba(59,130,246,0.06);
    }
}
@keyframes iconBob {
    0%,100% { transform: translateY(0) rotate(0deg); }
    50%     { transform: translateY(-8px) rotate(4deg); }
}
@keyframes scanLine {
    0%   { top: 10%; opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { top: 88%; opacity: 0; }
}
@keyframes pulseRing {
    0%   { transform: scale(0.85); opacity: 0.6; }
    100% { transform: scale(1.4); opacity: 0; }
}
@keyframes particleOrbit {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes coreGlow {
    0%,100% { opacity: 0.4; transform: scale(1); }
    50%     { opacity: 0.7; transform: scale(1.1); }
}
@keyframes hexRotate {
    from { transform: rotate(0deg); }
    to   { transform: rotate(-360deg); }
}
@keyframes dataStream {
    0%   { background-position: 0 0; }
    100% { background-position: 0 200px; }
}
@keyframes gridScroll {
    0%   { transform: perspective(500px) rotateX(60deg) translateY(0); }
    100% { transform: perspective(500px) rotateX(60deg) translateY(50px); }
}
@keyframes btnGlow {
    0%,100% { box-shadow: 0 0 16px rgba(59,130,246,0.12); }
    50%     { box-shadow: 0 0 28px rgba(59,130,246,0.22); }
}


/* ==========================================================================
   3. NAVBAR
   ========================================================================== */
.nav {
    position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    background: rgba(6,13,25,0.55);
    border-bottom: 1px solid rgba(255,255,255,0.03);
    padding: 0 clamp(24px,4vw,64px);
    height: 56px;
    display: flex; align-items: center; justify-content: space-between;
}
.nav-l { display: flex; align-items: center; gap: 12px; }
.nav-mark {
    width: 28px; height: 28px;
    background: linear-gradient(135deg,#3b82f6,#7c3aed);
    border-radius: 7px; display: grid; place-items: center;
    color: #fff; font-size: 13px; font-weight: 900;
}
.nav-name {
    color: #f8fafc; font-size: 15px; font-weight: 700;
    letter-spacing: -0.4px;
}
.nav-r { display: flex; align-items: center; gap: 2px; }

/* Nav link with animated underline */
.nav-a {
    color: #94a3b8 !important; font-size: 12.5px; font-weight: 500;
    padding: 6px 16px; text-decoration: none !important;
    position: relative; transition: color 0.2s;
}
.nav-a::after {
    content: ''; position: absolute;
    bottom: 0; left: 50%; width: 0; height: 1.5px;
    background: #3b82f6; border-radius: 1px;
    transform: translateX(-50%); transition: width 0.3s ease;
}
.nav-a:hover { color: #f1f5f9 !important; }
.nav-a:hover::after { width: 20px; }

/* Nav CTA */
.nav-cta {
    margin-left: 12px; padding: 6px 18px;
    background: linear-gradient(135deg,#3b82f6,#6366f1);
    color: #fff !important; font-size: 12px; font-weight: 700;
    border-radius: 7px; text-decoration: none !important;
    transition: all 0.25s; letter-spacing: 0.3px;
}
.nav-cta:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59,130,246,0.3);
}


/* ==========================================================================
   4. HERO — SCENE 1
   ========================================================================== */
.hero {
    position: relative; overflow: hidden;
    min-height: 100vh; width: 100%;
}
/* 3D perspective grid */
.hero::before {
    content: '';
    position: absolute; bottom: 0; left: -60%; width: 220%; height: 50%;
    background:
        repeating-linear-gradient(0deg,transparent,transparent 48px,rgba(59,130,246,0.025) 48px,rgba(59,130,246,0.025) 50px),
        repeating-linear-gradient(90deg,transparent,transparent 48px,rgba(59,130,246,0.025) 48px,rgba(59,130,246,0.025) 50px);
    transform: perspective(500px) rotateX(60deg);
    transform-origin: center bottom;
    animation: gridScroll 5s linear infinite;
    mask-image: linear-gradient(to top,rgba(0,0,0,0.4) 0%,transparent 70%);
    -webkit-mask-image: linear-gradient(to top,rgba(0,0,0,0.4) 0%,transparent 70%);
    pointer-events: none; z-index: 0;
}
/* Floating orbs */
.orb1 {
    position: absolute; top: 8%; left: -6%;
    width: 520px; height: 520px;
    background: radial-gradient(circle,rgba(59,130,246,0.12) 0%,transparent 65%);
    filter: blur(80px); border-radius: 50%;
    animation: float1 18s ease-in-out infinite;
    pointer-events: none; z-index: 0;
}
.orb2 {
    position: absolute; bottom: 3%; right: -8%;
    width: 440px; height: 440px;
    background: radial-gradient(circle,rgba(124,58,237,0.09) 0%,transparent 65%);
    filter: blur(90px); border-radius: 50%;
    animation: float2 22s ease-in-out infinite 4s;
    pointer-events: none; z-index: 0;
}

/* Hero inner layout — two columns */
.hero-inner {
    position: relative; z-index: 1;
    max-width: 1100px; margin: 0 auto;
    padding: 140px clamp(24px,5vw,64px) 80px;
    display: grid; grid-template-columns: 1.2fr 0.8fr;
    align-items: center; gap: 48px; min-height: 100vh;
}

/* Left side — text */
.hero-txt { animation: fadeIn 0.9s ease both; }
.hero-tag {
    display: inline-block;
    background: rgba(59,130,246,0.06);
    border: 1px solid rgba(59,130,246,0.14);
    color: #60a5fa; font-size: 10px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    padding: 6px 16px; border-radius: 100px; margin-bottom: 24px;
}
.hero-h1 {
    font-size: clamp(36px,5.5vw,60px) !important;
    font-weight: 900 !important; letter-spacing: -0.04em !important;
    line-height: 1.08 !important; margin: 0 !important;
    color: #f8fafc !important;
}
.hero-h1 span {
    background: linear-gradient(135deg,#60a5fa,#a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    color: #64748b !important; font-size: clamp(14px,1.6vw,17px);
    line-height: 1.8; max-width: 420px; margin: 22px 0 36px 0;
}
.hero-btns { display: flex; gap: 12px; flex-wrap: wrap; }
.btn-p {
    padding: 14px 30px; border-radius: 10px;
    background: linear-gradient(135deg,#3b82f6,#6366f1);
    color: #fff !important; font-size: 13.5px; font-weight: 700;
    text-decoration: none !important; transition: all 0.25s;
    animation: btnGlow 4s ease-in-out infinite;
}
.btn-p:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 12px 36px rgba(59,130,246,0.3);
    color: #fff !important;
}
.btn-s {
    padding: 14px 26px; border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.07); background: transparent;
    color: #94a3b8 !important; font-size: 13.5px; font-weight: 600;
    text-decoration: none !important; transition: all 0.25s;
}
.btn-s:hover {
    border-color: rgba(255,255,255,0.14);
    color: #f1f5f9 !important;
    background: rgba(255,255,255,0.02);
}
.hero-note {
    margin-top: 32px; color: #1e293b;
    font-size: 9.5px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
}

/* Right side — shield visual */
.hero-vis {
    display: flex; align-items: center; justify-content: center;
    animation: fadeIn 1.1s ease both 0.2s;
}
.vis-container {
    width: clamp(280px,30vw,380px); height: clamp(280px,30vw,380px);
    position: relative;
    display: grid; place-items: center;
}
/* Core glow */
.vis-core {
    position: absolute; inset: 25%;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
    animation: coreGlow 4s ease-in-out infinite;
    z-index: 0;
}
/* Outer ring */
.vis-ring-outer {
    position: absolute; inset: 0;
    border-radius: 50%;
    border: 1px solid rgba(59,130,246,0.1);
    animation: ringBreath 6s ease-in-out infinite;
}
/* Hex frame - rotates slowly */
.vis-hex {
    position: absolute; inset: 8%;
    animation: hexRotate 40s linear infinite;
}
.vis-hex svg {
    width: 100%; height: 100%;
    fill: none;
    stroke: rgba(99,102,241,0.08);
    stroke-width: 1;
}
/* Scanning line */
.vis-scan {
    position: absolute;
    left: 15%; right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.5), rgba(96,165,250,0.8), rgba(59,130,246,0.5), transparent);
    box-shadow: 0 0 12px rgba(59,130,246,0.3), 0 0 4px rgba(96,165,250,0.5);
    animation: scanLine 3.5s ease-in-out infinite;
    z-index: 3;
}
/* Pulse rings */
.vis-pulse {
    position: absolute; inset: 20%;
    border-radius: 50%;
    border: 1px solid rgba(59,130,246,0.15);
    animation: pulseRing 3s ease-out infinite;
    z-index: 1;
}
.vis-pulse-2 {
    position: absolute; inset: 20%;
    border-radius: 50%;
    border: 1px solid rgba(99,102,241,0.12);
    animation: pulseRing 3s ease-out infinite 1.5s;
    z-index: 1;
}
/* Orbiting particles */
.vis-particles {
    position: absolute; inset: -4%;
    animation: particleOrbit 16s linear infinite;
    z-index: 2;
}
.vis-p {
    position: absolute;
    width: 4px; height: 4px;
    border-radius: 50%;
    background: #60a5fa;
    box-shadow: 0 0 8px rgba(96,165,250,0.6), 0 0 20px rgba(59,130,246,0.3);
}
.vis-p:nth-child(1) { top: 5%; left: 48%; }
.vis-p:nth-child(2) { top: 50%; right: 2%; width: 3px; height: 3px; background: #818cf8; }
.vis-p:nth-child(3) { bottom: 8%; left: 30%; width: 3px; height: 3px; }
.vis-p:nth-child(4) { top: 35%; left: 3%; width: 2px; height: 2px; background: #a78bfa; }
/* Reverse orbit */
.vis-particles-2 {
    position: absolute; inset: 6%;
    animation: particleOrbit 24s linear infinite reverse;
    z-index: 2;
}
.vis-p2 {
    position: absolute;
    width: 3px; height: 3px;
    border-radius: 50%;
    background: rgba(139,92,246,0.6);
    box-shadow: 0 0 6px rgba(139,92,246,0.4);
}
.vis-p2:nth-child(1) { top: 0; left: 55%; }
.vis-p2:nth-child(2) { bottom: 5%; right: 25%; width: 2px; height: 2px; }
/* Inner ring */
.vis-ring-inner {
    position: absolute; inset: 22%;
    border-radius: 50%;
    border: 1px solid rgba(59,130,246,0.06);
}
/* Data stream background */
.vis-stream {
    position: absolute; inset: 28%;
    border-radius: 50%;
    overflow: hidden;
    opacity: 0.15;
}
.vis-stream::before {
    content: '';
    position: absolute; inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent 0px,
        transparent 8px,
        rgba(59,130,246,0.15) 8px,
        rgba(59,130,246,0.15) 9px
    );
    animation: dataStream 4s linear infinite;
}
/* Shield icon center */
.vis-icon {
    position: relative; z-index: 4;
    width: 64px; height: 64px;
    display: grid; place-items: center;
}
.vis-icon svg {
    width: 56px; height: 56px;
    filter: drop-shadow(0 0 20px rgba(96,165,250,0.35));
    animation: iconBob 5s ease-in-out infinite;
}


/* ==========================================================================
   5. SCENES — shared styles
   ========================================================================== */
.scene {
    max-width: 1100px; margin: 0 auto;
    padding: 0 clamp(24px,5vw,64px);
    box-sizing: border-box;
}
.scene-gap { height: clamp(100px,12vh,160px); }
.scene-fade { animation: fadeIn 0.7s ease both; }

/* About section expanded styles */
.about-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-top: 48px;
}
.about-block {
    background: rgba(15,23,42,0.4);
    border: 1px solid rgba(255,255,255,0.03);
    border-radius: 14px;
    padding: 32px 28px;
    transition: all 0.3s;
}
.about-block:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.25);
    border-color: rgba(59,130,246,0.08);
}
.about-block h4 {
    color: #e2e8f0 !important; font-size: 16px !important;
    font-weight: 700; margin: 0 0 12px 0 !important;
}
.about-block p {
    color: #475569 !important; font-size: 13.5px;
    line-height: 1.8; margin: 0;
}
.about-hero {
    grid-column: 1 / -1;
    background: linear-gradient(160deg, rgba(59,130,246,0.04), rgba(15,23,42,0.6));
    border: 1px solid rgba(59,130,246,0.08);
    border-radius: 16px;
    padding: 48px 40px;
    transition: all 0.3s;
}
.about-hero:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.3);
}
.about-hero h3 {
    color: #f1f5f9 !important; font-size: 22px !important;
    font-weight: 800; margin: 0 0 16px 0 !important;
    letter-spacing: -0.02em;
}
.about-hero p {
    color: #64748b !important; font-size: 15px;
    line-height: 1.85; margin: 0 0 12px 0;
    max-width: 700px;
}
.about-stat-row {
    display: flex; gap: 40px; margin-top: 28px; flex-wrap: wrap;
}
.about-stat h5 {
    color: #60a5fa !important; font-size: 28px !important;
    font-weight: 900; margin: 0 0 4px 0 !important;
}
.about-stat p {
    color: #475569 !important; font-size: 11px;
    text-transform: uppercase; letter-spacing: 1.5px;
    font-weight: 600; margin: 0;
}

/* Section header */
.sh {
    margin-bottom: 56px;
    animation: fadeIn 0.6s ease both;
}
.sh-label {
    color: #3b82f6; font-size: 10px; font-weight: 700;
    letter-spacing: 3px; text-transform: uppercase;
    margin: 0 0 12px 0;
}
.sh-title {
    color: #f1f5f9 !important;
    font-size: clamp(26px,3.8vw,42px) !important;
    font-weight: 800 !important; letter-spacing: -0.03em;
    line-height: 1.15 !important; margin: 0 0 14px 0 !important;
    max-width: 600px;
}
.sh-sub {
    color: #475569 !important; font-size: 15px;
    line-height: 1.7; max-width: 480px; margin: 0;
}

/* Divider — subtle gradient line */
.divider {
    height: 1px; border: none; margin: 0;
    background: linear-gradient(90deg, transparent 5%, rgba(59,130,246,0.08) 50%, transparent 95%);
}


/* ==========================================================================
   6. PROBLEM → SOLUTION (SCENE 2)
   ========================================================================== */
.ps-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 48px; align-items: start;
    animation: fadeIn 0.7s ease both;
}
.ps-card {
    padding: 36px 32px; border-radius: 16px;
}
.ps-problem {
    background: rgba(239,68,68,0.03);
    border: 1px solid rgba(239,68,68,0.06);
}
.ps-solution {
    background: rgba(59,130,246,0.03);
    border: 1px solid rgba(59,130,246,0.06);
}
.ps-card h4 {
    font-size: 14px !important; font-weight: 700;
    margin: 0 0 14px 0 !important; letter-spacing: -0.01em;
}
.ps-problem h4 { color: #f87171 !important; }
.ps-solution h4 { color: #60a5fa !important; }
.ps-card p {
    color: #64748b !important; font-size: 14px;
    line-height: 1.8; margin: 0;
}


/* ==========================================================================
   7. CARDS & INPUTS
   ========================================================================== */
.crd {
    background: rgba(15,23,42,0.55);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 16px; padding: 36px 32px;
    backdrop-filter: blur(10px);
    transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s;
}
.crd:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.3);
    border-color: rgba(59,130,246,0.08);
}
.crd-up {
    background: linear-gradient(170deg,rgba(15,23,42,0.7) 0%,rgba(10,16,30,0.4) 100%);
    border: 1px solid rgba(59,130,246,0.06);
    border-radius: 16px; padding: 40px 36px;
    transition: transform 0.3s, box-shadow 0.3s;
    animation: fadeIn 0.5s ease both;
}
.crd-up:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.25);
}
.crd-head {
    color: #64748b; font-size: 10.5px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2.5px;
    margin-bottom: 24px; display: flex; align-items: center; gap: 12px;
}
.crd-head-line { flex: 1; height: 1px; background: rgba(255,255,255,0.03); }

/* Labels */
.mi {
    color: #475569; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px; margin: 0 0 8px 0;
}
.vl {
    color: #e2e8f0; font-size: 15px; font-weight: 500;
    word-break: break-all; line-height: 1.5; margin: 0 0 24px 0;
}
.mn {
    font-family: 'SF Mono','Fira Code','Courier New',monospace !important;
    color: #64748b; font-size: 12px; word-break: break-all;
}
.pill { display: inline-block; padding: 5px 14px; border-radius: 6px; font-size: 10px; font-weight: 700; letter-spacing: 1px; }
.pill-ok { background: rgba(74,222,128,0.07); color: #4ade80; }
.sep { border: none; border-top: 1px solid rgba(255,255,255,0.03); margin: 24px 0; }

/* Buttons */
.stButton > button {
    width: auto !important;
    min-width: 200px;
    padding: 12px 28px !important;
    border-radius: 10px;
    font-family: 'Inter',sans-serif !important;
    font-weight: 700; font-size: 14px; letter-spacing: 0.3px;
    border: none;
    background: linear-gradient(135deg,#3b82f6,#6366f1) !important;
    color: #fff !important; transition: all 0.25s;
    box-shadow: 0 0 16px rgba(59,130,246,0.1);
    display: inline-block !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 0 32px rgba(59,130,246,0.25), 0 8px 24px rgba(0,0,0,0.2);
}
.stButton > button:active {
    transform: translateY(0) scale(0.99);
}
/* Full-width buttons only inside upload/verify cards */
.crd-up .stButton > button {
    width: 100% !important;
    display: block !important;
}
.stDownloadButton > button {
    width: auto !important; min-width: 200px;
    padding: 11px 24px !important; border-radius: 9px;
    font-family: 'Inter',sans-serif !important;
    font-weight: 600; font-size: 13px;
}

/* Inputs */
[data-testid="stFileUploader"] section {
    border: 1px dashed rgba(255,255,255,0.05) !important;
    border-radius: 12px !important; padding: 24px !important;
    background: rgba(15,23,42,0.25) !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(59,130,246,0.12) !important;
}
/* Push the Browse/Upload button to the right inside the dropzone */
[data-testid="stFileUploaderDropzone"] {
    display: flex !important;
    flex-direction: row-reverse !important;
    align-items: center !important;
    gap: 12px !important;
}
/* Hide the material icon text "upload" that overlaps with the button label */
[data-testid="stFileUploader"] [data-testid="stIconMaterial"] {
    display: none !important;
}
[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
    flex-shrink: 0 !important;
    padding: 8px 20px !important;
    border-radius: 8px !important;
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: #fff !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    white-space: nowrap !important;
    min-width: auto !important;
    width: auto !important;
    transition: all 0.25s !important;
    overflow: hidden !important;
}
[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59,130,246,0.3) !important;
}
[data-testid="stFileUploader"] small {
    color: #475569 !important;
    font-size: 12px !important;
    white-space: nowrap !important;
}
[data-testid="stNumberInput"] input {
    background: rgba(6,13,25,0.5) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 9px !important; color: #e2e8f0 !important;
    font-family: 'Inter',sans-serif !important;
    padding: 11px 14px !important;
}
.streamlit-expanderHeader {
    font-family: 'Inter',sans-serif !important;
    color: #94a3b8 !important; background: transparent !important;
    border: 1px solid rgba(255,255,255,0.03) !important;
    border-radius: 9px !important;
}


/* ==========================================================================
   8. STEPS UI (Verify section)
   ========================================================================== */
.stp { margin-bottom: 24px; }
.stp-h { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.stp-n {
    width: 26px; height: 26px; border-radius: 7px;
    background: rgba(59,130,246,0.07);
    color: #60a5fa; font-size: 11px; font-weight: 800;
    display: grid; place-items: center; flex-shrink: 0;
}
.stp-t { color: #cbd5e1; font-size: 12.5px; font-weight: 600; }
.stp-line { width: 1px; height: 16px; background: rgba(255,255,255,0.03); margin-left: 13px; }


/* ==========================================================================
   9. FEATURES GRID
   ========================================================================== */
.feat-grid {
    display: grid; grid-template-columns: repeat(3,1fr);
    gap: 18px; animation: fadeIn 0.6s ease both;
}
.feat {
    background: rgba(15,23,42,0.4);
    border: 1px solid rgba(255,255,255,0.03);
    border-radius: 14px; padding: 32px 24px;
    transition: all 0.3s; position: relative; overflow: hidden;
}
.feat::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,transparent,rgba(59,130,246,0.12),transparent);
    opacity: 0; transition: opacity 0.3s;
}
.feat:hover {
    transform: translateY(-4px);
    box-shadow: 0 14px 44px rgba(0,0,0,0.25);
    border-color: rgba(59,130,246,0.08);
}
.feat:hover::before { opacity: 1; }
.feat-ic {
    width: 36px; height: 36px;
    background: rgba(59,130,246,0.06); border-radius: 9px;
    display: grid; place-items: center;
    color: #60a5fa; font-size: 15px; font-weight: 800;
    margin-bottom: 18px;
}
.feat h4 {
    color: #e2e8f0 !important; font-size: 15px !important;
    font-weight: 700; margin: 0 0 8px 0 !important;
}
.feat p {
    color: #475569 !important; font-size: 12.5px; line-height: 1.7; margin: 0;
}


/* ==========================================================================
   10. FOOTER
   ========================================================================== */
.ft {
    text-align: center; padding: 56px 24px;
    border-top: 1px solid rgba(255,255,255,0.02);
}
.ft p { color: #1e293b !important; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; }


/* ==========================================================================
   11. RESPONSIVE
   ========================================================================== */
@media (max-width: 768px) {
    .hero-inner { grid-template-columns: 1fr; }
    .hero-vis { display: none; }
    .ps-grid { grid-template-columns: 1fr; }
    .feat-grid { grid-template-columns: 1fr; }
    .about-grid { grid-template-columns: 1fr; }
    .block-container {
        padding: 0 16px !important;
    }
}

</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# NAVBAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="nav">
    <a class="nav-l" href="#" style="text-decoration:none !important;">
        <div class="nav-mark">E</div>
        <div class="nav-name">EvidenceChain</div>
    </a>
    <div class="nav-r">
        <a class="nav-a" href="#certify">Upload</a>
        <a class="nav-a" href="#verify">Verify</a>
        <a class="nav-a" href="#about">About</a>
        <a class="nav-cta" href="#certify">Start</a>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 1 — HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="orb1"></div>
    <div class="orb2"></div>
    <div class="hero-inner">
        <div class="hero-txt">
            <div class="hero-tag">Forensic System</div>
            <h1 class="hero-h1">
                Secure Digital Evidence<br>
                <span>Verification</span>
            </h1>
            <p class="hero-sub">
                Ensure integrity. Detect tampering.<br>
                Present court-ready proof.
            </p>
            <div class="hero-btns">
                <a class="btn-p" href="#certify">Start Certification</a>
                <a class="btn-s" href="#verify">Verify File</a>
            </div>
            <p class="hero-note">SHA-256 &middot; RSA-2048 &middot; Tamper Detection</p>
        </div>
        <div class="hero-vis">
            <div class="vis-container">
                <div class="vis-core"></div>
                <div class="vis-ring-outer"></div>
                <div class="vis-hex">
                    <svg viewBox="0 0 200 200"><polygon points="100,8 185,54 185,146 100,192 15,146 15,54"/></svg>
                </div>
                <div class="vis-scan"></div>
                <div class="vis-pulse"></div>
                <div class="vis-pulse-2"></div>
                <div class="vis-ring-inner"></div>
                <div class="vis-stream"></div>
                <div class="vis-particles">
                    <div class="vis-p"></div>
                    <div class="vis-p"></div>
                    <div class="vis-p"></div>
                    <div class="vis-p"></div>
                </div>
                <div class="vis-particles-2">
                    <div class="vis-p2"></div>
                    <div class="vis-p2"></div>
                </div>
                <div class="vis-icon">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <linearGradient id="sg" x1="0" y1="0" x2="1" y2="1">
                                <stop offset="0%" stop-color="#60a5fa"/>
                                <stop offset="100%" stop-color="#a78bfa"/>
                            </linearGradient>
                        </defs>
                        <path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z" fill="url(#sg)" opacity="0.9"/>
                        <path d="M10 15.5l-3.5-3.5 1.41-1.41L10 12.67l5.59-5.59L17 8.5l-7 7z" fill="#fff" opacity="0.95"/>
                    </svg>
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 2 — PROBLEM → SOLUTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="scene-gap"></div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown("""
<div class="scene scroll-reveal" style="padding-top:100px; padding-bottom:20px;">
    <div class="sh">
        <p class="sh-label">The Challenge</p>
        <h2 class="sh-title">Digital Evidence Cannot Be Trusted Without Proof</h2>
    </div>
    <div class="ps-grid">
        <div class="ps-card ps-problem">
            <h4>The Problem</h4>
            <p>
                Files can be silently modified after collection.
                Screenshots can be doctored. Metadata can be stripped.
                Without cryptographic proof, digital evidence is just a file
                &mdash; and files can lie.
            </p>
        </div>
        <div class="ps-card ps-solution">
            <h4>The Solution</h4>
            <p>
                EvidenceChain creates an immutable cryptographic fingerprint
                at the moment of certification. Any modification &mdash; even a single
                byte &mdash; is instantly detectable. Your evidence becomes provable.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 3 — CERTIFY EVIDENCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="scene-gap"></div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div id="certify"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="scene scroll-reveal" style="padding-top:100px;">
    <div class="sh">
        <p class="sh-label">Certification</p>
        <h2 class="sh-title">Certify Evidence</h2>
        <p class="sh-sub">Upload a file, generate a cryptographic signature, receive a verifiable certificate.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Layout: description left, upload card right
col_info, col_upload = st.columns([1, 1.2], gap="large")

with col_info:
    st.markdown("""
    <div style="padding: 12px 0 12px 24px; animation: fadeIn 0.6s ease both;">
        <div style="margin-bottom:32px;">
            <p style="color:#60a5fa; font-size:11px; font-weight:700;
                      letter-spacing:2px; text-transform:uppercase; margin:0 0 8px 0;">Step 1</p>
            <p style="color:#e2e8f0; font-size:15px; font-weight:600; margin:0 0 6px 0;">Upload your evidence file</p>
            <p style="color:#475569; font-size:13px; line-height:1.7; margin:0;">Any file type. Any size.</p>
        </div>
        <div style="margin-bottom:32px;">
            <p style="color:#60a5fa; font-size:11px; font-weight:700;
                      letter-spacing:2px; text-transform:uppercase; margin:0 0 8px 0;">Step 2</p>
            <p style="color:#e2e8f0; font-size:15px; font-weight:600; margin:0 0 6px 0;">Hash + Signature generated</p>
            <p style="color:#475569; font-size:13px; line-height:1.7; margin:0;">SHA-256 fingerprint, RSA-2048 digital signature.</p>
        </div>
        <div>
            <p style="color:#60a5fa; font-size:11px; font-weight:700;
                      letter-spacing:2px; text-transform:uppercase; margin:0 0 8px 0;">Step 3</p>
            <p style="color:#e2e8f0; font-size:15px; font-weight:600; margin:0 0 6px 0;">Certificate + QR issued</p>
            <p style="color:#475569; font-size:13px; line-height:1.7; margin:0;">Download your PDF. Share the QR for instant verification.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_upload:
    st.markdown("""
    <div class="crd-up">
        <div class="crd-head">
            Upload Evidence
            <span class="crd-head-line"></span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="mi">Evidence File</p>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("file", type=None, label_visibility="collapsed", key="upload_main")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    certify_clicked = st.button("Certify Evidence", type="primary", key="btn_certify")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Handle certification ─────────────────────────────────────────────
    if certify_clicked and uploaded_file is not None:
        with st.spinner("Generating cryptographic certificate..."):
            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/octet-stream",
                    )
                }
                resp = requests.post(
                    f"{API_BASE}/upload",
                    files=files,
                    timeout=30,
                )
                st.write("Status:", resp.status_code)
                st.write("Response:", resp.text)
                data = resp.json()
            except Exception as e:
                st.error(f"Backend unreachable — {e}")
                st.stop()

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # Success header
        st.markdown("""
        <div style="text-align:center; margin-bottom:8px; animation: fadeIn 0.5s ease both;">
            <h3 style="font-size:22px !important; font-weight:800; margin:0 0 6px 0;">Evidence Certified</h3>
            <p style="color:#475569; font-size:13px; margin:0;">Cryptographic signature generated and recorded</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # Result card
        st.markdown('<div class="crd">', unsafe_allow_html=True)

        r1, r2 = st.columns([1.6, 1])
        with r1:
            st.markdown(f'<p class="mi">Filename</p><p class="vl">{data.get("filename","—")}</p>', unsafe_allow_html=True)
        with r2:
            rid = data.get("record_id", "—")
            st.markdown(f'<p class="mi">Record ID</p><p class="vl" style="font-size:30px;font-weight:900;color:#60a5fa;margin-bottom:8px;">#{rid}</p>', unsafe_allow_html=True)

        st.markdown('<hr class="sep">', unsafe_allow_html=True)

        full_hash = data.get("sha256", "")
        short = full_hash[:24] + " … " + full_hash[-12:] if len(full_hash) > 36 else full_hash

        r3, r4 = st.columns([2, 1])
        with r3:
            st.markdown(f'<p class="mi">SHA-256 Hash</p><p class="mn">{short}</p>', unsafe_allow_html=True)
        with r4:
            st.markdown('<p class="mi">Status</p><span class="pill pill-ok">CERTIFIED</span>', unsafe_allow_html=True)

        st.markdown('<hr class="sep">', unsafe_allow_html=True)
        with st.expander("RSA Digital Signature"):
            st.code(data.get("signature", ""), language=None)
        st.markdown('</div>', unsafe_allow_html=True)

        # QR card
        qr_path = data.get("qr_code", "")
        verify_url = data.get("verify_url", "")
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="crd" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown('<p class="mi" style="text-align:center;margin-bottom:18px;">Scan to Verify</p>', unsafe_allow_html=True)

        if qr_path and Path(qr_path).exists():
            _, qc, _ = st.columns([1.3, 1, 1.3])
            with qc:
                st.image(str(qr_path), use_container_width=True)

        if verify_url:
            st.markdown(f"""
            <div style="margin-top:14px;">
                <a href="{verify_url}" target="_blank"
                   style="color:#60a5fa;font-size:12px;font-weight:500;
                          text-decoration:none;word-break:break-all;">{verify_url}</a>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Download
        pdf_path = data.get("pdf", "")
        if pdf_path:
            cert_file = Path(pdf_path)
            if cert_file.exists():
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                with open(cert_file, "rb") as f:
                    st.download_button("Download Certificate PDF", f.read(), cert_file.name, "application/pdf")

    elif certify_clicked:
        st.warning("Select a file first.")


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 4 — VERIFY INTEGRITY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="scene-gap"></div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div id="verify"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="scene scroll-reveal" style="padding-top:100px;">
    <div class="sh">
        <p class="sh-label">Verification</p>
        <h2 class="sh-title">Verify Integrity</h2>
        <p class="sh-sub">Check if a file has been altered since certification.</p>
    </div>
</div>
""", unsafe_allow_html=True)

_, col_v, _ = st.columns([0.8, 2.4, 0.8])

with col_v:
    st.markdown('<div class="crd-up">', unsafe_allow_html=True)

    # Step 1
    st.markdown('<div class="stp"><div class="stp-h"><div class="stp-n">1</div><div class="stp-t">Enter Record ID</div></div></div>', unsafe_allow_html=True)
    record_id = st.number_input("id", min_value=1, step=1, label_visibility="collapsed", help="From the certificate")
    st.markdown('<div class="stp-line"></div>', unsafe_allow_html=True)

    # Step 2
    st.markdown('<div class="stp"><div class="stp-h"><div class="stp-n">2</div><div class="stp-t">Upload Evidence File</div></div></div>', unsafe_allow_html=True)
    verify_file = st.file_uploader("file", type=None, key="verify_up", label_visibility="collapsed")
    st.markdown('<div class="stp-line"></div>', unsafe_allow_html=True)

    # Step 3
    st.markdown('<div class="stp" style="margin-bottom:8px;"><div class="stp-h"><div class="stp-n">3</div><div class="stp-t">Run Verification</div></div></div>', unsafe_allow_html=True)
    verify_clicked = st.button("Verify Evidence", type="primary", key="btn_verify")
    st.markdown('</div>', unsafe_allow_html=True)

    if verify_clicked and verify_file is not None:
        with st.spinner("Analyzing integrity..."):
            try:
                files = {
                    "file": (
                        verify_file.name,
                        verify_file.getvalue(),
                        "application/octet-stream",
                    )
                }
                resp = requests.post(
                    f"{API_BASE}/verify?id={record_id}",
                    files=files,
                    timeout=30,
                )
            except Exception as e:
                st.error(f"Backend unreachable — {e}")
                st.stop()

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        html = resp.text
        html = html.replace('src="/', f'src="{API_BASE}/')
        html = html.replace('href="/', f'href="{API_BASE}/')
        components.html(html, height=850, scrolling=True)

    elif verify_clicked:
        st.warning("Select a file and enter the Record ID.")


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 5 — FEATURES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="scene-gap"></div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown("""
<div class="scene scroll-reveal" style="padding-top:100px;">
    <div class="sh" style="text-align:center;">
        <p class="sh-label" style="text-align:center;">Technology</p>
        <h2 class="sh-title" style="max-width:100%; text-align:center;">Built on Proven Standards</h2>
    </div>
    <div class="feat-grid">
        <div class="feat">
            <div class="feat-ic">#</div>
            <h4>SHA-256 Integrity</h4>
            <p>Every file gets a unique 256-bit fingerprint. Change one byte and the hash changes entirely.</p>
        </div>
        <div class="feat">
            <div class="feat-ic">K</div>
            <h4>RSA-2048 Signatures</h4>
            <p>Certificates are signed with 2048-bit RSA keys for non-repudiation and authenticity.</p>
        </div>
        <div class="feat">
            <div class="feat-ic">&#x27D0;</div>
            <h4>Chain of Custody</h4>
            <p>Timestamped records create an auditable trail from certification to courtroom.</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 6 — ABOUT + FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="scene-gap"></div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div id="about"></div>', unsafe_allow_html=True)

# About header
st.markdown("""
<div class="scene scroll-reveal" style="padding-top:100px;">
    <div class="sh" style="text-align:center;">
        <p class="sh-label" style="text-align:center;">About</p>
        <h2 class="sh-title" style="max-width:100%; text-align:center;">About EvidenceChain</h2>
        <p class="sh-sub" style="text-align:center; max-width:560px; margin:0 auto;">
            A forensic-grade platform for professionals who need
            tamper-proof digital evidence.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Mission hero card
st.markdown("""
<div class="scene" style="padding-bottom:24px;">
    <div class="about-hero">
        <h3>Our Mission</h3>
        <p>
            In legal proceedings, regulatory investigations, and corporate compliance,
            digital evidence is only as strong as its verifiability. EvidenceChain was
            built to close the trust gap &mdash; providing instant, cryptographic proof
            that a file has not been altered since the moment of certification.
        </p>
        <p>
            We combine industry-standard SHA-256 hashing with RSA-2048 digital signatures
            to create certificates that are independently verifiable, tamper-evident, and
            court-admissible &mdash; all without requiring third-party trust.
        </p>
        <div class="about-stat-row">
            <div class="about-stat">
                <h5>256-bit</h5>
                <p>Hash digest length</p>
            </div>
            <div class="about-stat">
                <h5>2048-bit</h5>
                <p>RSA key strength</p>
            </div>
            <div class="about-stat">
                <h5>&lt;1s</h5>
                <p>Verification time</p>
            </div>
            <div class="about-stat">
                <h5>100%</h5>
                <p>Offline capable</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Detail cards
st.markdown("""
<div class="scene" style="padding-bottom:24px;">
    <div class="about-grid">
        <div class="about-block">
            <h4>How It Works</h4>
            <p>
                Upload any file. EvidenceChain computes a SHA-256 hash &mdash; a unique
                256-bit fingerprint. This hash is then signed with a 2048-bit RSA private
                key, producing a digital signature that can be verified by anyone with
                the corresponding public key. The result is packaged into a downloadable
                PDF certificate with an embedded QR code.
            </p>
        </div>
        <div class="about-block">
            <h4>Why It Matters</h4>
            <p>
                Traditional evidence handling relies on trust &mdash; trust that the file
                has not been modified, trust in the chain of custody. Cryptographic
                certification removes the need for trust entirely. The math proves
                integrity. If even a single byte changes, verification fails.
            </p>
        </div>
        <div class="about-block">
            <h4>For Legal Professionals</h4>
            <p>
                Designed for lawyers, investigators, and compliance officers who need
                court-admissible proof of digital evidence integrity. Every certificate
                includes timestamps, hash values, and digital signatures suitable for
                regulatory submissions and litigation.
            </p>
        </div>
        <div class="about-block">
            <h4>For Organizations</h4>
            <p>
                Whether you are preserving whistleblower submissions, audit logs, or
                incident response artifacts, EvidenceChain provides an automated,
                verifiable chain of custody that withstands scrutiny.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Closing quote
st.markdown("""
<div class="scene" style="padding-bottom:60px;">
    <div style="text-align:center; margin-top:32px; padding:40px 24px;">
        <p style="color:#334155 !important; font-size:16px; font-style:italic;
                  line-height:1.8; max-width:520px; margin:0 auto;">
            &ldquo;In digital forensics, if you cannot prove it has not changed,
            you cannot prove anything.&rdquo;
        </p>
        <p style="color:#1e293b !important; font-size:11px; font-weight:700;
                  letter-spacing:2px; text-transform:uppercase; margin-top:16px;">
            Built for proof. Not promises.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="scene-gap"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="ft">
    <p>EvidenceChain &middot; Cryptographic Evidence Verification</p>
</div>
""", unsafe_allow_html=True)
