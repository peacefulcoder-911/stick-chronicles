#!/usr/bin/env python3
"""
Universal Watermark Remover - Interactive Web Application Studio
===============================================================
A web studio for automatic and interactive watermark removal.
Features:
- Pure Vanilla CSS design with glassmorphism, dark mode, glowing accents
- Multi-layer interactive canvas with Brush, Box, Eraser, Pan/Zoom
- Interactive Before/After Split Comparison Slider
- One-click presets & autonomous computer vision / AI auto-detection
- Multi-scale PDE inpainting, texture synthesis, alpha deblending
- Download PNG/JPG & Copy to Clipboard
- Zero external web framework dependencies (built-in http.server)
"""

import os
import io
import json
import base64
import socket
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from pathlib import Path

import numpy as np
from PIL import Image

from watermark_engine import WatermarkEngine

ENGINE = WatermarkEngine()

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>WatermarkX AI — Universal Watermark Remover</title>
  <meta name="description" content="State-of-the-art interactive tool to remove any watermark, logo, stamp, or text overlay from any image cleanly.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #080b11;
      --bg-card: rgba(16, 23, 38, 0.75);
      --bg-card-hover: rgba(22, 32, 54, 0.85);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(99, 102, 241, 0.5);
      --primary: #6366f1;
      --primary-hover: #4f46e5;
      --primary-glow: rgba(99, 102, 241, 0.35);
      --accent-cyan: #06b6d4;
      --accent-coral: #ff4757;
      --accent-green: #10b981;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --text-sub: #64748b;
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 18px;
      --radius-full: 9999px;
      --shadow-glow: 0 0 25px rgba(99, 102, 241, 0.25);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
    }

    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background-color: var(--bg-dark);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 80%, rgba(6, 182, 212, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(16, 23, 38, 0.5) 0%, transparent 100%);
    }

    /* TOP NAVBAR */
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 28px;
      background: rgba(11, 15, 25, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
    }

    .brand-icon {
      width: 38px;
      height: 38px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, var(--primary), var(--accent-cyan));
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 15px var(--primary-glow);
    }

    .brand-icon svg {
      width: 22px;
      height: 22px;
      fill: #ffffff;
    }

    .brand-title {
      font-family: 'Outfit', sans-serif;
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(135deg, #ffffff 40%, #a5b4fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .brand-badge {
      font-size: 0.68rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 3px 8px;
      background: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.3);
      color: #a5b4fc;
      border-radius: var(--radius-full);
      margin-left: 6px;
    }

    .nav-stats {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .status-pill {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.8rem;
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.04);
      padding: 6px 14px;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-color);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent-green);
      box-shadow: 0 0 10px var(--accent-green);
    }

    /* MAIN CONTAINER */
    .app-container {
      display: flex;
      flex: 1;
      height: calc(100vh - 71px);
      overflow: hidden;
    }

    /* SIDEBAR */
    .sidebar {
      width: 360px;
      background: var(--bg-card);
      backdrop-filter: blur(20px);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 20px;
      overflow-y: auto;
      z-index: 10;
    }

    .sidebar-section {
      background: rgba(255, 255, 255, 0.025);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .section-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .section-title {
      font-family: 'Outfit', sans-serif;
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* UPLOAD ZONE */
    .drop-zone {
      border: 2px dashed rgba(99, 102, 241, 0.35);
      border-radius: var(--radius-md);
      padding: 24px 16px;
      text-align: center;
      cursor: pointer;
      background: rgba(99, 102, 241, 0.03);
      transition: all 0.25s ease;
      position: relative;
    }

    .drop-zone:hover, .drop-zone.dragover {
      border-color: var(--primary);
      background: rgba(99, 102, 241, 0.08);
      transform: translateY(-1px);
    }

    .drop-icon {
      width: 36px;
      height: 36px;
      margin: 0 auto 8px;
      color: var(--primary);
    }

    .drop-text {
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-main);
    }

    .drop-subtext {
      font-size: 0.72rem;
      color: var(--text-sub);
      margin-top: 4px;
    }

    #file-input {
      display: none;
    }

    /* TOOL BUTTONS */
    .tool-group {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .btn-tool {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 10px 8px;
      color: var(--text-muted);
      font-size: 0.78rem;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }

    .btn-tool:hover {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-main);
      border-color: rgba(255, 255, 255, 0.15);
    }

    .btn-tool.active {
      background: rgba(99, 102, 241, 0.2);
      border-color: var(--primary);
      color: #ffffff;
      box-shadow: 0 0 12px rgba(99, 102, 241, 0.3);
    }

    .btn-tool svg {
      width: 18px;
      height: 18px;
    }

    /* PRESETS GRID */
    .preset-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }

    .btn-preset {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 8px 10px;
      color: var(--text-muted);
      font-size: 0.76rem;
      text-align: left;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }

    .btn-preset:hover {
      background: rgba(99, 102, 241, 0.15);
      border-color: rgba(99, 102, 241, 0.4);
      color: var(--text-main);
    }

    /* AUTO DETECT BUTTONS */
    .btn-detect {
      width: 100%;
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(99, 102, 241, 0.15));
      border: 1px solid rgba(6, 182, 212, 0.3);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      color: #67e8f9;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.2s ease;
    }

    .btn-detect:hover {
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.25), rgba(99, 102, 241, 0.25));
      border-color: var(--accent-cyan);
      box-shadow: 0 0 16px rgba(6, 182, 212, 0.2);
    }

    /* SLIDERS */
    .control-row {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .control-label {
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    .control-val {
      font-family: 'JetBrains Mono', monospace;
      color: var(--accent-cyan);
      font-weight: 500;
    }

    input[type="range"] {
      -webkit-appearance: none;
      width: 100%;
      height: 5px;
      border-radius: 5px;
      background: rgba(255, 255, 255, 0.1);
      outline: none;
    }

    input[type="range"]::-webkit-slider-thumb {
      -webkit-appearance: none;
      width: 15px;
      height: 15px;
      border-radius: 50%;
      background: var(--primary);
      cursor: pointer;
      box-shadow: 0 0 8px var(--primary);
      transition: transform 0.15s ease;
    }

    input[type="range"]::-webkit-slider-thumb:hover {
      transform: scale(1.2);
    }

    /* SELECT DROPDOWN */
    .select-dropdown {
      width: 100%;
      background: rgba(11, 15, 25, 0.8);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 8px 12px;
      color: var(--text-main);
      font-size: 0.8rem;
      outline: none;
      cursor: pointer;
    }

    .select-dropdown:focus {
      border-color: var(--primary);
    }

    /* PRIMARY CTA BUTTON */
    .btn-primary {
      background: linear-gradient(135deg, var(--primary) 0%, #4338ca 100%);
      color: #ffffff;
      border: none;
      border-radius: var(--radius-md);
      padding: 14px 18px;
      font-size: 0.92rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      box-shadow: 0 4px 20px var(--primary-glow);
      transition: all 0.25s ease;
    }

    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 25px rgba(99, 102, 241, 0.5);
    }

    .btn-primary:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      filter: grayscale(0.5);
    }

    /* WORKSPACE CANVAS AREA */
    .workspace {
      flex: 1;
      display: flex;
      flex-direction: column;
      position: relative;
      background: #05070c;
      overflow: hidden;
    }

    /* WORKSPACE TOOLBAR */
    .canvas-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 20px;
      background: rgba(16, 23, 38, 0.5);
      border-bottom: 1px solid var(--border-color);
      z-index: 5;
    }

    .canvas-tools {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .btn-icon {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 6px 10px;
      color: var(--text-muted);
      font-size: 0.8rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }

    .btn-icon:hover {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-main);
    }

    .viewport {
      flex: 1;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      cursor: crosshair;
      user-select: none;
    }

    .canvas-stage {
      position: relative;
      transform-origin: center center;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
      border-radius: 4px;
      overflow: hidden;
    }

    #image-canvas, #mask-canvas, #result-canvas {
      position: absolute;
      top: 0;
      left: 0;
    }

    #image-canvas {
      z-index: 1;
    }

    #mask-canvas {
      z-index: 2;
      opacity: 0.65;
    }

    #result-canvas {
      z-index: 3;
      display: none;
    }

    /* COMPARISON SPLIT SLIDER */
    .split-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 4;
      pointer-events: none;
      display: none;
    }

    .split-line {
      position: absolute;
      top: 0;
      bottom: 0;
      width: 3px;
      background: #ffffff;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.8), 0 0 6px var(--primary);
      cursor: ew-resize;
      pointer-events: all;
    }

    .split-handle {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--primary);
      border: 3px solid #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }

    .split-handle svg {
      width: 16px;
      height: 16px;
      fill: #ffffff;
    }

    /* EMPTY STATE */
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      color: var(--text-sub);
      text-align: center;
      max-width: 400px;
    }

    .empty-icon {
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background: rgba(99, 102, 241, 0.08);
      border: 1px solid rgba(99, 102, 241, 0.2);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--primary);
    }

    /* SPINNER & MODAL */
    .loading-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(8, 11, 17, 0.8);
      backdrop-filter: blur(8px);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      z-index: 50;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }

    .loading-overlay.active {
      opacity: 1;
      pointer-events: all;
    }

    .spinner {
      width: 48px;
      height: 48px;
      border: 3px solid rgba(99, 102, 241, 0.15);
      border-top-color: var(--primary);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .loading-text {
      font-family: 'Outfit', sans-serif;
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text-main);
    }

    /* TOAST */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(16, 23, 38, 0.95);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 12px 20px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 0.85rem;
      z-index: 999;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }

    .toast-icon {
      color: var(--accent-green);
    }
  </style>
</head>
<body>

  <!-- TOP HEADER -->
  <header>
    <a href="#" class="brand">
      <div class="brand-icon">
        <svg viewBox="0 0 24 24"><path d="M19.5 12c0-.23-.01-.45-.03-.68l1.86-1.41c.17-.13.22-.38.12-.56l-1.76-3.05c-.1-.18-.32-.25-.51-.18l-2.19.88c-.46-.35-.95-.65-1.48-.87l-.33-2.33c-.03-.2-.2-.35-.4-.35h-3.52c-.2 0-.37.15-.4.35l-.33 2.33c-.53.22-1.02.52-1.48.87l-2.19-.88c-.19-.07-.41 0-.51.18l-1.76 3.05c-.1.18-.05.43.12.56l1.86 1.41c-.02.23-.03.45-.03.68s.01.45.03.68l-1.86 1.41c-.17.13-.22.38-.12.56l1.76 3.05c.1.18.32.25.51.18l2.19-.88c.46.35.95.65 1.48.87l.33 2.33c.03.2.2.35.4.35h3.52c.2 0 .37-.15.4-.35l.33-2.33c.53-.22 1.02-.52 1.48-.87l2.19.88c.19.07.41 0 .51-.18l1.76-3.05c.1-.18.05-.43-.12-.56l-1.86-1.41c.02-.23.03-.45.03-.68zm-7.5 3c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/></svg>
      </div>
      <div>
        <span class="brand-title">WatermarkX</span>
        <span class="brand-badge">Universal AI Engine</span>
      </div>
    </a>

    <div class="nav-stats">
      <div class="status-pill">
        <div class="status-dot"></div>
        <span id="engine-status">Multi-Scale PDE & Texture Engine Ready</span>
      </div>
      <button class="btn-icon" id="btn-copy-clipboard" title="Copy clean image to clipboard" disabled>
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
        Copy
      </button>
      <button class="btn-primary" id="btn-download" style="padding: 8px 16px; font-size: 0.84rem;" disabled>
        <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
        Download Clean
      </button>
    </div>
  </header>

  <!-- APP MAIN CONTAINER -->
  <div class="app-container">
    
    <!-- LEFT SIDEBAR CONTROLS -->
    <aside class="sidebar">
      
      <!-- Upload Box -->
      <div class="sidebar-section">
        <div class="section-title">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
          Source Image
        </div>
        <div class="drop-zone" id="drop-zone">
          <svg class="drop-icon" fill="currentColor" viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/></svg>
          <div class="drop-text">Drop image here or click to browse</div>
          <div class="drop-subtext">Supports PNG, JPG, WebP, BMP (or Paste Ctrl+V)</div>
          <input type="file" id="file-input" accept="image/*">
        </div>
      </div>

      <!-- Auto Detectors -->
      <div class="sidebar-section">
        <div class="section-title">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
          Autonomous Detection
        </div>
        <button class="btn-detect" id="btn-auto-detect">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
          ⚡ Auto-Detect Watermark (CV)
        </button>
        <button class="btn-detect" id="btn-ai-detect" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(236, 72, 153, 0.15)); border-color: rgba(236, 72, 153, 0.3); color: #f472b6;">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14l-5-5 1.41-1.41L12 14.17l7.59-7.59L21 8l-9 9z"/></svg>
          🤖 AI Vision Detect (Gemini)
        </button>
      </div>

      <!-- Quick Presets -->
      <div class="sidebar-section">
        <div class="section-title">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
          Standard Presets
        </div>
        <div class="preset-grid">
          <button class="btn-preset" data-preset="gemini-sparkle" style="grid-column: span 2; background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(6, 182, 212, 0.3)); border-color: var(--accent-cyan); color: #ffffff; font-weight: 600; padding: 10px 12px; box-shadow: 0 0 12px rgba(6, 182, 212, 0.25);">⭐ Gemini / Imagen Sparkle (Bottom)</button>
          <button class="btn-preset" data-preset="bottom-right">↘️ Bottom-Right</button>
          <button class="btn-preset" data-preset="bottom-left">↙️ Bottom-Left</button>
          <button class="btn-preset" data-preset="top-right">↗️ Top-Right</button>
          <button class="btn-preset" data-preset="top-left">↖️ Top-Left</button>
          <button class="btn-preset" data-preset="bottom-banner">➖ Bottom Banner</button>
          <button class="btn-preset" data-preset="full-tiled">🌐 Full Tiled Grid</button>
        </div>
      </div>

      <!-- Drawing Tools -->
      <div class="sidebar-section">
        <div class="section-title">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M7 14c-1.66 0-3 1.34-3 3 0 1.31-1.16 2-2 2 .92 1.22 2.49 2 4 2 2.21 0 4-1.79 4-4 0-1.66-1.34-3-3-3zm13.71-9.37l-1.34-1.34a.996.996 0 0 0-1.41 0L9 12.25 11.75 15l8.96-8.96c.39-.39.39-1.02 0-1.41z"/></svg>
          Interactive Tools
        </div>
        <div class="tool-group">
          <button class="btn-tool active" id="tool-brush">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 14c-1.66 0-3 1.34-3 3 0 1.31-1.16 2-2 2 .92 1.22 2.49 2 4 2 2.21 0 4-1.79 4-4 0-1.66-1.34-3-3-3zm13.71-9.37l-1.34-1.34a.996.996 0 0 0-1.41 0L9 12.25 11.75 15l8.96-8.96c.39-.39.39-1.02 0-1.41z"/></svg>
            Brush
          </button>
          <button class="btn-tool" id="tool-box">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/></svg>
            Box
          </button>
          <button class="btn-tool" id="tool-eraser">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.14 3c-.43 0-.85.17-1.17.49l-8.5 8.5c-.64.64-.64 1.69 0 2.33l6.5 6.5c.32.32.74.49 1.17.49h7.86v-2H13.6l-5-5 8.29-8.29c.64-.64.64-1.69 0-2.33l-1.58-1.58c-.32-.32-.74-.49-1.17-.49z"/></svg>
            Eraser
          </button>
        </div>

        <div class="control-row">
          <div class="control-label">
            <span>Brush Size</span>
            <span class="control-val" id="val-brush-size">28px</span>
          </div>
          <input type="range" id="brush-size" min="6" max="120" value="28">
        </div>

        <div class="control-row">
          <div class="control-label">
            <span>Mask Expansion (Halo Removal)</span>
            <span class="control-val" id="val-dilation">4px</span>
          </div>
          <input type="range" id="dilation-slider" min="0" max="16" value="4">
        </div>
      </div>

      <!-- Algorithm Engine -->
      <div class="sidebar-section">
        <div class="section-title">
          <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2-1.09V17h2V9L12 3zm6.82 6L12 12.72 5.18 9 12 5.28 18.82 9zM17 15.99l-5 2.73-5-2.73v-3.72L12 15l5-2.73v3.72z"/></svg>
          Inpainting Algorithm
        </div>
        <select class="select-dropdown" id="algorithm-select">
          <option value="pde_multiscale" selected>⚡ Multi-Scale Laplacian PDE (Fast, Smooth Fill)</option>
          <option value="texture_synthesis">🎨 Texture Match Synthesis (Grain & Patterns)</option>
          <option value="alpha_deblend">✨ Semi-Transparent Inversion (Shutterstock/Stock)</option>
          <option value="directional_diffusion">📐 Directional Diffusion (Sharp Edge Boundaries)</option>
        </select>
      </div>

      <!-- Action Button -->
      <button class="btn-primary" id="btn-remove-watermark" disabled>
        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM10 17l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
        Remove Watermark
      </button>

    </aside>

    <!-- RIGHT WORKSPACE AREA -->
    <main class="workspace">
      
      <!-- Canvas Bar Controls -->
      <div class="canvas-bar">
        <div class="canvas-tools">
          <button class="btn-icon" id="btn-undo" title="Undo stroke">
            <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24"><path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/></svg>
            Undo
          </button>
          <button class="btn-icon" id="btn-clear-mask" title="Clear drawn mask">
            <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            Clear Mask
          </button>
          <button class="btn-icon" id="btn-toggle-compare" style="display: none;">
            <svg width="15" height="15" fill="currentColor" viewBox="0 0 24 24"><path d="M10 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h5v2h2V1h-2v2zm-5 16V5h5v14H5zm14-16h-5v2h5v14h-5v2h5c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/></svg>
            Compare Split
          </button>
        </div>

        <div class="canvas-tools">
          <button class="btn-icon" id="btn-zoom-out" title="Zoom Out">−</button>
          <span style="font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;" id="zoom-text">100%</span>
          <button class="btn-icon" id="btn-zoom-in" title="Zoom In">+</button>
          <button class="btn-icon" id="btn-zoom-reset" title="Reset View">Reset</button>
        </div>
      </div>

      <!-- Canvas Viewport -->
      <div class="viewport" id="viewport">
        
        <!-- Empty State Prompt -->
        <div class="empty-state" id="empty-state">
          <div class="empty-icon">
            <svg width="32" height="32" fill="currentColor" viewBox="0 0 24 24"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
          </div>
          <h2 style="font-family: 'Outfit'; font-size: 1.25rem; font-weight: 600; color: #ffffff;">No Image Loaded</h2>
          <p style="font-size: 0.85rem; line-height: 1.5;">Drag and drop any watermarked image into the window, or click the upload area on the left to get started.</p>
        </div>

        <!-- Canvas Stage -->
        <div class="canvas-stage" id="canvas-stage" style="display: none;">
          <canvas id="image-canvas"></canvas>
          <canvas id="mask-canvas"></canvas>
          <canvas id="result-canvas"></canvas>

          <!-- Split Slider Line -->
          <div class="split-container" id="split-container">
            <div class="split-line" id="split-line">
              <div class="split-handle">
                <svg viewBox="0 0 24 24"><path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/></svg>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Loading Overlay -->
      <div class="loading-overlay" id="loading-overlay">
        <div class="spinner"></div>
        <div class="loading-text" id="loading-text">Inpainting Watermark...</div>
        <p style="font-size: 0.8rem; color: var(--text-muted);">Solving multi-scale boundary harmonics</p>
      </div>

    </main>
  </div>

  <!-- Toast Notification -->
  <div class="toast" id="toast">
    <svg class="toast-icon" width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
    <span id="toast-message">Watermark removed cleanly!</span>
  </div>

  <script>
    // State management
    const state = {
      image: null,
      imageWidth: 0,
      imageHeight: 0,
      currentTool: 'brush', // 'brush', 'box', 'eraser'
      brushSize: 28,
      dilation: 4,
      zoom: 1.0,
      panX: 0,
      panY: 0,
      isDrawing: false,
      isPanning: false,
      boxStartX: 0,
      boxStartY: 0,
      history: [],
      cleanImageBase64: null,
      isCompareMode: false,
      splitPos: 0.5
    };

    // DOM Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const viewport = document.getElementById('viewport');
    const canvasStage = document.getElementById('canvas-stage');
    const emptyState = document.getElementById('empty-state');
    const imageCanvas = document.getElementById('image-canvas');
    const maskCanvas = document.getElementById('mask-canvas');
    const resultCanvas = document.getElementById('result-canvas');
    const splitContainer = document.getElementById('split-container');
    const splitLine = document.getElementById('split-line');
    const btnRemove = document.getElementById('btn-remove-watermark');
    const btnDownload = document.getElementById('btn-download');
    const btnCopy = document.getElementById('btn-copy-clipboard');
    const btnAutoDetect = document.getElementById('btn-auto-detect');
    const btnAiDetect = document.getElementById('btn-ai-detect');
    const btnClearMask = document.getElementById('btn-clear-mask');
    const btnUndo = document.getElementById('btn-undo');
    const btnCompare = document.getElementById('btn-toggle-compare');
    const brushSizeSlider = document.getElementById('brush-size');
    const dilationSlider = document.getElementById('dilation-slider');
    const valBrushSize = document.getElementById('val-brush-size');
    const valDilation = document.getElementById('val-dilation');
    const algorithmSelect = document.getElementById('algorithm-select');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    const imgCtx = imageCanvas.getContext('2d');
    const maskCtx = maskCanvas.getContext('2d');
    const resCtx = resultCanvas.getContext('2d');

    // Show Toast
    function showToast(msg) {
      toastMessage.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3500);
    }

    // Set Loading
    function setLoading(isLoading, text = "Processing...") {
      loadingText.textContent = text;
      if (isLoading) loadingOverlay.classList.add('active');
      else loadingOverlay.classList.remove('active');
    }

    // File Drag & Drop
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length) handleFile(e.target.files[0]);
    });

    // Clipboard Paste Listener (Ctrl+V / Cmd+V)
    window.addEventListener('paste', (e) => {
      const items = e.clipboardData?.items;
      if (!items) return;
      for (let item of items) {
        if (item.type.startsWith('image/')) {
          handleFile(item.getAsFile());
          showToast("Image pasted from clipboard!");
          break;
        }
      }
    });

    function handleFile(file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          state.image = img;
          state.imageWidth = img.naturalWidth;
          state.imageHeight = img.naturalHeight;
          state.cleanImageBase64 = null;
          state.history = [];
          
          initCanvas();
          emptyState.style.display = 'none';
          canvasStage.style.display = 'block';
          btnRemove.disabled = false;
          btnDownload.disabled = true;
          btnCopy.disabled = true;
          btnCompare.style.display = 'none';
          showToast(`Loaded ${file.name || 'image'} (${state.imageWidth}×${state.imageHeight})`);
        };
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
    }

    function initCanvas() {
      const w = state.imageWidth;
      const h = state.imageHeight;

      imageCanvas.width = w;
      imageCanvas.height = h;
      maskCanvas.width = w;
      maskCanvas.height = h;
      resultCanvas.width = w;
      resultCanvas.height = h;

      canvasStage.style.width = `${w}px`;
      canvasStage.style.height = `${h}px`;

      imgCtx.clearRect(0, 0, w, h);
      imgCtx.drawImage(state.image, 0, 0);

      clearMask();
      fitStageToViewport();
    }

    function fitStageToViewport() {
      const vpW = viewport.clientWidth - 40;
      const vpH = viewport.clientHeight - 40;
      const scaleX = vpW / state.imageWidth;
      const scaleY = vpH / state.imageHeight;
      state.zoom = Math.min(1.0, scaleX, scaleY);
      state.panX = 0;
      state.panY = 0;
      updateTransform();
    }

    function updateTransform() {
      canvasStage.style.transform = `translate(${state.panX}px, ${state.panY}px) scale(${state.zoom})`;
      document.getElementById('zoom-text').textContent = `${Math.round(state.zoom * 100)}%`;
    }

    // Zoom buttons
    document.getElementById('btn-zoom-in').addEventListener('click', () => { state.zoom = Math.min(4.0, state.zoom * 1.25); updateTransform(); });
    document.getElementById('btn-zoom-out').addEventListener('click', () => { state.zoom = Math.max(0.15, state.zoom / 1.25); updateTransform(); });
    document.getElementById('btn-zoom-reset').addEventListener('click', fitStageToViewport);

    viewport.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      state.zoom = Math.max(0.15, Math.min(5.0, state.zoom * zoomFactor));
      updateTransform();
    }, { passive: false });

    // Tool switching
    const toolBtns = {
      brush: document.getElementById('tool-brush'),
      box: document.getElementById('tool-box'),
      eraser: document.getElementById('tool-eraser')
    };

    function setTool(toolName) {
      state.currentTool = toolName;
      Object.keys(toolBtns).forEach(k => toolBtns[k].classList.toggle('active', k === toolName));
    }

    toolBtns.brush.addEventListener('click', () => setTool('brush'));
    toolBtns.box.addEventListener('click', () => setTool('box'));
    toolBtns.eraser.addEventListener('click', () => setTool('eraser'));

    brushSizeSlider.addEventListener('input', (e) => {
      state.brushSize = parseInt(e.target.value);
      valBrushSize.textContent = `${state.brushSize}px`;
    });

    dilationSlider.addEventListener('input', (e) => {
      state.dilation = parseInt(e.target.value);
      valDilation.textContent = `${state.dilation}px`;
    });

    // Save mask history for Undo
    function saveHistory() {
      const copy = document.createElement('canvas');
      copy.width = maskCanvas.width;
      copy.height = maskCanvas.height;
      copy.getContext('2d').drawImage(maskCanvas, 0, 0);
      state.history.push(copy);
      if (state.history.length > 20) state.history.shift();
    }

    btnUndo.addEventListener('click', () => {
      if (!state.history.length) return;
      const prev = state.history.pop();
      maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
      maskCtx.drawImage(prev, 0, 0);
    });

    function clearMask() {
      saveHistory();
      maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
    }
    btnClearMask.addEventListener('click', clearMask);

    // Coordinate conversion
    function getCanvasCoords(e) {
      const rect = canvasStage.getBoundingClientRect();
      const clientX = e.clientX ?? (e.touches && e.touches[0].clientX);
      const clientY = e.clientY ?? (e.touches && e.touches[0].clientY);
      const x = (clientX - rect.left) / state.zoom;
      const y = (clientY - rect.top) / state.zoom;
      return { x, y };
    }

    // Mask Drawing Events
    viewport.addEventListener('mousedown', (e) => {
      if (!state.image) return;
      if (e.button === 1 || e.spaceKey) {
        state.isPanning = true;
        return;
      }
      if (e.button !== 0) return;

      saveHistory();
      state.isDrawing = true;
      const coords = getCanvasCoords(e);
      state.boxStartX = coords.x;
      state.boxStartY = coords.y;

      if (state.currentTool === 'brush' || state.currentTool === 'eraser') {
        drawStroke(coords.x, coords.y, true);
      }
    });

    window.addEventListener('mousemove', (e) => {
      if (state.isPanning) {
        state.panX += e.movementX;
        state.panY += e.movementY;
        updateTransform();
        return;
      }
      if (!state.isDrawing) return;

      const coords = getCanvasCoords(e);
      if (state.currentTool === 'brush' || state.currentTool === 'eraser') {
        drawStroke(coords.x, coords.y);
      } else if (state.currentTool === 'box') {
        // Redraw preview from last history
        maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
        if (state.history.length) {
          maskCtx.drawImage(state.history[state.history.length - 1], 0, 0);
        }
        maskCtx.fillStyle = 'rgba(255, 71, 87, 0.75)';
        const bx = Math.min(state.boxStartX, coords.x);
        const by = Math.min(state.boxStartY, coords.y);
        const bw = Math.abs(coords.x - state.boxStartX);
        const bh = Math.abs(coords.y - state.boxStartY);
        maskCtx.fillRect(bx, by, bw, bh);
      }
    });

    window.addEventListener('mouseup', () => {
      state.isDrawing = false;
      state.isPanning = false;
    });

    function drawStroke(x, y, isStart = false) {
      maskCtx.lineWidth = state.brushSize;
      maskCtx.lineCap = 'round';
      maskCtx.lineJoin = 'round';

      if (state.currentTool === 'eraser') {
        maskCtx.globalCompositeOperation = 'destination-out';
      } else {
        maskCtx.globalCompositeOperation = 'source-over';
        maskCtx.strokeStyle = 'rgba(255, 71, 87, 0.85)';
        maskCtx.fillStyle = 'rgba(255, 71, 87, 0.85)';
      }

      if (isStart) {
        maskCtx.beginPath();
        maskCtx.arc(x, y, state.brushSize / 2, 0, Math.PI * 2);
        maskCtx.fill();
        maskCtx.beginPath();
        maskCtx.moveTo(x, y);
      } else {
        maskCtx.lineTo(x, y);
        maskCtx.stroke();
      }
    }

    // PRESET BUTTONS
    document.querySelectorAll('.btn-preset').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!state.image) {
          showToast("Please upload an image first!");
          return;
        }
        const preset = btn.dataset.preset;
        setLoading(true, `Applying ${preset} preset...`);
        try {
          const res = await fetch('/api/presets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ preset, width: state.imageWidth, height: state.imageHeight })
          });
          const data = await res.json();
          if (data.mask_base64) {
            saveHistory();
            const maskImg = new Image();
            maskImg.onload = () => {
              maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
              maskCtx.drawImage(maskImg, 0, 0);
              setLoading(false);
              showToast(`Applied preset: ${preset}`);
            };
            maskImg.src = data.mask_base64;
          }
        } catch (err) {
          setLoading(false);
          showToast("Error loading preset: " + err.message);
        }
      });
    });

    // AUTO DETECT (CV)
    btnAutoDetect.addEventListener('click', async () => {
      if (!state.image) return showToast("Upload an image first!");
      setLoading(true, "Scanning image for watermarks (Computer Vision)...");
      try {
        const res = await fetch('/api/detect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: imageCanvas.toDataURL('image/png'),
            method: 'cv'
          })
        });
        const data = await res.json();
        if (data.mask_base64) {
          saveHistory();
          const maskImg = new Image();
          maskImg.onload = () => {
            maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
            maskCtx.drawImage(maskImg, 0, 0);
            setLoading(false);
            showToast(`Detected ${data.boxes.length} watermark region(s)!`);
          };
          maskImg.src = data.mask_base64;
        } else {
          setLoading(false);
          showToast("No watermarks detected.");
        }
      } catch (err) {
        setLoading(false);
        showToast("Detection failed: " + err.message);
      }
    });

    // AI VISION DETECT (GEMINI)
    btnAiDetect.addEventListener('click', async () => {
      if (!state.image) return showToast("Upload an image first!");
      setLoading(true, "Querying Gemini 2.5 Flash Vision...");
      try {
        const res = await fetch('/api/detect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: imageCanvas.toDataURL('image/png'),
            method: 'ai'
          })
        });
        const data = await res.json();
        if (data.mask_base64) {
          saveHistory();
          const maskImg = new Image();
          maskImg.onload = () => {
            maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
            maskCtx.drawImage(maskImg, 0, 0);
            setLoading(false);
            showToast(`AI detected ${data.boxes.length} watermark(s)!`);
          };
          maskImg.src = data.mask_base64;
        } else {
          setLoading(false);
          showToast("AI found no watermarks.");
        }
      } catch (err) {
        setLoading(false);
        showToast("AI detection failed: " + err.message);
      }
    });

    // INPAINT / REMOVE WATERMARK
    btnRemove.addEventListener('click', async () => {
      if (!state.image) return;
      
      // If no mask has been painted or selected, automatically detect Gemini / corner watermark!
      const maskData = maskCtx.getImageData(0, 0, maskCanvas.width, maskCanvas.height).data;
      let hasMask = false;
      for (let i = 3; i < maskData.length; i += 4) {
        if (maskData[i] > 20) { hasMask = true; break; }
      }
      
      if (!hasMask) {
        setLoading(true, "Auto-detecting Gemini sparkle watermark...");
        try {
          const detRes = await fetch('/api/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              image_base64: imageCanvas.toDataURL('image/png'),
              method: 'cv'
            })
          });
          const detData = await detRes.json();
          if (detData.mask_base64) {
            saveHistory();
            await new Promise(resolve => {
              const maskImg = new Image();
              maskImg.onload = () => {
                maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
                maskCtx.drawImage(maskImg, 0, 0);
                resolve();
              };
              maskImg.src = detData.mask_base64;
            });
            hasMask = true;
          }
        } catch (e) {
          console.error("Auto detect failed", e);
        }

        // Fallback to gemini-sparkle preset if detection didn't trigger
        if (!hasMask) {
          try {
            const presRes = await fetch('/api/presets', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ preset: 'gemini-sparkle', width: state.imageWidth, height: state.imageHeight })
            });
            const presData = await presRes.json();
            if (presData.mask_base64) {
              saveHistory();
              await new Promise(resolve => {
                const maskImg = new Image();
                maskImg.onload = () => {
                  maskCtx.clearRect(0, 0, maskCanvas.width, maskCanvas.height);
                  maskCtx.drawImage(maskImg, 0, 0);
                  resolve();
                };
                maskImg.src = presData.mask_base64;
              });
              hasMask = true;
            }
          } catch (e) {
            console.error("Preset fallback failed", e);
          }
        }
      }

      setLoading(true, "Inpainting and restoring background...");
      const t0 = performance.now();
      try {
        const res = await fetch('/api/inpaint', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image_base64: imageCanvas.toDataURL('image/png'),
            mask_base64: maskCanvas.toDataURL('image/png'),
            method: algorithmSelect.value,
            dilation: state.dilation
          })
        });
        const data = await res.json();
        if (data.success && data.clean_image_base64) {
          state.cleanImageBase64 = data.clean_image_base64;
          const cleanImg = new Image();
          cleanImg.onload = () => {
            resCtx.clearRect(0, 0, resultCanvas.width, resultCanvas.height);
            resCtx.drawImage(cleanImg, 0, 0);
            
            // Switch to result view
            resultCanvas.style.display = 'block';
            maskCanvas.style.display = 'none';
            btnDownload.disabled = false;
            btnCopy.disabled = false;
            btnCompare.style.display = 'flex';
            
            setLoading(false);
            const elapsed = Math.round(performance.now() - t0);
            showToast(`Watermark removed in ${elapsed}ms!`);
          };
          cleanImg.src = data.clean_image_base64;
        } else {
          setLoading(false);
          showToast("Inpainting failed: " + (data.error || "Unknown error"));
        }
      } catch (err) {
        setLoading(false);
        showToast("Error: " + err.message);
      }
    });

    // COMPARE SPLIT SLIDER
    btnCompare.addEventListener('click', () => {
      state.isCompareMode = !state.isCompareMode;
      btnCompare.classList.toggle('active', state.isCompareMode);
      if (state.isCompareMode) {
        splitContainer.style.display = 'block';
        updateSplit(0.5);
      } else {
        splitContainer.style.display = 'none';
        resultCanvas.style.clipPath = 'none';
      }
    });

    function updateSplit(pct) {
      state.splitPos = pct;
      const w = state.imageWidth;
      const x = w * pct;
      splitLine.style.left = `${x}px`;
      resultCanvas.style.clipPath = `polygon(${x}px 0, ${w}px 0, ${w}px 100%, ${x}px 100%)`;
    }

    let isSliding = false;
    splitLine.addEventListener('mousedown', (e) => { e.stopPropagation(); isSliding = true; });
    window.addEventListener('mousemove', (e) => {
      if (!isSliding) return;
      const rect = canvasStage.getBoundingClientRect();
      const x = (e.clientX - rect.left) / state.zoom;
      const pct = Math.max(0.01, Math.min(0.99, x / state.imageWidth));
      updateSplit(pct);
    });
    window.addEventListener('mouseup', () => { isSliding = false; });

    // DOWNLOAD
    btnDownload.addEventListener('click', () => {
      if (!state.cleanImageBase64) return;
      const a = document.createElement('a');
      a.href = state.cleanImageBase64;
      a.download = `watermark_removed_${Date.now()}.png`;
      a.click();
      showToast("Download started!");
    });

    // COPY TO CLIPBOARD
    btnCopy.addEventListener('click', async () => {
      if (!state.cleanImageBase64) return;
      try {
        const blob = await (await fetch(state.cleanImageBase64)).blob();
        await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
        showToast("Clean image copied to clipboard!");
      } catch (err) {
        showToast("Copy error: " + err.message);
      }
    });
  </script>
</body>
</html>
"""

class WatermarkStudioHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200):
        def _json_default(o):
            if isinstance(o, (np.integer, np.int64, np.int32)):
                return int(o)
            if isinstance(o, (np.floating, np.float32, np.float64)):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
            return str(o)

        body = json.dumps(data, default=_json_default).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ["/", "/index.html"]:
            body = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
        elif parsed.path == "/api/status":
            self._send_json({"status": "ready", "has_gemini": bool(ENGINE.gemini_client)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8")
        try:
            payload = json.loads(body) if body else {}
        except Exception:
            payload = {}

        if parsed.path == "/api/presets":
            preset = payload.get("preset", "bottom-right")
            w = int(payload.get("width", 1000))
            h = int(payload.get("height", 1000))
            mask_np = ENGINE.get_preset_mask(w, h, preset)
            
            # Convert mask to base64 RGBA image
            rgba = np.zeros((h, w, 4), dtype=np.uint8)
            rgba[mask_np] = [255, 71, 87, 200]
            pil_mask = Image.fromarray(rgba, "RGBA")
            buf = io.BytesIO()
            pil_mask.save(buf, format="PNG")
            b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
            self._send_json({"preset": preset, "mask_base64": b64})

        elif parsed.path == "/api/detect":
            img_b64 = payload.get("image_base64", "")
            method = payload.get("method", "cv")
            
            if "," in img_b64:
                img_b64 = img_b64.split(",", 1)[1]
            raw_bytes = base64.b64decode(img_b64)
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            
            if method == "ai":
                res = ENGINE.auto_detect_watermarks_ai(img)
            else:
                res = ENGINE.auto_detect_watermarks_cv(img)

            mask_np = res["mask"]
            h, w = mask_np.shape
            rgba = np.zeros((h, w, 4), dtype=np.uint8)
            rgba[mask_np] = [255, 71, 87, 210]
            pil_mask = Image.fromarray(rgba, "RGBA")
            buf = io.BytesIO()
            pil_mask.save(buf, format="PNG")
            b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")
            
            self._send_json({
                "method": res["method"],
                "boxes": res.get("detected_boxes", []),
                "mask_base64": b64
            })

        elif parsed.path == "/api/inpaint":
            img_b64 = payload.get("image_base64", "")
            mask_b64 = payload.get("mask_base64", "")
            method = payload.get("method", "pde_multiscale")
            dilation = int(payload.get("dilation", 4))

            if "," in img_b64:
                img_b64 = img_b64.split(",", 1)[1]
            if "," in mask_b64:
                mask_b64 = mask_b64.split(",", 1)[1]

            img = Image.open(io.BytesIO(base64.b64decode(img_b64))).convert("RGB")
            mask_img = Image.open(io.BytesIO(base64.b64decode(mask_b64))).convert("RGBA")
            
            # Mask is True wherever alpha > 20
            mask_np = np.array(mask_img)[:, :, 3] > 20

            clean_pil = ENGINE.inpaint(img, mask_np, method=method, dilation=dilation)
            
            buf = io.BytesIO()
            clean_pil.save(buf, format="PNG")
            res_b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

            self._send_json({
                "success": True,
                "clean_image_base64": res_b64
            })
        else:
            self.send_response(404)
            self.end_headers()

def launch_web_app(port: int = 7860, open_browser: bool = True):
    server_address = ("", port)
    try:
        httpd = ThreadingHTTPServer(server_address, WatermarkStudioHandler)
    except OSError:
        port = port + 1
        server_address = ("", port)
        httpd = ThreadingHTTPServer(server_address, WatermarkStudioHandler)

    url = f"http://localhost:{port}"
    print(f"\n=======================================================")
    print(f"✨ WatermarkX Studio is live at: {url}")
    print(f"🎨 Open the URL in your browser to remove watermarks interactively.")
    print(f"Press Ctrl+C to stop.")
    print(f"=======================================================\n")
    
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping WatermarkX Studio server...")
        httpd.server_close()

if __name__ == "__main__":
    launch_web_app(port=7860)
