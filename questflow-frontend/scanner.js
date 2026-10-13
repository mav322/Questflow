/**
 * ==============================================================================
 * QUESTFLOW // React Bits <Scanner /> — Vanilla WebGL2 Port
 * Exact port of the React Bits Scanner component for non-React use.
 * Uses raw WebGL2 (identical shader to the original OGL-based component).
 *
 * Props (from user's BG Studio configuration):
 *   color1: #BAFF5C, color2: #BAFF5C, color3: #FFFFFF
 *   speed: 0.85, sweepSpeed: 0.25, sweepWidth: 1.6, sweepFalloff: 6
 *   scale: 1.5, frequency: 2, ripple: 0.22, bandDensity: 11
 *   lineSharpness: 5.5, glow: 0.22, scanDirection: vertical
 *   colorSpread: 0.7, brightness: 1.0, contrast: 1.15, softness: 1.4
 *   vignette: 0.45, scanline: true, grain: true, grainIntensity: 0.05
 *   opacity: 1.0, mouseInteraction: true, mouseRadius: 0.5, mouseStrength: 0.5
 * ==============================================================================
 */

(function () {
  'use strict';

  // ---- Helpers ----
  function hexToRgb(hex) {
    var r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!r) return [1, 1, 1];
    return [parseInt(r[1], 16) / 255, parseInt(r[2], 16) / 255, parseInt(r[3], 16) / 255];
  }

  // ---- Configuration (matching user's BG Studio screenshot) ----
  var CONFIG = {
    color1: '#BAFF5C',
    color2: '#BAFF5C',
    color3: '#FFFFFF',
    speed: 0.85,
    sweepSpeed: 0.25,
    sweepWidth: 1.6,
    sweepFalloff: 6,
    scale: 1.5,
    frequency: 2,
    ripple: 0.22,
    bandDensity: 11,
    lineSharpness: 5.5,
    glow: 0.22,
    scanDirection: 'vertical',
    colorSpread: 0.7,
    brightness: 1.0,
    contrast: 1.15,
    softness: 1.4,
    vignette: 0.45,
    scanline: true,
    grain: true,
    grainIntensity: 0.05,
    opacity: 1.0,
    mouseInteraction: true,
    mouseRadius: 0.5,
    mouseStrength: 0.5
  };

  // ---- Shaders (exact copy from React Bits Scanner component) ----
  var VERT = [
    '#version 300 es',
    'in vec2 position;',
    'void main() {',
    '  gl_Position = vec4(position, 0.0, 1.0);',
    '}'
  ].join('\n');

  var FRAG = [
    '#version 300 es',
    'precision highp float;',
    'uniform vec2 iResolution;',
    'uniform float iTime;',
    'uniform float uSpeed;',
    'uniform float uSweepSpeed;',
    'uniform float uSweepWidth;',
    'uniform float uSweepFalloff;',
    'uniform float uScale;',
    'uniform float uFrequency;',
    'uniform float uRipple;',
    'uniform float uBandDensity;',
    'uniform float uLineSharpness;',
    'uniform float uGlow;',
    'uniform float uColorSpread;',
    'uniform float uBrightness;',
    'uniform float uContrast;',
    'uniform float uSoftness;',
    'uniform float uVignette;',
    'uniform float uOpacity;',
    'uniform float uScanline;',
    'uniform float uGrain;',
    'uniform float uGrainIntensity;',
    'uniform float uDirection;',
    'uniform vec2 uMouse;',
    'uniform float uMouseEnabled;',
    'uniform float uMouseRadius;',
    'uniform float uMouseStrength;',
    'uniform float uMouseActive;',
    'uniform vec3 uColor1;',
    'uniform vec3 uColor2;',
    'uniform vec3 uColor3;',
    'out vec4 fragColor;',
    '',
    'const float TAU = 6.2831853;',
    '',
    'float signalField(vec2 p, float t) {',
    '  float w = sin(p.x * 1.3 + t * 0.7);',
    '  w += sin(p.y * 1.7 - t * 0.52) * 0.8;',
    '  w += sin((p.x + p.y) * 0.9 + t * 0.91) * 0.6;',
    '  w += sin((p.x - p.y) * 1.53 - t * 0.63) * 0.42;',
    '  return w * 0.35;',
    '}',
    '',
    'vec3 palette(float f) {',
    '  f = clamp(f, 0.0, 1.0);',
    '  f = pow(f, uContrast);',
    '  vec3 c = mix(uColor1, uColor2, smoothstep(0.08, 0.6, f));',
    '  return mix(c, uColor3, smoothstep(0.68, 1.0, f));',
    '}',
    '',
    'float scanBand(float x, float aa, float sharp) {',
    '  float v = mix(0.5, 0.5 + 0.5 * cos(x * TAU), aa);',
    '  return pow(v, sharp);',
    '}',
    '',
    'void main() {',
    '  float aspect = iResolution.x / iResolution.y;',
    '  vec2 uv0 = (gl_FragCoord.xy * 2.0 - iResolution.xy) / iResolution.y;',
    '  vec2 p = uv0 / max(uScale, 0.001);',
    '',
    '  float t = iTime * uSpeed;',
    '',
    '  float mouseBoost = 0.0;',
    '  if (uMouseEnabled > 0.5) {',
    '    vec2 mUv = vec2((uMouse.x * 2.0 - 1.0) * aspect, uMouse.y * 2.0 - 1.0);',
    '    vec2 md = uv0 - mUv;',
    '    float r = max(uMouseRadius, 0.001);',
    '    mouseBoost = exp(-dot(md, md) / (r * r)) * uMouseStrength * uMouseActive;',
    '  }',
    '',
    '  float axis;',
    '  if (uDirection < 0.5) axis = p.y;',
    '  else if (uDirection < 1.5) axis = p.x;',
    '  else axis = (p.x + p.y) * 0.70710678;',
    '',
    '  float sig = signalField(p * uFrequency, t);',
    '  float coord = axis + sig * uRipple;',
    '',
    '  float phase = coord / max(uSweepWidth, 0.05) - t * uSweepSpeed;',
    '  float sweep = pow(0.5 + 0.5 * cos(phase * TAU), max(uSweepFalloff, 0.1));',
    '',
    '  float lc = coord * uBandDensity;',
    '  float aa = 1.0 / (1.0 + uSoftness * fwidth(lc) * 3.0);',
    '  aa = clamp(aa * (1.0 + mouseBoost * 0.6), 0.0, 1.0);',
    '',
    '  float bodyBase = clamp(0.5 + 0.5 * sig, 0.0, 1.0);',
    '  float activeSweep = max(sweep, 0.22);',
    '  float body = bodyBase * bodyBase * uGlow * activeSweep;',
    '',
    '  float sharp = max(uLineSharpness, 0.1);',
    '  float split = uColorSpread * 0.16;',
    '  float fr = clamp(scanBand(lc + split, aa, sharp) * activeSweep + body, 0.0, 1.0);',
    '  float fg = clamp(scanBand(lc, aa, sharp) * activeSweep + body, 0.0, 1.0);',
    '  float fb = clamp(scanBand(lc - split, aa, sharp) * activeSweep + body, 0.0, 1.0);',
    '',
    '  vec3 col = vec3(palette(fr).r, palette(fg).g, palette(fb).b);',
    '',
    '  float inten = (fr + fg + fb) * 0.3333333 * uBrightness;',
    '  inten *= 1.0 + mouseBoost * 0.9;',
    '',
    '  if (uScanline > 0.5) {',
    '    inten *= 1.0 - 0.18 * (0.5 + 0.5 * cos(gl_FragCoord.y * 1.7));',
    '  }',
    '',
    '  if (uGrain > 0.5) {',
    '    float g = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233)) + iTime) * 43758.5453);',
    '    inten += (g - 0.5) * uGrainIntensity;',
    '  }',
    '',
    '  inten *= clamp(1.0 - uVignette * smoothstep(0.55, 1.65, length(uv0)), 0.0, 1.0);',
    '  inten = clamp(inten, 0.0, 1.0);',
    '',
    '  float a = clamp(inten * uOpacity, 0.0, 1.0);',
    '  fragColor = vec4(clamp(col, 0.0, 1.0) * a, a);',
    '}'
  ].join('\n');


  // ---- Initialization ----
  function boot() {
    var container = document.getElementById('scanner-bg');
    if (!container) {
      console.error('[QuestFlow Scanner] #scanner-bg element not found in DOM.');
      return;
    }

    // Canvas
    var canvas = document.createElement('canvas');
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.display = 'block';
    container.appendChild(canvas);

    // WebGL2 context
    var gl = canvas.getContext('webgl2', {
      alpha: true,
      premultipliedAlpha: true,
      antialias: false,
      preserveDrawingBuffer: false
    });

    if (!gl) {
      // Fallback: try WebGL 1 with modified shaders? No — just log clearly.
      console.error('[QuestFlow Scanner] WebGL 2 is NOT supported by this browser.');
      container.style.background = 'radial-gradient(ellipse at 50% 30%, rgba(186,255,92,0.08) 0%, transparent 70%)';
      return;
    }

    console.log('[QuestFlow Scanner] WebGL2 context acquired successfully.');

    // ---- Compile Shader ----
    function compile(type, src) {
      var s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
        console.error('[QuestFlow Scanner] Shader compile error (' +
          (type === gl.VERTEX_SHADER ? 'VERTEX' : 'FRAGMENT') + '):\n' +
          gl.getShaderInfoLog(s));
        gl.deleteShader(s);
        return null;
      }
      return s;
    }

    var vs = compile(gl.VERTEX_SHADER, VERT);
    var fs = compile(gl.FRAGMENT_SHADER, FRAG);

    if (!vs || !fs) {
      console.error('[QuestFlow Scanner] Shader compilation failed. Aborting.');
      return;
    }

    var prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);

    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
      console.error('[QuestFlow Scanner] Program link error:\n' + gl.getProgramInfoLog(prog));
      return;
    }

    gl.useProgram(prog);
    console.log('[QuestFlow Scanner] Shaders compiled and linked OK.');

    // ---- Full-Screen Triangle ----
    var vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    var posLoc = gl.getAttribLocation(prog, 'position');
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    // ---- Uniform Locations ----
    var u = {};
    var names = [
      'iResolution', 'iTime',
      'uSpeed', 'uSweepSpeed', 'uSweepWidth', 'uSweepFalloff',
      'uScale', 'uFrequency', 'uRipple', 'uBandDensity',
      'uLineSharpness', 'uGlow', 'uColorSpread', 'uBrightness',
      'uContrast', 'uSoftness', 'uVignette', 'uOpacity',
      'uScanline', 'uGrain', 'uGrainIntensity', 'uDirection',
      'uMouse', 'uMouseEnabled', 'uMouseRadius', 'uMouseStrength',
      'uMouseActive', 'uColor1', 'uColor2', 'uColor3'
    ];
    names.forEach(function (n) { u[n] = gl.getUniformLocation(prog, n); });

    // ---- Set Uniforms from CONFIG ----
    var c1 = hexToRgb(CONFIG.color1);
    var c2 = hexToRgb(CONFIG.color2);
    var c3 = hexToRgb(CONFIG.color3);
    var dirFloat = CONFIG.scanDirection === 'horizontal' ? 1.0 :
                   CONFIG.scanDirection === 'diagonal'   ? 2.0 : 0.0;

    gl.uniform1f(u.uSpeed, CONFIG.speed);
    gl.uniform1f(u.uSweepSpeed, CONFIG.sweepSpeed);
    gl.uniform1f(u.uSweepWidth, CONFIG.sweepWidth);
    gl.uniform1f(u.uSweepFalloff, CONFIG.sweepFalloff);
    gl.uniform1f(u.uScale, CONFIG.scale);
    gl.uniform1f(u.uFrequency, CONFIG.frequency);
    gl.uniform1f(u.uRipple, CONFIG.ripple);
    gl.uniform1f(u.uBandDensity, CONFIG.bandDensity);
    gl.uniform1f(u.uLineSharpness, CONFIG.lineSharpness);
    gl.uniform1f(u.uGlow, CONFIG.glow);
    gl.uniform1f(u.uColorSpread, CONFIG.colorSpread);
    gl.uniform1f(u.uBrightness, CONFIG.brightness);
    gl.uniform1f(u.uContrast, CONFIG.contrast);
    gl.uniform1f(u.uSoftness, CONFIG.softness);
    gl.uniform1f(u.uVignette, CONFIG.vignette);
    gl.uniform1f(u.uOpacity, CONFIG.opacity);
    gl.uniform1f(u.uScanline, CONFIG.scanline ? 1.0 : 0.0);
    gl.uniform1f(u.uGrain, CONFIG.grain ? 1.0 : 0.0);
    gl.uniform1f(u.uGrainIntensity, CONFIG.grainIntensity);
    gl.uniform1f(u.uDirection, dirFloat);
    gl.uniform1f(u.uMouseEnabled, CONFIG.mouseInteraction ? 1.0 : 0.0);
    gl.uniform1f(u.uMouseRadius, CONFIG.mouseRadius);
    gl.uniform1f(u.uMouseStrength, CONFIG.mouseStrength);
    gl.uniform1f(u.uMouseActive, 0.0);
    gl.uniform2f(u.uMouse, 0.5, 0.5);
    gl.uniform3f(u.uColor1, c1[0], c1[1], c1[2]);
    gl.uniform3f(u.uColor2, c2[0], c2[1], c2[2]);
    gl.uniform3f(u.uColor3, c3[0], c3[1], c3[2]);

    // ---- Blending (crucial for alpha compositing over page) ----
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

    // ---- Resize ----
    function setSize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var w = Math.floor(container.clientWidth * dpr);
      var h = Math.floor(container.clientHeight * dpr);
      if (w < 1) w = 1;
      if (h < 1) h = 1;
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
        gl.viewport(0, 0, w, h);
        gl.uniform2f(u.iResolution, w, h);
      }
    }

    window.addEventListener('resize', setSize);
    setSize();

    // ---- Mouse Tracking ----
    var currentMouse = [0.5, 0.5];
    var targetMouse = [0.5, 0.5];
    var mouseActive = 0;
    var targetMouseActive = 0;

    if (CONFIG.mouseInteraction) {
      canvas.style.pointerEvents = 'auto';
      canvas.addEventListener('mousemove', function (e) {
        var rect = canvas.getBoundingClientRect();
        targetMouse[0] = (e.clientX - rect.left) / rect.width;
        targetMouse[1] = 1.0 - (e.clientY - rect.top) / rect.height;
        targetMouseActive = 1;
      });
      canvas.addEventListener('mouseleave', function () {
        targetMouseActive = 0;
      });
    }

    // ---- Render Loop ----
    var t0 = null;
    var rafId = 0;
    var frameCount = 0;

    function render(now) {
      if (t0 === null) t0 = now;
      var t = Math.max(0, (now - t0) * 0.001);
      gl.uniform1f(u.iTime, t);

      // Smooth mouse interpolation (matches React Bits source)
      currentMouse[0] += 0.05 * (targetMouse[0] - currentMouse[0]);
      currentMouse[1] += 0.05 * (targetMouse[1] - currentMouse[1]);
      mouseActive += 0.05 * (targetMouseActive - mouseActive);
      gl.uniform2f(u.uMouse, currentMouse[0], currentMouse[1]);
      gl.uniform1f(u.uMouseActive, mouseActive);

      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.bindVertexArray(vao);
      gl.drawArrays(gl.TRIANGLES, 0, 3);

      frameCount++;
      if (frameCount === 1) {
        console.log('[QuestFlow Scanner] Active // Rendering WebGL2 radar field.');
      }

      rafId = requestAnimationFrame(render);
    }

    rafId = requestAnimationFrame(render);
    console.log('[QuestFlow Scanner] Render loop started.');

    // ---- Visibility Pause ----
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        if (rafId) { cancelAnimationFrame(rafId); rafId = 0; }
      } else if (!rafId) {
        rafId = requestAnimationFrame(render);
      }
    });
  }

  // ---- Entry Point ----
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
