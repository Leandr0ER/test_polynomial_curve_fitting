<script lang="ts">
    interface Point {
        x: number;
        y?: number;
        t?: number;
    }

    interface FitResponse {
        points: Point[];
        fitted_curve: Point[];
        real_curve: Point[];
        weights: number[];
    }

    let N = $state(10);
    let M = $state(9);
    let lnLambda = $state(-18);
    let useRegularization = $state(false);
    let noiseLevel = $state(0.2);

    let data = $state<FitResponse | null>(null);
    let loading = $state(false);

    // Interactive state
    let hoveredPoint = $state<Point | null>(null);
    let mousePos = $state({ x: 0, y: 0 });

    // Reactive dimensions for full screen
    let containerWidth = $state(800);
    let containerHeight = $state(600);
    const padding = 70; // Increased padding for axis labels

    // Scale constants
    const yMin = -1.5;
    const yMax = 1.5;
    const yRange = yMax - yMin;

    // Responsive scaling functions
    function scaleX(x: number) {
        return padding + x * (containerWidth - 2 * padding);
    }
    function scaleY(y: number) {
        const normalized = (y - yMin) / yRange;
        return containerHeight - (padding + normalized * (containerHeight - 2 * padding));
    }

    async function fetchData() {
        loading = true;
        try {
            const response = await fetch('http://localhost:8000/fit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    N,
                    M,
                    ln_lambda: useRegularization ? lnLambda : null,
                    noise_level: noiseLevel
                })
            });
            const result: FitResponse = await response.json();
            data = result;
        } catch (e) {
            console.error("Error fetching data:", e);
        } finally {
            loading = false;
        }
    }

    $effect(() => {
        fetchData();
    });

    function getPath(points: Point[]) {
        if (!points || points.length === 0) return "";
        const validPoints = points
            .map((p: Point) => {
                const val = (p.y !== undefined) ? p.y : p.t;
                if (val === undefined || isNaN(val) || !isFinite(val)) return null;
                const clampedY = Math.max(yMin - 0.5, Math.min(yMax + 0.5, val));
                return { x: p.x, y: clampedY };
            })
            .filter((p): p is {x: number, y: number} => p !== null);

        if (validPoints.length === 0) return "";
        return "M " + validPoints.map(p => `${scaleX(p.x)},${scaleY(p.y)}`).join(" L ");
    }

    function resetToDefaults() {
        N = 10;
        M = 9;
        lnLambda = -18;
        useRegularization = false;
        noiseLevel = 0.2;
    }

    function handlePointEnter(p: Point, event: MouseEvent) {
        hoveredPoint = p;
        mousePos = { x: event.clientX, y: event.clientY };
    }

    function handlePointLeave() {
        hoveredPoint = null;
    }

    // Ticks generation
    const xTicks = [0, 0.2, 0.4, 0.6, 0.8, 1.0];
    const yTicks = [-1.0, -0.5, 0, 0.5, 1.0];
</script>

<div class="app-container">
    <aside class="sidebar">
        <h1>Bishop 1.1</h1>
        <p class="subtitle">Polynomial Curve Fitting</p>
        
        <div class="controls">
            <div class="control-group">
                <label for="n-points">Points (N): <strong>{N}</strong></label>
                <input id="n-points" type="range" bind:value={N} min="3" max="100" />
            </div>

            <div class="control-group">
                <label for="m-degree">Degree (M): <strong>{M}</strong></label>
                <input id="m-degree" type="range" bind:value={M} min="0" max="9" />
            </div>

            <div class="control-group checkbox">
                <input id="use-reg" type="checkbox" bind:checked={useRegularization} />
                <label for="use-reg">Use Regularization (λ)</label>
            </div>

            {#if useRegularization}
                <div class="control-group">
                    <label for="ln-lambda">ln λ: <strong>{lnLambda}</strong></label>
                    <input id="ln-lambda" type="range" bind:value={lnLambda} min="-40" max="0" step="1" />
                </div>
            {/if}

            <div class="control-group">
                <label for="noise">Noise level: <strong>{noiseLevel}</strong></label>
                <input id="noise" type="range" bind:value={noiseLevel} min="0" max="1" step="0.05" />
            </div>

            <button class="reset-btn" onclick={resetToDefaults}>
                Reset to Defaults
            </button>
        </div>

        {#if data}
            <div class="weights-box">
                <h3>Model Weights (w*)</h3>
                <div class="weights-list">
                    {#each data.weights as w, i}
                        <div class="weight-item">
                            <span class="weight-label">w<sub>{i}</sub>:</span>
                            <span class="weight-value">{w.toFixed(2)}</span>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}

        <div class="info-box">
            <h3>Quick Experiments</h3>
            <ul>
                <li><strong>Over-fitting:</strong> M=9, N=10</li>
                <li><strong>Regularized:</strong> Add ln λ ≈ -18</li>
                <li><strong>Big Data:</strong> N=100, M=9</li>
            </ul>
        </div>

        {#if !data && !loading}
            <div class="error-msg">
                ⚠️ Backend connection failed (port 8000).
            </div>
        {/if}
    </aside>

    <main class="visualization" bind:clientWidth={containerWidth} bind:clientHeight={containerHeight}>
        <svg width={containerWidth} height={containerHeight} viewBox="0 0 {containerWidth} {containerHeight}">
            <rect width={containerWidth} height={containerHeight} fill="#fff" />
            
            <!-- Grid Lines -->
            <line x1={padding} y1={containerHeight-padding} x2={containerWidth-padding} y2={containerHeight-padding} stroke="#eee" stroke-width="2" />
            <line x1={padding} y1={padding} x2={padding} y2={containerHeight-padding} stroke="#eee" stroke-width="2" />

            <!-- Chart Title -->
            <text x={containerWidth/2} y={30} text-anchor="middle" fill="#212529" font-size="25" font-weight="bold">Polynomial Curve Fitting</text>

            <!-- Legend Group (Top Right) -->
            <g transform="translate({containerWidth - padding - 160}, {padding + 10})">
                <rect x="-10" y="-10" width="170" height="85" fill="white" fill-opacity="0.9" stroke="#eee" rx="6" />
                
                <!-- Target Legend -->
                <line x1="0" y1="10" x2="30" y2="10" stroke="#2ecc71" stroke-width="2" stroke-dasharray="5,3" />
                <text x="40" y="15" fill="#495057" font-size="12">Target function</text>
                
                <!-- Fitted Legend -->
                <line x1="0" y1="35" x2="30" y2="35" stroke="#e74c3c" stroke-width="3" />
                <text x="40" y="40" fill="#495057" font-size="12">Fitted Model</text>
                
                <!-- Samples Legend -->
                <circle cx="15" cy="60" r="5" fill="white" stroke="#3498db" stroke-width="2" />
                <text x="40" y="65" fill="#495057" font-size="12">Data Samples</text>
            </g>

            <!-- Axes Lines -->
            <line x1={padding} y1={containerHeight-padding} x2={containerWidth-padding} y2={containerHeight-padding} stroke="#333" stroke-width="2" />
            <line x1={padding} y1={padding} x2={padding} y2={containerHeight-padding} stroke="#333" stroke-width="2" />

            <!-- X Axis Ticks and Labels -->
            {#each xTicks as tick}
                <line x1={scaleX(tick)} y1={containerHeight-padding} x2={scaleX(tick)} y2={containerHeight-padding + 8} stroke="#333" stroke-width="2" />
                <text x={scaleX(tick)} y={containerHeight-padding + 25} text-anchor="middle" fill="#666" font-size="12">{tick.toFixed(1)}</text>
            {/each}
            <text x={containerWidth/2} y={containerHeight-15} text-anchor="middle" fill="#333" font-weight="bold" font-size="14">x (input variable)</text>

            <!-- Y Axis Ticks and Labels -->
            {#each yTicks as tick}
                <line x1={padding-8} y1={scaleY(tick)} x2={padding} y2={scaleY(tick)} stroke="#333" stroke-width="2" />
                <text x={padding-15} y={scaleY(tick) + 4} text-anchor="end" fill="#666" font-size="12">{tick.toFixed(1)}</text>
                <!-- Horizontal Grid Line -->
                <line x1={padding} y1={scaleY(tick)} x2={containerWidth-padding} y2={scaleY(tick)} stroke="#f0f0f0" stroke-width="1" />
            {/each}
            <text x={20} y={containerHeight/2} text-anchor="middle" fill="#333" font-weight="bold" font-size="14" transform="rotate(-90, 20, {containerHeight/2})">y (target)</text>

            {#if data}
                <!-- Target function -->
                <path d={getPath(data.real_curve)} fill="none" stroke="#2ecc71" stroke-width="2" stroke-dasharray="8,4" />
                
                <!-- Prediction model -->
                <path d={getPath(data.fitted_curve)} fill="none" stroke="#e74c3c" stroke-width="4" />

                <!-- Samples -->
                {#each data.points as p}
                    <circle 
                        cx={scaleX(p.x)} 
                        cy={scaleY(p.t ?? 0)} 
                        r={hoveredPoint === p ? 10 : 6} 
                        fill={hoveredPoint === p ? "#3498db" : "white"} 
                        stroke="#3498db" 
                        stroke-width="3" 
                        style="cursor: crosshair; transition: all 0.2s;"
                        onmouseenter={(e) => handlePointEnter(p, e)}
                        onmouseleave={handlePointLeave}
                    />
                {/each}
            {/if}

            {#if loading}
                <text x={containerWidth/2} y={containerHeight/2} text-anchor="middle" fill="#bdc3c7" font-size="24" font-style="italic">Updating Matrix...</text>
            {/if}
        </svg>

        {#if hoveredPoint}
            <div class="tooltip" style="left: {mousePos.x + 15}px; top: {mousePos.y - 15}px;">
                <div class="tooltip-row">
                    <span class="tooltip-label">x:</span>
                    <span class="tooltip-value">{hoveredPoint.x.toFixed(4)}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">target (y):</span>
                    <span class="tooltip-value">{(hoveredPoint.t ?? 0).toFixed(4)}</span>
                </div>
            </div>
        {/if}
    </main>
</div>

<style>
    :global(body, html) {
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        overflow: hidden;
        font-family: 'Inter', -apple-system, sans-serif;
        background: #f8f9fa;
    }

    .app-container {
        display: flex;
        width: 100vw;
        height: 100vh;
    }

    .sidebar {
        width: 320px;
        background: white;
        border-right: 1px solid #e9ecef;
        padding: 2rem;
        display: flex;
        flex-direction: column;
        box-shadow: 4px 0 15px rgba(0,0,0,0.05);
        z-index: 10;
        overflow-y: auto;
    }

    h1 {
        margin: 0;
        font-size: 1.5rem;
        color: #212529;
    }

    .subtitle {
        color: #6c757d;
        margin-bottom: 2rem;
        font-size: 0.9rem;
    }

    .controls {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .control-group {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .control-group label {
        font-size: 0.85rem;
        color: #495057;
    }

    .control-group.checkbox {
        flex-direction: row;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
    }

    input[type="range"] {
        width: 100%;
        accent-color: #3498db;
    }

    .reset-btn {
        margin-top: 0.5rem;
        padding: 0.75rem;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        color: #495057;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        font-family: inherit;
    }

    .reset-btn:hover {
        background: #e9ecef;
        border-color: #ced4da;
    }

    .reset-btn:active {
        background: #dee2e6;
        transform: translateY(1px);
    }

    .weights-box {
        margin-top: 1.5rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }

    .weights-box h3 {
        margin: 0 0 0.75rem 0;
        font-size: 0.9rem;
        color: #212529;
    }

    .weights-list {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .weight-item {
        display: flex;
        justify-content: space-between;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.75rem;
        background: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        border: 1px solid #f1f3f5;
    }

    .weight-label {
        color: #6c757d;
        font-weight: bold;
        min-width: 30px;
    }

    .weight-value {
        color: #e74c3c;
        text-align: right;
        flex-grow: 1;
    }

    .info-box {
        margin-top: 2rem;
        padding: 1rem;
        background: #f1f3f5;
        border-radius: 8px;
        font-size: 0.85rem;
    }

    .info-box h3 {
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
    }

    .info-box ul {
        margin: 0;
        padding-left: 1.2rem;
        color: #495057;
    }

    .visualization {
        flex-grow: 1;
        position: relative;
        background: white;
    }

    .tooltip {
        position: fixed;
        pointer-events: none;
        background: rgba(33, 37, 41, 0.95);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        z-index: 100;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255,255,255,0.1);
    }

    .tooltip-row {
        display: flex;
        justify-content: space-between;
        gap: 1.5rem;
    }

    .tooltip-label {
        color: #adb5bd;
        font-weight: 500;
    }

    .tooltip-value {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: #3498db;
    }

    .error-msg {
        margin-top: 1rem;
        color: #e74c3c;
        font-size: 0.8rem;
        background: #fff5f5;
        padding: 0.75rem;
        border-radius: 6px;
        border: 1px solid #fed7d7;
    }

    svg {
        display: block;
    }
</style>
