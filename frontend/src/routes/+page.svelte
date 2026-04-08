<script>
    let N = $state(10);
    let M = $state(9);
    let lnLambda = $state(-18);
    let useRegularization = $state(false);
    let noiseLevel = $state(0.2);

    let data = $state(null);
    let loading = $state(false);

    // Reactive dimensions for full screen
    let containerWidth = $state(800);
    let containerHeight = $state(600);
    const padding = 70; // Increased padding for axis labels

    // Scale constants
    const yMin = -1.5;
    const yMax = 1.5;
    const yRange = yMax - yMin;

    // Responsive scaling functions
    function scaleX(x) {
        return padding + x * (containerWidth - 2 * padding);
    }
    function scaleY(y) {
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
            const result = await response.json();
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

    function getPath(points) {
        if (!points || points.length === 0) return "";
        const validPoints = points
            .map(p => {
                const val = (p.y !== undefined) ? p.y : p.t;
                if (isNaN(val) || !isFinite(val)) return null;
                const clampedY = Math.max(yMin - 0.5, Math.min(yMax + 0.5, val));
                return { x: p.x, y: clampedY };
            })
            .filter(p => p !== null);

        if (validPoints.length === 0) return "";
        return "M " + validPoints.map(p => `${scaleX(p.x)},${scaleY(p.y)}`).join(" L ");
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
        </div>

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
        
        <div class="legend">
            <div class="item"><span class="color real"></span> Target function</div>
            <div class="item"><span class="color fitted"></span> Fitted Model</div>
            <div class="item"><span class="color points"></span> Data Samples</div>
        </div>
    </aside>

    <main class="visualization" bind:clientWidth={containerWidth} bind:clientHeight={containerHeight}>
        <svg width={containerWidth} height={containerHeight} viewBox="0 0 {containerWidth} {containerHeight}">
            <rect width={containerWidth} height={containerHeight} fill="#fff" />
            
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
            <text x={20} y={containerHeight/2} text-anchor="middle" fill="#333" font-weight="bold" font-size="14" transform="rotate(-90, 20, {containerHeight/2})">target (y)</text>

            {#if data}
                <!-- Target function -->
                <path d={getPath(data.real_curve)} fill="none" stroke="#2ecc71" stroke-width="2" stroke-dasharray="8,4" />
                
                <!-- Prediction model -->
                <path d={getPath(data.fitted_curve)} fill="none" stroke="#e74c3c" stroke-width="4" />

                <!-- Samples -->
                {#each data.points as p}
                    <circle cx={scaleX(p.x)} cy={scaleY(p.t)} r="6" fill="white" stroke="#3498db" stroke-width="3" />
                {/each}
            {/if}

            {#if loading}
                <text x={containerWidth/2} y={containerHeight/2} text-anchor="middle" fill="#bdc3c7" font-size="24" font-style="italic">Updating Matrix...</text>
            {/if}
        </svg>
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

    .legend {
        margin-top: auto;
        padding-top: 2rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
        font-size: 0.85rem;
    }

    .item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .color {
        width: 14px;
        height: 14px;
        border-radius: 4px;
    }

    .real { border: 2px dashed #2ecc71; }
    .fitted { background: #e74c3c; }
    .points { border: 2px solid #3498db; background: white; }

    .visualization {
        flex-grow: 1;
        position: relative;
        background: white;
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
