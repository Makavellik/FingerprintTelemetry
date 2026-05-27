from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import hashlib, time, uuid, statistics, os, math

app = FastAPI()

SESSIONS = {}
IDENTITIES = {}

# ------------------ Utils ------------
# ─────────────────────────────────────
# Deterministic identity hash
# ─────────────────────────────────────
def sha(value: str, *, normalize: bool = True) -> str:

    if value is None:
        value = ""

    if not isinstance(value, str):
        value = str(value)

    if normalize:
        value = " ".join(value.strip().split())

    return hashlib.sha256(
        value.encode("utf-8", errors="ignore")
    ).hexdigest()


# ─────────────────────────────────────
# Behavioral entropy estimator
# ─────────────────────────────────────
def entropy(values) -> float:

    if not values or len(values) < 2:
        return 0.0

    try:

        # ─────────────────────────────
        # Normalize incoming values
        # ─────────────────────────────
        clean = []

        for v in values:

            try:
                n = float(v)

                if math.isfinite(n):
                    clean.append(n)

            except:
                continue

        if len(clean) < 2:
            return 0.0

        # ─────────────────────────────
        # Remove impossible spikes
        # ─────────────────────────────
        median = statistics.median(clean)

        filtered = [
            x for x in clean
            if abs(x - median) < (median * 8 + 1)
        ]

        if len(filtered) < 2:
            filtered = clean

        # ─────────────────────────────
        # Core metrics
        # ─────────────────────────────
        stdev = statistics.stdev(filtered)

        mean = statistics.mean(filtered)

        spread = max(filtered) - min(filtered)

        # ─────────────────────────────
        # Relative behavioral instability
        # ─────────────────────────────
        relative_noise = (
            stdev / mean
            if mean > 0 else 0
        )

        # ─────────────────────────────
        # Final weighted entropy
        # ─────────────────────────────
        entropy_score = (
            (stdev * 0.55) +
            (relative_noise * 35) +
            (spread * 0.10)
        )

        return round(entropy_score, 6)

    except Exception:
        return 0.0


# ─────────────────────────────────────
# High precision temporal marker
# ─────────────────────────────────────
def now(ms: bool = True) -> float:

    current = time.time()

    return round(
        current,
        3 if ms else 2
    )

# ------------------ Static Routes FIRST ------------------


@app.get("/ping")
def ping():
    return {
        "t": time.time(),
        "mono": time.perf_counter(),
        "pid": os.getpid(),
        "status": "ok"
    }


@app.get("/s.js")
def js():

    return HTMLResponse("""

async function start(token){

  // ─────────────────────────────────────
  // Temporal baseline
  // ─────────────────────────────────────
  const sessionStart = performance.now();

  // ─────────────────────────────────────
  // Core telemetry structure
  // ─────────────────────────────────────
  const fp = {

    ua: navigator.userAgent,

    lang: navigator.language,

    platform: navigator.platform,

    cores:
      navigator.hardwareConcurrency || 0,

    mem:
      navigator.deviceMemory || 0,

    tz:
      Intl.DateTimeFormat()
        .resolvedOptions()
        .timeZone,

    screen: {

      w: screen.width,

      h: screen.height,

      depth: screen.colorDepth,

      dpr:
        window.devicePixelRatio || 1
    },

    touch:
      navigator.maxTouchPoints || 0,

    visibility: [],

    focus: [],

    timing: [],

    cpu: [],

    frame: [],

    idle: [],

    net: [],

    interaction: [],

    render: [],

    environment: {},

    analysis: {},

    consistency: {},

    behavioral: {}
  };

  // ─────────────────────────────────────
  // Environment snapshot
  // ─────────────────────────────────────
  fp.environment = {

    online:
      navigator.onLine,

    cookie:
      navigator.cookieEnabled,

    webdriver:
      navigator.webdriver || false,

    history:
      history.length || 0,

    visibility:
      document.visibilityState,

    referrer:
      document.referrer || null,

    languageList:
      navigator.languages || [],

    memory:
      performance.memory ? {

        heapLimit:
          performance.memory.jsHeapSizeLimit,

        heapTotal:
          performance.memory.totalJSHeapSize,

        heapUsed:
          performance.memory.usedJSHeapSize

      } : null
  };

  // ─────────────────────────────────────
  // Utility
  // ─────────────────────────────────────
  function pause(min=20,max=140){

    return new Promise(r =>

      setTimeout(
        r,
        min + Math.random() * (max-min)
      )
    );
  }

  function stats(arr){

    if(!arr.length){
      return null;
    }

    const avg =
      arr.reduce((a,b)=>a+b,0) / arr.length;

    const min = Math.min(...arr);

    const max = Math.max(...arr);

    const variance =
      arr.reduce((a,b)=>
        a + Math.pow(b - avg,2)
      ,0) / arr.length;

    return {

      avg:
        Number(avg.toFixed(4)),

      min:
        Number(min.toFixed(4)),

      max:
        Number(max.toFixed(4)),

      spread:
        Number((max-min).toFixed(4)),

      variance:
        Number(variance.toFixed(4)),

      samples:
        arr.length
    };
  }

  // ─────────────────────────────────────
  // Visibility tracking
  // ─────────────────────────────────────
  document.addEventListener(
    "visibilitychange",
    () => {

      fp.visibility.push({

        state:
          document.visibilityState,

        ts:
          performance.now()
      });
    }
  );

  // ─────────────────────────────────────
  // Focus behavior
  // ─────────────────────────────────────
  window.addEventListener(
    "focus",
    () => {

      fp.focus.push({

        state:1,

        ts:performance.now()
      });
    }
  );

  window.addEventListener(
    "blur",
    () => {

      fp.focus.push({

        state:0,

        ts:performance.now()
      });
    }
  );

  // ─────────────────────────────────────
  // Human interaction rhythm
  // ─────────────────────────────────────
  let lastInteraction = performance.now();

  ["mousemove","keydown","scroll","click"]
    .forEach(evt => {

      window.addEventListener(
        evt,
        () => {

          const now = performance.now();

          fp.interaction.push({

            type:evt,

            delta:
              now - lastInteraction,

            ts:now
          });

          lastInteraction = now;

        },
        { passive:true }
      );

    });

  // ─────────────────────────────────────
  // Idle rhythm sampling
  // ─────────────────────────────────────
  for(let i=0;i<12;i++){

    const s = performance.now();

    await pause(80,320);

    fp.idle.push(
      performance.now() - s
    );
  }

  // ─────────────────────────────────────
  // Timing entropy
  // ─────────────────────────────────────
  for(let i=0;i<28;i++){

    const s = performance.now();

    await pause(15,180);

    const e = performance.now();

    fp.timing.push(e - s);
  }

  // ─────────────────────────────────────
  // CPU fluctuation profile
  // ─────────────────────────────────────
  for(let i=0;i<24;i++){

    const s = performance.now();

    let x = 0;

    const limit =
      60000 +
      Math.floor(Math.random()*100000);

    for(let j=0;j<limit;j++){

      x += Math.sqrt(
        (j ^ (j % 23))
      );
    }

    fp.cpu.push(
      performance.now() - s
    );

    await pause(10,70);
  }

  // ─────────────────────────────────────
  // Rendering rhythm
  // ─────────────────────────────────────
  await new Promise(resolve => {

    let frames = 0;

    let last = performance.now();

    function loop(){

      const now = performance.now();

      const delta = now - last;

      fp.frame.push(delta);

      if(delta > 22){

        fp.render.push({

          type:"frame-drop",

          delta,
          ts:now
        });
      }

      last = now;

      if(++frames < 42){

        requestAnimationFrame(loop);

      }else{

        resolve();
      }
    }

    requestAnimationFrame(loop);

  });

  // ─────────────────────────────────────
  // Network timing
  // ─────────────────────────────────────
  for(let i=0;i<8;i++){

    const t0 = performance.now();

    try{

      const r = await fetch(
        "/ping",
        { cache:"no-store" }
      );

      const t1 = performance.now();

      const js = await r.json();

      fp.net.push({

        rtt:
          t1 - t0,

        drift:
          Date.now() - js.t,

        mono:
          js.mono,

        ts:
          performance.now()
      });

    }catch(err){

      fp.net.push({

        error:true,

        reason:String(err)
      });
    }

    await pause(40,220);
  }

  // ─────────────────────────────────────
  // Statistical analysis
  // ─────────────────────────────────────
  const timingStats =
    stats(fp.timing);

  const cpuStats =
    stats(fp.cpu);

  const frameStats =
    stats(fp.frame);

  const idleStats =
    stats(fp.idle);

  // ─────────────────────────────────────
  // Behavioral interpretation
  // ─────────────────────────────────────
  fp.analysis = {

    timing:
      timingStats,

    cpu:
      cpuStats,

    frame:
      frameStats,

    idle:
      idleStats,

    interactionVolume:
      fp.interaction.length,

    focusTransitions:
      fp.focus.length,

    visibilityTransitions:
      fp.visibility.length
  };

  // ─────────────────────────────────────
  // Environmental coherence
  // ─────────────────────────────────────
  fp.consistency = {

    renderStability:

      frameStats &&
      frameStats.variance < 2

        ? "stable-rendering"

        : frameStats &&
          frameStats.variance > 18

            ? "volatile-rendering"

            : "moderate-rendering",

    timingNoise:

      timingStats &&
      timingStats.variance < 1

        ? "overly-consistent"

        : timingStats &&
          timingStats.variance > 40

            ? "organic-fluctuation"

            : "moderate-noise",

    cpuBehavior:

      cpuStats &&
      cpuStats.spread > 25

        ? "resource-instability"

        : "stable-execution",

    interactionPattern:

      fp.interaction.length < 2

        ? "minimal-human-interaction"

        : fp.interaction.length > 20

            ? "high-interaction-environment"

            : "normal-interaction"
  };

  // ─────────────────────────────────────
  // Behavioral synthesis
  // ─────────────────────────────────────
  fp.behavioral = {

    environmentNature:

      (
        timingStats &&
        cpuStats &&
        timingStats.variance < 0.8 &&
        cpuStats.variance < 0.8
      )

        ? "uniform-environment"

        : "organic-environment",

    attentionModel:

      fp.visibility.length === 0

        ? "continuous-attention"

        : "fragmented-attention",

    executionPressure:

      (
        frameStats &&
        frameStats.avg > 22
      )

        ? "under-load"

        : "stable-runtime",

    temporalIdentity:

      (
        idleStats &&
        idleStats.variance > 30
      )

        ? "human-rhythm-present"

        : "low-rhythm-variance"
  };

  // ─────────────────────────────────────
  // Final transmission
  // ─────────────────────────────────────
  fetch("/collect",{

    method:"POST",

    headers:{
      "Content-Type":"application/json"
    },

    body:JSON.stringify({

      token,

      ts:Date.now(),

      uptime:
        performance.now() - sessionStart,

      fp
    })
  });

}

""", media_type="application/javascript")

@app.get("/dashboard")
def dashboard():

    rows = ""

    total_sessions = len(SESSIONS)
    active_sessions = 0
    anomalous_sessions = 0

    for token, s in SESSIONS.items():

        created = time.strftime(
            "%H:%M:%S",
            time.localtime(s["created"])
        )

        last = "—"

        if s.get("last_seen"):

            last = time.strftime(
                "%H:%M:%S",
                time.localtime(s["last_seen"])
            )

        signals = s.get("signals", [])

        if signals:
            active_sessions += 1

        # ─────────────────────────────────────
        # Empty session state
        # ─────────────────────────────────────
        if not signals:

            rows += f"""
            <div class="session-card idle-card">

                <div class="top-row">

                    <div>
                        <div class="token">
                            {token[:12]}...
                        </div>

                        <div class="created">
                            Created · {created}
                        </div>
                    </div>

                    <div class="badge waiting">
                        Waiting
                    </div>

                </div>

                <div class="empty-state">

                    Session initialized successfully,
                    but no behavioral telemetry has been received yet.

                    The environment has not produced enough
                    temporal interaction to establish coherence.

                </div>

                <div class="actions">

                    <a href="/{token}" target="_blank">
                        Open Session
                    </a>

                </div>

            </div>
            """

            continue

        # ─────────────────────────────────────
        # Latest signal
        # ─────────────────────────────────────
        sig = signals[-1]

        anomaly = float(sig.get("anomaly", 0))
        coherence = str(sig.get("coherence", "unknown"))

        coherence_score = round(
            float(sig.get("coherence_score", 0)),
            3
        )

        if anomaly >= 0.45:
            anomalous_sessions += 1

        # ─────────────────────────────────────
        # Human readable interpretation
        # ─────────────────────────────────────
        interpretation = "Organic behavioral flow"

        if anomaly > 0.75:

            interpretation = (
                "Environmental behavior deviates "
                "significantly from previous timing patterns."
            )

        elif anomaly > 0.45:

            interpretation = (
                "Execution profile shows instability "
                "and irregular timing fluctuation."
            )

        elif coherence == "synthetic":

            interpretation = (
                "Behavior appears excessively uniform "
                "with reduced natural entropy."
            )

        elif coherence == "unstable":

            interpretation = (
                "Resource fluctuation and execution variance detected."
            )

        elif coherence == "organic":

            interpretation = (
                "Natural interaction noise and timing drift present."
            )

        # ─────────────────────────────────────
        # Activity profile
        # ─────────────────────────────────────
        activity = "Passive observation"

        if sig.get("focus_events", 0) > 2:
            activity = "Interactive environment"

        if sig.get("visibility_changes", 0) > 3:
            activity = "Frequent contextual switching"

        # ─────────────────────────────────────
        # Visual state
        # ─────────────────────────────────────
        state_class = "stable"

        if anomaly > 0.45:
            state_class = "warning"

        if anomaly > 0.75:
            state_class = "critical"

        rows += f"""

        <div class="session-card {state_class}">

            <div class="top-row">

                <div>

                    <div class="token">
                        {token[:12]}...
                    </div>

                    <div class="created">
                        Created · {created}
                    </div>

                </div>

                <div class="badge {coherence}">
                    {coherence.upper()}
                </div>

            </div>

            <div class="grid">

                <div class="cell">
                    <div class="label">
                        Fingerprint
                    </div>

                    <div class="value fingerprint">
                        {sig.get("id","unknown")}
                    </div>
                </div>

                <div class="cell">
                    <div class="label">
                        Platform
                    </div>

                    <div class="value">
                        {sig.get("platform","Unknown")}
                    </div>
                </div>

                <div class="cell">
                    <div class="label">
                        Hardware
                    </div>

                    <div class="value">
                        {sig.get("cores","?")} Cores ·
                        {sig.get("mem","?")} GB
                    </div>
                </div>

                <div class="cell">
                    <div class="label">
                        Network RTT
                    </div>

                    <div class="value">
                        {sig.get("rtt","?")} ms
                    </div>
                </div>

                <div class="cell">
                    <div class="label">
                        Coherence Score
                    </div>

                    <div class="value">
                        {coherence_score}
                    </div>
                </div>

                <div class="cell">
                    <div class="label">
                        Anomaly
                    </div>

                    <div class="value anomaly {state_class}">
                        {round(anomaly,4)}
                    </div>
                </div>

            </div>

            <div class="ua-box">

                <div class="label">
                    User-Agent
                </div>

                <div class="ua">
                    {sig.get("ua","Unknown")}
                </div>

            </div>

            <div class="analysis">

                <div class="analysis-title">
                    Environmental Interpretation
                </div>

                <div class="analysis-text">
                    {interpretation}
                </div>

            </div>

            <div class="activity">

                <span>
                    Activity Profile:
                </span>

                {activity}

            </div>

            <div class="bottom">

                <div class="last">
                    Last Seen · {last}
                </div>

                <a href="/{token}" target="_blank">
                    Inspect Session
                </a>

            </div>

        </div>
        """

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1.0">

<title>
HybridSignals — Cognitive Command Center
</title>

<style>

:root {{

    --bg:#050508;

    --panel:#0b1016;

    --line:
      rgba(255,255,255,0.06);

    --text:#e8fffb;

    --muted:#7edbcc;

    --primary:#00ffcc;

    --warning:#ffaa33;

    --danger:#ff5f6d;
}}

* {{
    box-sizing:border-box;
}}

html,body {{

    margin:0;
    padding:0;

    background:
      radial-gradient(
        circle at top,
        rgba(0,255,200,0.05),
        transparent 35%
      ),

      var(--bg);

    color:var(--text);

    font-family:
      Inter,
      ui-monospace,
      monospace;
}}

body {{
    overflow-x:hidden;
}}

.glow {{

    position:fixed;

    top:-240px;
    right:-240px;

    width:600px;
    height:600px;

    background:
      radial-gradient(
        circle,
        rgba(0,255,200,0.08),
        transparent 70%
      );

    filter:blur(40px);

    pointer-events:none;
}}

header {{

    position:sticky;
    top:0;

    z-index:999;

    padding:28px;

    backdrop-filter:blur(16px);

    background:
      rgba(4,6,8,0.82);

    border-bottom:
      1px solid var(--line);
}}

h1 {{

    margin:0;

    font-size:1.7rem;
}}

.subtitle {{

    margin-top:10px;

    color:var(--muted);

    opacity:0.8;

    line-height:1.7;

    max-width:850px;
}}

.metrics {{

    display:grid;

    grid-template-columns:
      repeat(auto-fit,minmax(180px,1fr));

    gap:16px;

    margin-top:24px;
}}

.metric {{

    padding:18px;

    border-radius:18px;

    background:
      rgba(255,255,255,0.03);

    border:
      1px solid rgba(255,255,255,0.04);
}}

.metric .label {{

    font-size:0.75rem;

    opacity:0.6;

    text-transform:uppercase;

    letter-spacing:1px;
}}

.metric .value {{

    margin-top:8px;

    color:var(--primary);

    font-size:1.5rem;

    font-weight:700;
}}

.wrapper {{

    width:100%;

    max-width:1700px;

    margin:auto;

    padding:26px;

    display:grid;

    grid-template-columns:
      repeat(auto-fit,minmax(420px,1fr));

    gap:24px;
}}

.session-card {{

    position:relative;

    padding:24px;

    border-radius:26px;

    background:
      linear-gradient(
        145deg,
        rgba(14,18,24,0.96),
        rgba(5,8,12,0.96)
      );

    border:1px solid rgba(255,255,255,0.05);

    overflow:hidden;

    transition:0.25s ease;
}}

.session-card:hover {{

    transform:translateY(-3px);

    border-color:
      rgba(0,255,200,0.12);
}}

.session-card::before {{

    content:"";

    position:absolute;

    inset:0;

    background:
      linear-gradient(
        130deg,
        transparent,
        rgba(255,255,255,0.03),
        transparent
      );

    pointer-events:none;
}}

.top-row {{

    display:flex;

    justify-content:space-between;

    align-items:flex-start;

    gap:20px;
}}

.token {{

    font-size:1.05rem;

    font-weight:700;

    color:#f2fffd;
}}

.created {{

    margin-top:6px;

    opacity:0.58;

    font-size:0.8rem;
}}

.badge {{

    padding:8px 14px;

    border-radius:999px;

    font-size:0.72rem;

    font-weight:700;

    letter-spacing:1px;
}}

.badge.organic,
.badge.stable {{

    background:
      rgba(0,255,200,0.12);

    color:var(--primary);
}}

.badge.synthetic {{

    background:
      rgba(255,90,90,0.12);

    color:#ff7c8d;
}}

.badge.unstable {{

    background:
      rgba(255,170,0,0.12);

    color:var(--warning);
}}

.badge.waiting {{

    background:
      rgba(255,255,255,0.05);

    color:#d0d0d0;
}}

.grid {{

    margin-top:24px;

    display:grid;

    grid-template-columns:
      repeat(auto-fit,minmax(180px,1fr));

    gap:16px;
}}

.cell {{

    padding:14px;

    border-radius:16px;

    background:
      rgba(255,255,255,0.02);

    border:
      1px solid rgba(255,255,255,0.03);
}}

.label {{

    font-size:0.7rem;

    opacity:0.55;

    letter-spacing:1px;

    text-transform:uppercase;
}}

.value {{

    margin-top:8px;

    line-height:1.6;

    word-break:break-word;
}}

.fingerprint {{
    color:#8effef;
}}

.ua-box {{

    margin-top:20px;

    padding:16px;

    border-radius:18px;

    background:
      rgba(255,255,255,0.02);

    border:
      1px solid rgba(255,255,255,0.03);
}}

.ua {{

    margin-top:10px;

    font-size:0.82rem;

    line-height:1.8;

    color:#c6fff6;

    word-break:break-word;

    opacity:0.82;
}}

.analysis {{

    margin-top:22px;

    padding:18px;

    border-left:
      2px solid rgba(0,255,200,0.14);

    background:
      rgba(0,255,200,0.02);

    border-radius:14px;
}}

.analysis-title {{

    font-size:0.75rem;

    letter-spacing:1px;

    text-transform:uppercase;

    opacity:0.6;
}}

.analysis-text {{

    margin-top:10px;

    line-height:1.8;

    color:#d8fff9;
}}

.activity {{

    margin-top:18px;

    font-size:0.86rem;

    color:#9deedf;

    line-height:1.7;
}}

.activity span {{
    opacity:0.58;
}}

.bottom {{

    margin-top:24px;

    display:flex;

    justify-content:space-between;

    align-items:center;

    gap:18px;

    flex-wrap:wrap;
}}

.last {{

    opacity:0.55;

    font-size:0.78rem;
}}

.anomaly.warning {{
    color:var(--warning);
}}

.anomaly.critical {{
    color:var(--danger);
}}

a {{

    color:var(--primary);

    text-decoration:none;

    font-size:0.86rem;
}}

a:hover {{
    text-decoration:underline;
}}

.empty-state {{

    margin-top:18px;

    line-height:1.8;

    opacity:0.7;
}}

.footer {{

    padding:30px;

    text-align:center;

    border-top:
      1px solid rgba(255,255,255,0.04);

    opacity:0.5;

    line-height:1.9;

    font-size:0.78rem;
}}

@media(max-width:768px) {{

    header {{
        padding:22px;
    }}

    .wrapper {{
        padding:18px;
        grid-template-columns:1fr;
    }}

    .session-card {{
        padding:20px;
    }}

    .bottom {{
        flex-direction:column;
        align-items:flex-start;
    }}

    .metrics {{
        grid-template-columns:1fr;
    }}
}}

</style>
</head>

<body>

<div class="glow"></div>

<header>

    <h1>
      🧠 HybridSignals — Cognitive Command Center * Autor; ByMakaveliw
    </h1>

    <div class="subtitle">

      Environmental telemetry · temporal interpretation ·
      behavioral drift correlation · execution coherence analysis

      <br><br>

      The system does not attempt to identify the subject alone.

      It attempts to understand how environments behave
      under interruption, timing fluctuation and interaction variance.

    </div>

    <div class="metrics">

        <div class="metric">

            <div class="label">
              Total Sessions
            </div>

            <div class="value">
              {total_sessions}
            </div>

        </div>

        <div class="metric">

            <div class="label">
              Active Streams
            </div>

            <div class="value">
              {active_sessions}
            </div>

        </div>

        <div class="metric">

            <div class="label">
              Behavioral Deviations
            </div>

            <div class="value">
              {anomalous_sessions}
            </div>

        </div>

    </div>

</header>

<div class="wrapper">

{rows}

</div>

<div class="footer">

HybridSignals · Behavioral Drift Engine ·
Temporal Noise Analysis · Environmental Consistency Layer ·
Execution Variance Interpretation . 
Autor; ByMakaveliw

</div>

</body>
</html>
""")


# ------------------ Link Generator ------------------


def now():
    return time.time()

@app.get("/new")
def new():

    token = uuid.uuid4().hex[:12]

    SESSIONS[token] = {

        "created": now(),

        "signals": [],

        "status": "active",

        "last_seen": None
    }

    url = f"http://127.0.0.1:8000/{token}"

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="utf-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1.0">

<title>
HybridSignals — Session Initialization
</title>

<style>

:root {{

    --bg:#040507;

    --panel:
      rgba(12,16,22,0.94);

    --line:
      rgba(255,255,255,0.06);

    --primary:#00ffcc;

    --secondary:#7ffff1;

    --text:#e7fffb;

    --muted:#86dccc;

    --danger:#ff5c7a;
}}

* {{
    box-sizing:border-box;
}}

html,body {{

    margin:0;
    padding:0;

    width:100%;
    min-height:100%;

    background:

      radial-gradient(
        circle at top left,
        rgba(0,255,200,0.08),
        transparent 32%
      ),

      radial-gradient(
        circle at bottom right,
        rgba(0,120,255,0.08),
        transparent 36%
      ),

      var(--bg);

    color:var(--text);

    font-family:
      Inter,
      "Segoe UI",
      ui-monospace,
      monospace;
}}

body {{
    position:relative;
    overflow-x:hidden;
}}

.grid {{

    position:fixed;

    inset:0;

    background-image:

      linear-gradient(
        rgba(255,255,255,0.02) 1px,
        transparent 1px
      ),

      linear-gradient(
        90deg,
        rgba(255,255,255,0.02) 1px,
        transparent 1px
      );

    background-size:42px 42px;

    opacity:0.16;

    pointer-events:none;
}}

.glow {{

    position:fixed;

    top:-260px;
    right:-260px;

    width:720px;
    height:720px;

    background:
      radial-gradient(
        circle,
        rgba(0,255,200,0.10),
        transparent 72%
      );

    filter:blur(60px);

    pointer-events:none;

    animation:float 12s ease-in-out infinite;
}}

.glow2 {{

    position:fixed;

    bottom:-240px;
    left:-240px;

    width:580px;
    height:580px;

    background:
      radial-gradient(
        circle,
        rgba(0,140,255,0.09),
        transparent 72%
      );

    filter:blur(70px);

    pointer-events:none;

    animation:float2 16s ease-in-out infinite;
}}

@keyframes float {{

    0% {{
        transform:translateY(0px);
    }}

    50% {{
        transform:translateY(24px);
    }}

    100% {{
        transform:translateY(0px);
    }}
}}

@keyframes float2 {{

    0% {{
        transform:translateX(0px);
    }}

    50% {{
        transform:translateX(26px);
    }}

    100% {{
        transform:translateX(0px);
    }}
}}

.wrapper {{

    position:relative;

    width:100%;

    min-height:100vh;

    display:flex;

    align-items:center;

    justify-content:center;

    padding:40px 22px;
}}

.card {{

    position:relative;

    width:100%;

    max-width:760px;

    padding:42px;

    border-radius:30px;

    overflow:hidden;

    background:

      linear-gradient(
        145deg,
        rgba(14,18,25,0.96),
        rgba(5,8,12,0.95)
      );

    border:1px solid var(--line);

    backdrop-filter:blur(18px);

    box-shadow:

      0 0 80px rgba(0,255,200,0.08),

      inset 0 0 30px rgba(255,255,255,0.02);
}}

.card::before {{

    content:"";

    position:absolute;

    inset:0;

    background:

      linear-gradient(
        130deg,
        transparent,
        rgba(255,255,255,0.03),
        transparent
      );

    pointer-events:none;
}}

.topline {{

    display:flex;

    align-items:center;

    gap:12px;

    color:var(--secondary);

    letter-spacing:2px;

    text-transform:uppercase;

    font-size:0.75rem;

    opacity:0.82;

    flex-wrap:wrap;
}}

.dot {{

    width:9px;
    height:9px;

    border-radius:50%;

    background:var(--primary);

    box-shadow:
      0 0 14px var(--primary);
}}

h1 {{

    margin-top:22px;
    margin-bottom:14px;

    font-size:clamp(2rem,5vw,3rem);

    line-height:1.1;

    color:#f1fffd;
}}

.desc {{

    max-width:680px;

    color:var(--muted);

    line-height:1.9;

    font-size:0.97rem;

    opacity:0.86;
}}

.metrics {{

    display:grid;

    grid-template-columns:
      repeat(auto-fit,minmax(160px,1fr));

    gap:16px;

    margin-top:30px;
}}

.metric {{

    padding:18px;

    border-radius:18px;

    background:
      rgba(255,255,255,0.025);

    border:
      1px solid rgba(255,255,255,0.04);
}}

.metric .m-label {{

    font-size:0.72rem;

    opacity:0.58;

    text-transform:uppercase;

    letter-spacing:1px;
}}

.metric .m-value {{

    margin-top:10px;

    font-size:1rem;

    color:var(--primary);

    font-weight:700;
}}

.section {{
    margin-top:30px;
}}

.label {{

    margin-bottom:10px;

    font-size:0.78rem;

    letter-spacing:1px;

    text-transform:uppercase;

    opacity:0.64;

    color:#8ae9db;
}}

.box {{

    position:relative;

    padding:18px;

    border-radius:16px;

    overflow:hidden;

    background:
      rgba(255,255,255,0.025);

    border:
      1px solid rgba(255,255,255,0.05);

    color:#dcfffb;

    line-height:1.8;

    word-break:break-word;
}}

.box::before {{

    content:"";

    position:absolute;

    top:0;
    left:-100%;

    width:100%;
    height:100%;

    background:

      linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,0.05),
        transparent
      );

    animation:scan 7s linear infinite;
}}

@keyframes scan {{

    0% {{
        left:-100%;
    }}

    100% {{
        left:100%;
    }}
}}

.signal {{

    margin-top:28px;

    padding:22px;

    border-radius:20px;

    background:
      rgba(0,255,200,0.03);

    border:
      1px solid rgba(0,255,200,0.08);

    line-height:1.9;

    color:#a5f4e7;

    font-size:0.92rem;
}}

.signal span {{
    color:#ffffff;
}}

.actions {{

    display:flex;

    gap:16px;

    margin-top:34px;

    flex-wrap:wrap;
}}

button {{

    flex:1;

    min-width:220px;

    padding:16px 20px;

    border:none;

    border-radius:16px;

    cursor:pointer;

    transition:0.25s ease;

    font-weight:700;

    letter-spacing:0.5px;

    font-size:0.92rem;
}}

.primary {{

    color:#001712;

    background:

      linear-gradient(
        90deg,
        #00ffcc,
        #00d5ff
      );

    box-shadow:
      0 0 40px rgba(0,255,200,0.18);
}}

.primary:hover {{

    transform:translateY(-2px);

    box-shadow:
      0 0 55px rgba(0,255,200,0.24);
}}

.secondary {{

    background:
      rgba(255,255,255,0.03);

    color:#a4fff0;

    border:
      1px solid rgba(255,255,255,0.05);
}}

.secondary:hover {{

    background:
      rgba(255,255,255,0.06);
}}

.footer {{

    margin-top:30px;

    opacity:0.54;

    color:#7ddccc;

    line-height:1.8;

    font-size:0.8rem;
}}

.status-line {{

    display:flex;

    align-items:center;

    gap:10px;

    margin-top:22px;

    color:#9cf8e9;

    opacity:0.82;

    flex-wrap:wrap;
}}

.pulse {{

    width:10px;
    height:10px;

    border-radius:50%;

    background:#00ffcc;

    box-shadow:
      0 0 16px #00ffcc;

    animation:pulse 2s infinite;
}}

@keyframes pulse {{

    0% {{
        transform:scale(1);
        opacity:1;
    }}

    50% {{
        transform:scale(1.4);
        opacity:0.5;
    }}

    100% {{
        transform:scale(1);
        opacity:1;
    }}
}}

@media(max-width:768px) {{

    .wrapper {{
        padding:22px 16px;
    }}

    .card {{
        padding:28px 22px;
        border-radius:24px;
    }}

    h1 {{
        font-size:2rem;
    }}

    .desc {{
        font-size:0.92rem;
    }}

    .actions {{
        flex-direction:column;
    }}

    button {{
        width:100%;
    }}

    .metrics {{
        grid-template-columns:1fr;
    }}
}}

</style>
</head>

<body>

<div class="grid"></div>

<div class="glow"></div>
<div class="glow2"></div>

<div class="wrapper">

    <div class="card">

        <div class="topline">

            <div class="dot"></div>

            HYBRIDSIGNALS · COGNITIVE SESSION INITIALIZATION $Autor; ByMakaveliw

        </div>

        <h1>
          Environmental Telemetry Channel Created
        </h1>

        <div class="desc">

          The session has been initialized successfully and is now capable
          of receiving environmental, temporal and behavioral telemetry streams.

          <br><br>

          The objective is not limited to identity correlation.

          The objective is to observe how environments react under delay,
          interruption, instability, rendering pressure and interaction drift.

        </div>

        <div class="status-line">

            <div class="pulse"></div>

            Awaiting first behavioral signal...

        </div>

        <div class="metrics">

            <div class="metric">

                <div class="m-label">
                  Session State
                </div>

                <div class="m-value">
                  ACTIVE
                </div>

            </div>

            <div class="metric">

                <div class="m-label">
                  Signal Layer
                </div>

                <div class="m-value">
                  ARMED
                </div>

            </div>

            <div class="metric">

                <div class="m-label">
                  Entropy Sync
                </div>

                <div class="m-value">
                  READY
                </div>

            </div>

        </div>

        <div class="section">

            <div class="label">
              Secure Session Token
            </div>

            <div class="box">
              {token}
            </div>

        </div>

        <div class="section">

            <div class="label">
              Behavioral Channel Endpoint
            </div>

            <div class="box" id="url">
              {url}
            </div>

        </div>

        <div class="signal">

            <span>Signal Interpretation</span>

            <br><br>

            Stable environments usually reveal repetition.

            Organic environments reveal interruption,
            fluctuation and timing inconsistency.

            Artificial environments often reveal precision,
            synchronization and reduced behavioral noise.

            <br><br>

            A connection alone reveals nothing.

            Time reveals the rest.

        </div>

        <div class="actions">

            <button class="primary"
                    onclick="navigator.clipboard.writeText('{url}')">

                📡 Copy Session Endpoint

            </button>

            <button class="secondary"
                    onclick="window.location='/dashboard'">

                Open Command Center

            </button>

        </div>

        <div class="footer">

          HybridSignals · Temporal Interpretation Layer ·
          Environmental Coherence Engine ·
          Behavioral Drift Correlation .
          Autor; ByMakaveliw
        </div>

    </div>

</div>

</body>
</html>
""")

# ------------------ Collector ------------------

@app.post("/collect")
async def collect(req: Request):

    try:

        payload = await req.json()

        token = payload.get("token")
        fp = payload.get("fp", {})

        # ─────────────────────────────────────
        # Session validation
        # ─────────────────────────────────────
        if not token or token not in SESSIONS:

            return JSONResponse({
                "status": "invalid-session",
                "message":
                    "Unknown telemetry channel"
            }, status_code=400)

        # ─────────────────────────────────────
        # Safe extraction helpers
        # ─────────────────────────────────────
        def safe_list(v):
            return v if isinstance(v, list) else []

        def safe_number(v, default=0):
            try:
                return float(v)
            except:
                return default

        # ─────────────────────────────────────
        # Environmental profile normalization
        # ─────────────────────────────────────
        ua = str(fp.get("ua", ""))
        lang = str(fp.get("lang", ""))
        tz = str(fp.get("tz", ""))
        platform = str(fp.get("platform", ""))

        screen_data = fp.get("screen", {})
        cores = safe_number(fp.get("cores", 0))
        mem = safe_number(fp.get("mem", 0))
        dpr = safe_number(
            screen_data.get("dpr", 1)
            if isinstance(screen_data, dict)
            else fp.get("dpr", 1)
        )

        # ─────────────────────────────────────
        # Deterministic environmental identity
        # ─────────────────────────────────────
        identity_core = "|".join([

            ua,
            lang,
            tz,
            platform,

            str(cores),
            str(mem),
            str(dpr),

            str(screen_data)

        ])

        fid = sha(identity_core)[:16]

        # ─────────────────────────────────────
        # Behavioral channels
        # ─────────────────────────────────────
        cpu = safe_list(fp.get("cpu"))
        timing = safe_list(fp.get("timing"))
        frame = safe_list(fp.get("frame"))
        focus = safe_list(fp.get("focus"))
        visibility = safe_list(fp.get("visibility"))
        net = safe_list(fp.get("net"))

        # ─────────────────────────────────────
        # Entropy extraction
        # ─────────────────────────────────────
        cpu_entropy = round(entropy(cpu), 4)
        timing_entropy = round(entropy(timing), 4)
        frame_entropy = round(entropy(frame), 4)

        # ─────────────────────────────────────
        # Behavioral coherence estimation
        # ─────────────────────────────────────
        coherence_score = round(

            (
                cpu_entropy +
                timing_entropy +
                frame_entropy
            ) / 3,

            4
        )

        # ─────────────────────────────────────
        # Identity continuity model
        # ─────────────────────────────────────
        previous = IDENTITIES.get(fid)

        anomaly = 0.0

        if previous is not None:

            anomaly = round(
                abs(previous - coherence_score),
                4
            )

        IDENTITIES[fid] = coherence_score

        # ─────────────────────────────────────
        # Network behavioral profile
        # ─────────────────────────────────────
        avg_rtt = 0
        drift = 0
        failed_requests = 0

        if net:

            valid_rtt = []

            for n in net:

                try:

                    if n.get("error"):
                        failed_requests += 1
                        continue

                    rtt = safe_number(n.get("rtt"))

                    if rtt > 0:
                        valid_rtt.append(rtt)

                    drift += abs(
                        safe_number(
                            n.get("drift", 0)
                        )
                    )

                except:
                    failed_requests += 1

            if valid_rtt:

                avg_rtt = round(
                    sum(valid_rtt) / len(valid_rtt),
                    2
                )

            drift = round(
                drift / max(len(net),1),
                4
            )

        # ─────────────────────────────────────
        # Statistical interpretation
        # ─────────────────────────────────────
        interpretation = []

        if coherence_score < 1:
            interpretation.append(
                "low behavioral variability"
            )

        if coherence_score > 6:
            interpretation.append(
                "high environmental fluctuation"
            )

        if anomaly > 2:
            interpretation.append(
                "identity drift detected"
            )

        if failed_requests > 2:
            interpretation.append(
                "network instability present"
            )

        if len(focus) == 0:
            interpretation.append(
                "passive interaction profile"
            )

        if len(visibility) > 4:
            interpretation.append(
                "frequent context switching"
            )

        # ─────────────────────────────────────
        # Cognitive environmental classification
        # ─────────────────────────────────────
        classification = "organic"

        if anomaly > 4:
            classification = "volatile"

        elif coherence_score < 0.8:
            classification = "synthetic"

        elif coherence_score > 5:
            classification = "unstable"

        # ─────────────────────────────────────
        # Signal persistence layer
        # ─────────────────────────────────────
        signal = {

            "id": fid,

            "time": now(),

            # ─── Identity Layer ───
            "ua": ua,
            "lang": lang,
            "platform": platform,
            "tz": tz,

            # ─── Display Layer ───
            "screen": screen_data,
            "dpr": dpr,
            "touch": fp.get("touch", 0),

            # ─── Hardware Layer ───
            "cores": cores,
            "mem": mem,

            # ─── Entropy Layer ───
            "cpu_entropy": cpu_entropy,
            "timing_entropy": timing_entropy,
            "frame_entropy": frame_entropy,

            # ─── Network Layer ───
            "rtt": avg_rtt,
            "clock_drift": drift,
            "network_failures": failed_requests,

            # ─── Behavioral Layer ───
            "focus_events": len(focus),
            "visibility_changes": len(visibility),

            # ─── Intelligence Layer ───
            "coherence": classification,
            "coherence_score": coherence_score,
            "anomaly": anomaly,

            # ─── Interpretation Layer ───
            "interpretation": interpretation
        }

        # ─────────────────────────────────────
        # Persist telemetry stream
        # ─────────────────────────────────────
        SESSIONS[token]["signals"].append(signal)

        SESSIONS[token]["last_seen"] = time.time()

        # ─────────────────────────────────────
        # Session evolution metadata
        # ─────────────────────────────────────
        SESSIONS[token]["status"] = classification

        # ─────────────────────────────────────
        # Final response
        # ─────────────────────────────────────
        return {

            "status": "ok",

            "id": fid,

            "classification": classification,

            "coherence_score": coherence_score,

            "anomaly": anomaly,

            "rtt": avg_rtt,

            "network_failures": failed_requests,

            "interpretation": interpretation

        }

    except Exception as e:

        return JSONResponse({

            "status": "collection-error",

            "message":
                "Telemetry processing failure",

            "details": str(e)

        }, status_code=500)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": time.time(),
        "sessions": len(SESSIONS)
    }


# ------------------ Token Page (LAST) ------------------

@app.get("/{token}")
def page(token: str):

    if token not in SESSIONS:

        return HTMLResponse("""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1.0">

<title>
HybridSignals — Invalid Session
</title>

<style>

:root {

    --bg:#050507;

    --panel:
      rgba(12,16,22,0.95);

    --line:
      rgba(255,255,255,0.06);

    --text:#e7fffb;

    --muted:#82d8ca;

    --primary:#00ffcc;
}

*{
    box-sizing:border-box;
}

html,body{

    margin:0;
    padding:0;

    width:100%;
    min-height:100%;

    background:

      radial-gradient(
        circle at top left,
        rgba(0,255,200,0.06),
        transparent 35%
      ),

      var(--bg);

    color:var(--text);

    font-family:
      Inter,
      "Segoe UI",
      monospace;
}

body{

    display:flex;

    align-items:center;

    justify-content:center;

    padding:24px;
}

.box{

    width:100%;

    max-width:480px;

    padding:38px 30px;

    border-radius:26px;

    background:

      linear-gradient(
        145deg,
        rgba(15,18,24,0.96),
        rgba(5,8,12,0.96)
      );

    border:
      1px solid var(--line);

    box-shadow:
      0 0 60px rgba(0,0,0,0.45);

    text-align:center;
}

.dot{

    width:10px;
    height:10px;

    margin:0 auto 18px;

    border-radius:50%;

    background:var(--primary);

    box-shadow:
      0 0 18px var(--primary);
}

.title{

    font-size:clamp(1.8rem,5vw,2.4rem);

    margin-bottom:14px;
}

.desc{

    opacity:0.78;

    color:var(--muted);

    line-height:1.9;

    font-size:0.95rem;
}

</style>
</head>

<body>

<div class="box">

    <div class="dot"></div>

    <div class="title">
      Session Unavailable
    </div>

    <div class="desc">

      The requested telemetry channel no longer exists,
      has expired or was never initialized.

      <br><br>

      Environmental synchronization cannot continue
      without a valid session layer.

    </div>

</div>

</body>
</html>
""", status_code=404)

    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1.0">

<title>
HybridSignals — Environmental Synchronization
</title>

<style>

:root {{

    --bg:#040506;

    --panel:
      rgba(10,14,20,0.95);

    --line:
      rgba(255,255,255,0.06);

    --primary:#00ffcc;

    --secondary:#7effee;

    --text:#ebfffc;

    --muted:#7fd8ca;
}}

* {{
    box-sizing:border-box;
}}

html,body {{

    margin:0;
    padding:0;

    width:100%;
    min-height:100%;

    background:

      radial-gradient(
        circle at top left,
        rgba(0,255,200,0.06),
        transparent 32%
      ),

      radial-gradient(
        circle at bottom right,
        rgba(0,140,255,0.06),
        transparent 36%
      ),

      var(--bg);

    color:var(--text);

    font-family:
      Inter,
      "Segoe UI",
      monospace;
}}

body {{
    position:relative;
    overflow-x:hidden;
}}

.grid {{

    position:fixed;

    inset:0;

    opacity:0.16;

    pointer-events:none;

    background-image:

      linear-gradient(
        rgba(255,255,255,0.02) 1px,
        transparent 1px
      ),

      linear-gradient(
        90deg,
        rgba(255,255,255,0.02) 1px,
        transparent 1px
      );

    background-size:42px 42px;
}}

.noise {{

    position:fixed;

    inset:0;

    opacity:0.03;

    pointer-events:none;

    background-image:
      url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cg fill='white'%3E%3Ccircle cx='2' cy='2' r='1'/%3E%3C/g%3E%3C/svg%3E");
}}

.glow {{

    position:fixed;

    width:760px;
    height:760px;

    top:-280px;
    right:-280px;

    background:
      radial-gradient(
        circle,
        rgba(0,255,200,0.10),
        transparent 72%
      );

    filter:blur(60px);

    pointer-events:none;

    animation:float 12s ease-in-out infinite;
}}

.glow2 {{

    position:fixed;

    width:540px;
    height:540px;

    bottom:-200px;
    left:-200px;

    background:
      radial-gradient(
        circle,
        rgba(0,120,255,0.08),
        transparent 72%
      );

    filter:blur(70px);

    pointer-events:none;

    animation:float2 16s ease-in-out infinite;
}}

@keyframes float {{

    0% {{
        transform:translateY(0px);
    }}

    50% {{
        transform:translateY(24px);
    }}

    100% {{
        transform:translateY(0px);
    }}
}}

@keyframes float2 {{

    0% {{
        transform:translateX(0px);
    }}

    50% {{
        transform:translateX(26px);
    }}

    100% {{
        transform:translateX(0px);
    }}
}}

.wrapper {{

    position:relative;

    width:100%;

    min-height:100vh;

    display:flex;

    align-items:center;

    justify-content:center;

    padding:28px 18px;
}}

.panel {{

    position:relative;

    width:100%;

    max-width:720px;

    padding:42px;

    border-radius:30px;

    overflow:hidden;

    background:

      linear-gradient(
        145deg,
        rgba(14,18,25,0.96),
        rgba(5,8,12,0.95)
      );

    border:
      1px solid var(--line);

    backdrop-filter:blur(18px);

    box-shadow:

      0 0 80px rgba(0,255,200,0.08),

      inset 0 0 28px rgba(255,255,255,0.02);
}}

.panel::before {{

    content:"";

    position:absolute;

    inset:0;

    background:

      linear-gradient(
        130deg,
        transparent,
        rgba(255,255,255,0.03),
        transparent
      );

    pointer-events:none;
}}

.topline {{

    display:flex;

    align-items:center;

    gap:12px;

    flex-wrap:wrap;

    color:var(--secondary);

    letter-spacing:2px;

    text-transform:uppercase;

    font-size:0.74rem;

    opacity:0.82;
}}

.dot {{

    width:9px;
    height:9px;

    border-radius:50%;

    background:var(--primary);

    box-shadow:
      0 0 16px var(--primary);
}}

h1 {{

    margin-top:24px;
    margin-bottom:16px;

    font-size:clamp(2rem,5vw,3rem);

    line-height:1.1;

    color:#f3fffd;
}}

.description {{

    color:var(--muted);

    line-height:1.95;

    opacity:0.84;

    font-size:0.96rem;
}}

.status-box {{

    margin-top:30px;

    padding:22px;

    border-radius:20px;

    background:
      rgba(255,255,255,0.02);

    border:
      1px solid rgba(255,255,255,0.05);
}}

.status-label {{

    font-size:0.72rem;

    text-transform:uppercase;

    letter-spacing:1px;

    opacity:0.56;
}}

.status-text {{

    margin-top:12px;

    line-height:1.8;

    font-size:1.02rem;

    color:#ddfffa;
}}

.loader {{

    margin-top:24px;

    position:relative;

    width:100%;
    height:5px;

    overflow:hidden;

    border-radius:999px;

    background:
      rgba(255,255,255,0.04);
}}

.loader::before {{

    content:"";

    position:absolute;

    top:0;
    left:-35%;

    width:35%;
    height:100%;

    border-radius:999px;

    background:

      linear-gradient(
        90deg,
        transparent,
        var(--primary),
        transparent
      );

    animation:scan 1.8s linear infinite;
}}

@keyframes scan {{

    0% {{
        left:-35%;
    }}

    100% {{
        left:100%;
    }}
}}

.metrics {{

    display:grid;

    grid-template-columns:
      repeat(auto-fit,minmax(160px,1fr));

    gap:16px;

    margin-top:30px;
}}

.metric {{

    padding:16px;

    border-radius:18px;

    background:
      rgba(255,255,255,0.02);

    border:
      1px solid rgba(255,255,255,0.04);
}}

.metric .label {{

    font-size:0.68rem;

    letter-spacing:1px;

    text-transform:uppercase;

    opacity:0.56;
}}

.metric .value {{

    margin-top:10px;

    color:var(--primary);

    font-size:1rem;

    font-weight:700;
}}

.quote {{

    margin-top:28px;

    padding:18px 0 0 16px;

    border-left:
      1px solid rgba(0,255,200,0.16);

    color:#9cefe1;

    opacity:0.76;

    line-height:1.9;

    font-size:0.9rem;
}}

.footer {{

    margin-top:32px;

    color:#77dccd;

    opacity:0.52;

    font-size:0.78rem;

    line-height:1.9;
}}

@media(max-width:768px) {{

    .wrapper {{
        padding:22px 14px;
    }}

    .panel {{
        padding:28px 22px;
        border-radius:24px;
    }}

    .description {{
        font-size:0.92rem;
    }}

    .status-text {{
        font-size:0.96rem;
    }}

    .metrics {{
        grid-template-columns:1fr;
    }}
}}

</style>
</head>

<body>

<div class="noise"></div>

<div class="grid"></div>

<div class="glow"></div>

<div class="glow2"></div>

<div class="wrapper">

    <div class="panel">

        <div class="topline">

            <div class="dot"></div>

            HYBRIDSIGNALS · ENVIRONMENTAL SYNCHRONIZATION Autor; ByMakaveliw

        </div>

        <h1>
          Temporal Behavioral Initialization
        </h1>

        <div class="description">

          Establishing synchronization between environmental timing,
          rendering behavior, interaction drift and execution variance.

          <br><br>

          This process does not attempt to observe identity alone.

          It attempts to understand how environments react
          under instability, interruption, timing pressure
          and behavioral fluctuation.

        </div>

        <div class="status-box">

            <div class="status-label">
              Current State
            </div>

            <div class="status-text"
                 id="status">

              Initializing environmental synchronization...

            </div>

            <div class="loader"></div>

        </div>

        <div class="metrics">

            <div class="metric">

                <div class="label">
                  Session Layer
                </div>

                <div class="value">
                  Active
                </div>

            </div>

            <div class="metric">

                <div class="label">
                  Signal Drift
                </div>

                <div class="value">
                  Monitoring
                </div>

            </div>

            <div class="metric">

                <div class="label">
                  Entropy Link
                </div>

                <div class="value">
                  Armed
                </div>

            </div>

        </div>

        <div class="quote">

          “Stable systems reveal repetition.
          Organic systems reveal inconsistency.
          Time eventually reveals both.”

        </div>

        <div class="footer">

          HybridSignals · Behavioral Drift Engine ·
          Environmental Coherence Layer ·
          Temporal Analysis Interface · 
          Autor; ByMakaveliw

        </div>

    </div>

</div>

<script src="/s.js"></script>

<script>

const statusEl =
  document.getElementById("status");

const states = [

  "Calibrating temporal channels...",

  "Observing environmental timing drift...",

  "Synchronizing behavioral entropy...",

  "Establishing execution coherence profile...",

  "Awaiting environmental fluctuation..."

];

let idx = 0;

setInterval(() => {{

    idx = (idx + 1) % states.length;

    statusEl.innerText =
      states[idx];

}}, 3200);

start("{token}");

</script>

</body>
</html>
""")