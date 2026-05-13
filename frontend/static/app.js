/**
 * NEURAL TRAFFIC COMMAND — Olive/Maroon Tactical Dashboard
 * Form validation, clean edge rendering, descriptive output
 */
document.addEventListener('DOMContentLoaded', () => {

    const form          = document.getElementById('request-form');
    const submitBtn     = document.getElementById('submit-btn');
    const originSelect  = document.getElementById('currentLocation');
    const destSelect    = document.getElementById('destination');
    const resultsGrid   = document.getElementById('results-grid');
    const resultsHolder = document.getElementById('results-placeholder');
    const canvas        = document.getElementById('city-canvas');
    const ctx           = canvas.getContext('2d');
    const statusText    = document.querySelector('.status-text');

    let graphData  = { nodes: [], edges: [] };
    let activePath = [];

    /* ═══════ PARTICLE BACKGROUND (olive tint) ═══════ */
    class ParticleBG {
        constructor(el) {
            this.c = el; this.cx = el.getContext('2d'); this.particles = [];
            this.resize(); this.spawn(65); this.loop();
            window.addEventListener('resize', () => this.resize());
        }
        resize() { this.c.width = window.innerWidth; this.c.height = window.innerHeight; }
        spawn(n) {
            for (let i = 0; i < n; i++) this.particles.push({
                x: Math.random()*this.c.width, y: Math.random()*this.c.height,
                vx: (Math.random()-0.5)*0.35, vy: (Math.random()-0.5)*0.35,
                r: Math.random()*1.6+0.4, o: Math.random()*0.25+0.06
            });
        }
        loop() {
            this.cx.clearRect(0,0,this.c.width,this.c.height);
            const pts = this.particles;
            for (let i=0; i<pts.length; i++) for (let j=i+1; j<pts.length; j++) {
                const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y, d=Math.sqrt(dx*dx+dy*dy);
                if (d<130) { this.cx.beginPath(); this.cx.moveTo(pts[i].x,pts[i].y); this.cx.lineTo(pts[j].x,pts[j].y);
                    this.cx.strokeStyle=`rgba(139,154,62,${0.06*(1-d/130)})`; this.cx.lineWidth=0.6; this.cx.stroke(); }
            }
            pts.forEach(p => {
                p.x+=p.vx; p.y+=p.vy;
                if(p.x<0||p.x>this.c.width)p.vx*=-1; if(p.y<0||p.y>this.c.height)p.vy*=-1;
                this.cx.beginPath(); this.cx.arc(p.x,p.y,p.r,0,Math.PI*2);
                this.cx.fillStyle=`rgba(139,154,62,${p.o})`; this.cx.fill();
            });
            requestAnimationFrame(() => this.loop());
        }
    }
    const bgCanvas = document.getElementById('particle-bg');
    if (bgCanvas) new ParticleBG(bgCanvas);

    /* ═══════ FORM VALIDATION ═══════ */
    function checkFormValid() {
        const vt = document.getElementById('vehicleType').value;
        const rc = document.getElementById('requestCategory').value;
        const ol = originSelect.value;
        const dl = destSelect.value;
        const valid = vt && rc && ol && dl;
        submitBtn.disabled = !valid;
    }

    ['vehicleType','requestCategory'].forEach(id => {
        document.getElementById(id).addEventListener('change', checkFormValid);
    });

    /* ═══════ SLIDER VALUES ═══════ */
    // (Severity is now a radio button group, Time Sensitive is a checkbox)

    /* ═══════ INIT ═══════ */
    async function init() {
        try {
            const [locRes, graphRes] = await Promise.all([fetch('/api/locations'), fetch('/api/graph')]);
            const locations = await locRes.json();
            graphData = await graphRes.json();

            originSelect.innerHTML = '<option value="" disabled selected>Select Origin</option>';
            destSelect.innerHTML   = '<option value="" disabled selected>Select Destination</option>';
            locations.forEach(loc => {
                originSelect.add(new Option(loc.label, loc.id));
                destSelect.add(new Option(loc.label, loc.id));
            });

            originSelect.addEventListener('change', () => { checkFormValid(); renderGraph(); });
            destSelect.addEventListener('change', () => { checkFormValid(); renderGraph(); });

            renderGraph();
            if (statusText) statusText.textContent = 'SYSTEM ONLINE';
        } catch (err) {
            console.error('Init error:', err);
            if (statusText) statusText.textContent = 'CONNECTION ERROR';
        }
    }

    /* ═══════ MAP RENDERING (Clean Edges) ═══════ */
    function renderGraph() {
        if (!ctx) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw edges — clean and visible
        graphData.edges.forEach(edge => {
            const from = graphData.nodes.find(n => n.id === edge.from);
            const to   = graphData.nodes.find(n => n.id === edge.to);
            if (!from || !to) return;
            const onPath = isInPath(edge.from, edge.to);

            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);

            if (onPath) {
                ctx.shadowColor = '#b5c44e';
                ctx.shadowBlur  = 16;
                ctx.lineWidth   = 4;
                ctx.strokeStyle = '#b5c44e';
            } else {
                ctx.shadowBlur  = 0;
                ctx.lineWidth   = 1.8;
                ctx.strokeStyle = 'rgba(200,195,175,0.22)';
            }
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Weight label — pill background for visibility
            const mx = (from.x + to.x) / 2;
            const my = (from.y + to.y) / 2;
            const wt = String(edge.weight);
            ctx.font = '600 10px Inter';
            const tw = ctx.measureText(wt).width;
            ctx.fillStyle = 'rgba(10,10,8,0.75)';
            ctx.beginPath();
            ctx.roundRect(mx - tw/2 - 5, my - 8, tw + 10, 16, 4);
            ctx.fill();
            ctx.fillStyle = onPath ? '#b5c44e' : 'rgba(220,215,200,0.7)';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(wt, mx, my);
        });

        // Draw nodes
        graphData.nodes.forEach(node => {
            const onPath = activePath.includes(node.id);
            const isOrig = node.id === originSelect.value;
            const isDest = node.id === destSelect.value;
            const r      = onPath ? 13 : 9;

            if (onPath) { ctx.shadowColor = '#b5c44e'; ctx.shadowBlur = 20; }

            ctx.beginPath();
            ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
            ctx.fillStyle = nodeColor(node.type, onPath);
            ctx.fill();

            // Origin/Dest ring
            if (isOrig || isDest) {
                ctx.strokeStyle = '#8b1a2b';
                ctx.lineWidth = 3;
                ctx.stroke();
            }
            ctx.shadowBlur = 0;

            // Label
            ctx.font = '600 10px Inter';
            ctx.fillStyle = '#d5d0c4';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillText(node.label, node.x, node.y + r + 6);
        });
    }

    function nodeColor(type, active) {
        if (active) return '#b5c44e';
        return { hospital:'#8b1a2b', fire:'#c47a20', police:'#4a6fa5', intersection:'#6b6b5e', commercial:'#7a6b8a' }[type] || '#6b8e3e';
    }

    function isInPath(u, v) {
        if (!activePath || activePath.length < 2) return false;
        for (let i = 0; i < activePath.length - 1; i++)
            if ((activePath[i]===u && activePath[i+1]===v) || (activePath[i]===v && activePath[i+1]===u)) return true;
        return false;
    }

    /* ═══════ FORM SUBMIT ═══════ */
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        submitBtn.disabled = true;
        submitBtn.querySelector('.btn-text').textContent = 'PROCESSING...';

        resultsHolder.style.display = 'none';
        resultsGrid.style.display = 'flex';
        resultsGrid.innerHTML = '<div class="loading-state"><div class="loading-spinner"></div><p>Routing through AI modules...</p></div>';
        resetPipeline();

        try {
            const res = await fetch('/api/process', {
                method:'POST', headers:{'Content-Type':'application/json'},
                body: JSON.stringify({
                    vehicleType:     document.getElementById('vehicleType').value,
                    requestCategory: document.getElementById('requestCategory').value,
                    currentLocation: originSelect.value,
                    destination:     destSelect.value,
                    severity:        document.querySelector('input[name="severity"]:checked').value,
                    timeSensitive:   document.getElementById('timeSensitive').checked
                })
            });
            const data = await res.json();
            if (data.success) { renderResults(data); animatePipeline(data); }
            else resultsGrid.innerHTML = `<div class="error-box"><strong>Error:</strong> ${data.error}</div>`;
        } catch (err) {
            resultsGrid.innerHTML = '<div class="error-box"><strong>Network Error:</strong> Ensure app.py is running.</div>';
        } finally {
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').textContent = 'ENGAGE SYSTEM';
            checkFormValid();
        }
    });

    /* ═══════ RENDER RESULTS (Descriptive) ═══════ */
    function renderResults(data) {
        activePath = (data.modules.route && data.modules.route.path) ? data.modules.route.path : [];
        renderGraph();

        let html = '';

        // ANN Priority — descriptive
        if (data.modules.ann) {
            const lvl = data.modules.ann.priority.toLowerCase();
            const desc = {
                critical: 'Immediate action required. All available resources should be mobilized to handle this request with maximum urgency.',
                high: 'Elevated urgency detected. This request should be processed ahead of standard traffic and given priority routing.',
                normal: 'Standard priority level. The request will be processed through normal traffic management protocols.',
                low: 'Low urgency. This request can be handled through standard routing with no special interventions.'
            };
            html += `
                <div class="r-card">
                    <div class="r-tag">ANN PRIORITY ASSESSMENT</div>
                    <div class="r-desc">The Artificial Neural Network analyzed 4 normalized input features (vehicle type, severity, time sensitivity, traffic density) using a multi-layer perceptron with sigmoid activation.</div>
                    <div class="r-badge ${lvl}">${data.modules.ann.priority}</div>
                    <p class="r-desc">${desc[lvl] || ''}</p>
                    <div class="conf-wrap">
                        <div class="conf-lbl">Model Confidence: ${data.modules.ann.confidence}%</div>
                        <div class="conf-track"><div class="conf-fill" style="width:${data.modules.ann.confidence}%"></div></div>
                    </div>
                </div>`;
        }

        // Knowledge Base — descriptive
        if (data.modules.kb) {
            const auth = data.modules.kb.emergencyRouteAuth;
            const ruleCount = data.modules.kb.rulesFired ? data.modules.kb.rulesFired.length : 0;
            html += `
                <div class="r-card">
                    <div class="r-tag">KNOWLEDGE BASE POLICY ENGINE</div>
                    <div class="r-desc">The rule-based expert system evaluated ${ruleCount} traffic regulation rule(s) using forward chaining inference. ${data.modules.kb.notes || 'Standard policies apply to this request.'}</div>
                    <div class="r-row"><span>Route Authorization</span><span class="auth-badge ${auth?'auth-yes':'auth-no'}">${auth?'APPROVED':'STANDARD'}</span></div>
                    ${data.modules.kb.overridePriority ? `<div class="r-row"><span>KB Override Priority</span><span>${data.modules.kb.overridePriority}</span></div>` : ''}
                    ${data.modules.kb.signalOverride ? `<div class="r-row"><span>Signal Preemption</span><span style="color:var(--maroon-lit)">OVERRIDE ACTIVE</span></div>` : ''}
                    ${ruleCount > 0
                        ? `<div class="rule-chips">${data.modules.kb.rulesFired.map(r => `<span class="rule-chip" title="${r}">${r.split(':')[0]}</span>`).join('')}</div>`
                        : ''}
                </div>`;
        }

        // CSP Scheduler — descriptive
        if (data.modules.csp) {
            const cnt = Object.keys(data.modules.csp).length;
            html += `
                <div class="r-card">
                    <div class="r-tag">CSP SIGNAL SCHEDULER</div>
                    <div class="r-desc">The Constraint Satisfaction Problem solver used backtracking search to assign conflict-free signal phases to ${cnt} managed intersection(s). Adjacent intersections are guaranteed to have different phases to prevent traffic conflicts.</div>
                    <div class="csp-list">
                        ${Object.entries(data.modules.csp).map(([node, phase]) =>
                            `<div class="csp-row"><span>${node.replace(/_/g,' ')}</span><b>${phase}</b></div>`
                        ).join('')}
                    </div>
                </div>`;
        }

        // Navigation — descriptive
        if (data.modules.route) {
            const labels = data.modules.route.pathLabels || data.modules.route.path || [];
            const algoDesc = {
                'BFS': 'Breadth-First Search (optimal hop count for unweighted graphs)',
                'ASTAR': 'A* Search (optimal cost path using heuristic-guided expansion)',
                'UCS': 'Uniform Cost Search / Dijkstra (optimal cost without heuristic)'
            };
            html += `
                <div class="r-card">
                    <div class="r-tag">SEARCH & NAVIGATION</div>
                    <div class="r-desc">The ${algoDesc[data.modules.route.algorithm] || data.modules.route.algorithm} algorithm explored the city road network graph and computed the optimal route between the specified origin and destination nodes.</div>
                    <div class="r-row"><span>Algorithm</span><span>${data.modules.route.algorithm}</span></div>
                    <div class="r-row"><span>Total Travel Cost</span><span>${data.modules.route.cost} units</span></div>
                    <div class="r-row"><span>Path Length</span><span>${labels.length} nodes</span></div>
                    <div class="path-viz">
                        ${labels.map((n, i) =>
                            `<span class="path-node">${n}</span>${i < labels.length-1 ? '<span class="path-arrow">&#8594;</span>' : ''}`
                        ).join('')}
                    </div>
                </div>`;
        }

        // Final Decision — descriptive
        html += `
            <div class="r-card r-card-decision">
                <div class="r-tag">OPERATIONAL DECISION</div>
                <p>${data.decision.action}</p>
                <p class="r-desc" style="margin-top:8px;color:rgba(234,229,218,0.6);font-style:normal;">Effective Priority: <strong>${data.decision.priority}</strong></p>
            </div>`;

        resultsGrid.innerHTML = html;
    }

    /* ═══════ PIPELINE ═══════ */
    function resetPipeline() {
        document.querySelectorAll('.pipe-node').forEach(n => { n.classList.remove('active'); n.querySelector('.pipe-time').textContent = '--'; });
        document.querySelectorAll('.pipe-connector').forEach(c => c.classList.remove('active'));
    }

    function animatePipeline(data) {
        const steps = ['Preprocessing','annPriority','knowledgeBase','cspScheduler','searchNavigation','Response'];
        const nodes = document.querySelectorAll('.pipe-node');
        const conns = document.querySelectorAll('.pipe-connector');
        let delay = 0;
        steps.forEach((step, i) => {
            const time = data.timing[step];
            if (time) {
                delay += 150;
                setTimeout(() => {
                    nodes[i].classList.add('active');
                    nodes[i].querySelector('.pipe-time').textContent = time + 'ms';
                    if (i > 0 && conns[i-1]) conns[i-1].classList.add('active');
                }, delay);
            }
        });
    }

    /* ═══════ 3D TILT ═══════ */
    document.querySelectorAll('.neo-card').forEach(card => {
        card.addEventListener('mousemove', e => {
            const r = card.getBoundingClientRect();
            const rx = ((e.clientY-r.top-r.height/2)/(r.height/2))*-2.5;
            const ry = ((e.clientX-r.left-r.width/2)/(r.width/2))*2.5;
            card.style.transform = `perspective(800px) rotateX(${rx}deg) rotateY(${ry}deg)`;
        });
        card.addEventListener('mouseleave', () => { card.style.transform = 'perspective(800px) rotateX(0) rotateY(0)'; });
    });

    init();
});
