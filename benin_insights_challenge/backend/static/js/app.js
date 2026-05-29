// backend/static/js/app.js — TERROIR BeninScope
// Vue 3 app (CDN) — routing par hash, 4 vues.
// La logique Leaflet est déléguée à TerroirMap (map.js).

const { createApp, ref, computed, reactive, watch, nextTick } = Vue;

// ── Références département (centroides) ───────────────────────────────────
const DEPARTMENTS = [
  { code: "BN01", name: "Alibori",    lat: 11.50, lon: 2.80 },
  { code: "BN02", name: "Atacora",    lat: 10.50, lon: 1.50 },
  { code: "BN03", name: "Donga",      lat:  9.80, lon: 1.70 },
  { code: "BN04", name: "Borgou",     lat:  9.80, lon: 2.80 },
  { code: "BN05", name: "Collines",   lat:  8.50, lon: 2.20 },
  { code: "BN06", name: "Atlantique", lat:  6.60, lon: 2.20 },
  { code: "BN07", name: "Littoral",   lat:  6.37, lon: 2.42 },
  { code: "BN08", name: "Ouémé",      lat:  6.70, lon: 2.60 },
  { code: "BN09", name: "Couffo",     lat:  7.00, lon: 1.90 },
  { code: "BN10", name: "Zou",        lat:  7.50, lon: 2.30 },
  { code: "BN11", name: "Plateau",    lat:  7.20, lon: 2.90 },
  { code: "BN12", name: "Mono",       lat:  6.90, lon: 1.60 },
  { code: "BN18", name: "Parakou",    lat:  9.337, lon: 2.628 },
];

let _timelineRendered    = false;
let _sttChartRendered    = false;
let _gdeltStatusInterval = null;
let _mapRefreshInterval  = null;   // rafraîchit incidents + marqueurs toutes les 60 s

// ─────────────────────────────────────────────────────────────────────────
createApp({
  setup() {

    // ── Routing ─────────────────────────────────────────────────────────
    const currentRoute = ref(
      (window.location.hash && window.location.hash.length > 1)
        ? window.location.hash
        : "#/live"
    );
    if (!window.location.hash || window.location.hash.length <= 1) {
      window.location.replace("#/live");
    }
    window.addEventListener("hashchange", () => {
      currentRoute.value = window.location.hash;
    });

    // ── Toast ────────────────────────────────────────────────────────────
    const toastMessage = ref("");
    function showToast(msg, type = "success") {
      const el = document.getElementById("terroir-toast");
      if (!el) return;
      el.className = `toast align-items-center text-bg-${type} border-0`;
      toastMessage.value = msg;
      bootstrap.Toast.getOrCreateInstance(el, { delay: 3500 }).show();
    }

    // ── CARTE LIVE ───────────────────────────────────────────────────────
    const mapFilter       = ref("all");
    const mapLimit        = ref(500);
    const mapHours        = ref(720);   // défaut : 30 jours
    const excludeNigeria  = ref(false); // défaut : Nigeria inclus
    const mapStatus = reactive({
      loading:       false,
      error:         null,
      incidentError: null,
      gdeltCount:    0,
      securityCount: 0,
      incidentCount: 0,
      lastUpdate:    null,
      windowInfo:    null,
      idnPct:        null,
    });

    const MAP_HOURS_LABELS = {
      24:  "24 dernières heures",
      72:  "72 dernières heures",
      168: "7 derniers jours",
      720: "30 derniers jours",
    };

    const mapHoursLabel = computed(() =>
      MAP_HOURS_LABELS[mapHours.value] || `${mapHours.value}h`
    );

    function updateMapStatus(s) { Object.assign(mapStatus, s); }

    function loadLiveMap() {
      TerroirMap.loadLiveMap(
        mapFilter.value, parseInt(mapLimit.value), mapHours.value,
        excludeNigeria.value
      );
    }

    function setMapFilter(f) { mapFilter.value = f; loadLiveMap(); }
    function setMapHours(h)  { mapHours.value  = h; loadLiveMap(); }
    function refreshLiveMap() { loadLiveMap(); }

    function toggleNigeria() {
      excludeNigeria.value = !excludeNigeria.value;
      loadLiveMap();
    }

    // ── GDELT LIVE STATUS ────────────────────────────────────────────────
    const gdelt = reactive({
      loading:    false,
      refreshing: false,
      data:       null,
      error:      null,
    });

    async function loadGdeltStatus() {
      gdelt.loading = true;
      try {
        gdelt.data  = await apiGet("/gdelt/status");
        gdelt.error = null;
      } catch (_) {
        gdelt.error = "Statut GDELT indisponible.";
      } finally {
        gdelt.loading = false;
      }
    }

    async function refreshGdelt() {
      if (gdelt.refreshing) return;
      gdelt.refreshing = true;
      gdelt.error = null;
      try {
        const res = await apiPost("/gdelt/refresh", {});
        gdelt.data = await apiGet("/gdelt/status");
        const type = res.status === "error" ? "warning" : "success";
        showToast(res.message || "Cycle GDELT terminé.", type);
        loadLiveMap();
      } catch (err) {
        gdelt.error = "Erreur lors du rafraîchissement GDELT.";
        showToast("Erreur lors du rafraîchissement GDELT.", "danger");
      } finally {
        gdelt.refreshing = false;
      }
    }

    function gdeltStatusClass(status) {
      if (status === "ok")       return "gdelt-dot-ok";
      if (status === "error")    return "gdelt-dot-error";
      if (status === "checking") return "gdelt-dot-checking";
      return "gdelt-dot-pending";
    }

    function gdeltCoordLabel(quality) {
      if (!quality) return { exact: 0, dept: 0, country: 0 };
      return {
        exact:   (quality.action_geo || 0) + (quality.actor1_geo || 0) + (quality.actor2_geo || 0),
        dept:    quality.centroid_adm1    || 0,
        country: quality.centroid_country || 0,
      };
    }

    // ── STT / TERROIR ─────────────────────────────────────────────────────
    const stt = reactive({ loading: false, scores: [], error: null, incCount: null });

    async function loadStt() {
      stt.loading = true;
      stt.error   = null;
      _sttChartRendered = false;
      try {
        const [data, incData] = await Promise.allSettled([
          apiGet("/stt"),
          apiGet("/incidents?hours=168"),
        ]);
        if (data.status === "fulfilled")   stt.scores   = data.value.scores;
        else throw new Error(data.reason?.message || "Erreur STT");
        if (incData.status === "fulfilled") stt.incCount = incData.value.count ?? null;
      } catch (err) {
        stt.error = `Impossible de charger les scores STT : ${err.message}`;
      } finally {
        stt.loading = false;
        nextTick(() => renderSttChart());
      }
    }

    function triggerPhrase(dept) {
      if (dept.level === 0) return null;
      const levelStr = dept.level === 2 ? "alerte" : "précaution";
      const reasons  = [];
      if (dept.z_cameo    > 1.5)  reasons.push("une forte activité d'événements conflictuels");
      if (dept.z_tone     < -1.5 || dept.tone_cur < -3) reasons.push("un ton médiatique très négatif");
      if (dept.z_volume   > 1.5)  reasons.push("un volume d'événements supérieur à la normale");
      if (dept.neg_ratio_cur > 0.5) reasons.push("une part élevée de signaux sensibles");
      if (reasons.length === 0)   return `Cette zone est classée en ${levelStr} selon le score TERROIR.`;
      if (reasons.length === 1)   return `Cette zone est classée en ${levelStr} car ${reasons[0]}.`;
      return `Cette zone est classée en ${levelStr} car ${reasons.slice(0, -1).join(", ")} et ${reasons[reasons.length - 1]}.`;
    }

    function recommendedAction(level) {
      if (level === 2) return "Contacter les relais terrain, limiter les déplacements non essentiels et informer le coordinateur sécurité.";
      if (level === 1) return "Vérifier avec un relais local, surveiller l'évolution 24h et préparer une note de situation.";
      return "Continuer la veille habituelle. Aucun déplacement à modifier.";
    }

    function renderSttChart() {
      if (!stt.scores.length) return;
      const el = document.getElementById("stt-chart");
      if (!el) return;
      const names  = stt.scores.map((d) => d.departement);
      const scores = stt.scores.map((d) => d.stt);
      const colors = stt.scores.map((d) => ({ 0: "#198754", 1: "#ffc107", 2: "#dc3545" }[d.level] || "#6c757d"));
      const n = names.length;
      Plotly.react(
        "stt-chart",
        [{ x: names, y: scores, type: "bar", marker: { color: colors },
           hovertemplate: "%{x}<br>Score TERROIR : %{y:.2f}<extra></extra>" }],
        {
          margin: { t: 10, r: 10, b: 90, l: 44 },
          paper_bgcolor: "transparent", plot_bgcolor: "transparent",
          xaxis: { showgrid: false, tickangle: -40, tickfont: { size: 10 } },
          yaxis: { gridcolor: "#e5e7eb", tickfont: { size: 11 }, rangemode: "tozero" },
          font:  { family: "Segoe UI, system-ui, sans-serif", size: 11 },
          shapes: [
            { type: "line", x0: -0.5, x1: n - 0.5, y0: 2.0, y1: 2.0, line: { color: "#ffc107", width: 1.5, dash: "dash" } },
            { type: "line", x0: -0.5, x1: n - 0.5, y0: 3.0, y1: 3.0, line: { color: "#dc3545", width: 1.5, dash: "dash" } },
          ],
          annotations: [
            { x: n - 1, y: 2.05, text: "Précaution", showarrow: false, font: { size: 9, color: "#c89600" }, xanchor: "right", yanchor: "bottom" },
            { x: n - 1, y: 3.05, text: "Alerte",    showarrow: false, font: { size: 9, color: "#dc3545" }, xanchor: "right", yanchor: "bottom" },
          ],
        },
        { responsive: true, displayModeBar: false }
      );
      _sttChartRendered = true;
    }

    const sttTopAlert = computed(() =>
      stt.scores.length
        ? [...stt.scores].sort((a, b) => b.stt - a.stt)[0]
        : null
    );

    function sttAlertCount(level) {
      return stt.scores.filter((s) => s.level === level).length;
    }

    function levelBadgeClass(level) {
      return { 0: "bg-success", 1: "bg-warning text-dark", 2: "bg-danger" }[level] ?? "bg-secondary";
    }
    function levelColorClass(level) {
      return { 0: "success", 1: "warning", 2: "danger" }[level] ?? "secondary";
    }
    function levelProgressClass(level) {
      return { 0: "bg-success", 1: "bg-warning", 2: "bg-danger" }[level] ?? "bg-secondary";
    }
    function sttBarWidth(val) {
      return Math.max(2, Math.min(100, ((val + 5) / 15) * 100));
    }

    // ── ANALYSE 2025 ──────────────────────────────────────────────────────
    const stats    = reactive({ loading: false, data: {}, error: null });
    const timeline = reactive({ loading: false, data: [] });

    async function loadStats() {
      stats.loading = true;
      stats.error   = null;
      try {
        stats.data = await apiGet("/stats");
      } catch (err) {
        stats.error = `Impossible de charger les statistiques : ${err.message}`;
      } finally {
        stats.loading = false;
      }
    }

    async function loadTimeline() {
      timeline.loading = true;
      try {
        const res = await apiGet("/events/timeline");
        timeline.data    = res.timeline;
        timeline.loading = false;
        nextTick(() => renderTimelineChart());
      } catch (err) {
        console.error("Timeline error:", err);
        timeline.loading = false;
      }
    }

    function renderTimelineChart() {
      if (_timelineRendered) return;
      if (!timeline.data.length) return;
      const el = document.getElementById("timeline-chart");
      if (!el) return;

      const dates    = timeline.data.map((d) => d.date);
      const totals   = timeline.data.map((d) => d.total);
      const security = timeline.data.map((d) => d.security);

      Plotly.newPlot(
        "timeline-chart",
        [
          { x: dates, y: totals,   type: "bar", name: "Total",        marker: { color: "#2980b9", opacity: 0.55 } },
          { x: dates, y: security, type: "bar", name: "Sécuritaires", marker: { color: "#e74c3c", opacity: 0.85 } },
        ],
        {
          barmode: "overlay",
          margin: { t: 8, r: 8, b: 40, l: 44 },
          paper_bgcolor: "transparent",
          plot_bgcolor:  "transparent",
          legend: { orientation: "h", y: 1.12, font: { size: 11 } },
          xaxis:  { showgrid: false, tickangle: -30, tickfont: { size: 10 } },
          yaxis:  { gridcolor: "#e5e7eb", tickfont: { size: 11 } },
          font:   { family: "Segoe UI, system-ui, sans-serif", size: 11 },
        },
        { responsive: true, displayModeBar: false }
      );
      _timelineRendered = true;
    }

    function formatDateRange(range) {
      if (!range || !range.min) return "";
      const fmt = (d) => String(d).replace(/^(\d{4})(\d{2})(\d{2})$/, "$1-$2-$3");
      return `${fmt(range.min)} → ${fmt(range.max)}`;
    }

    // ── SIGNALEMENT ───────────────────────────────────────────────────────
    const report = reactive({
      success: false, submitting: false,
      geoLoading: false, geoError: null, geoSuccess: false,
      lastId: null, serverError: null, selectedDept: "",
      recentList: [], recentListError: null,
      errors: { type: false, description: false, lat: false, lon: false },
      form:   { type: "", description: "", lat: null, lon: null, pseudo: "", contact: "", source: "citoyen" },
    });

    const departments = DEPARTMENTS;

    function fillCoordsFromDept() {
      const dept = DEPARTMENTS.find((d) => d.code === report.selectedDept);
      if (dept) { report.form.lat = dept.lat; report.form.lon = dept.lon; }
    }

    function fillDeptFromCoords(lat, lon) {
      let best = null, bestDist = Infinity;
      for (const d of DEPARTMENTS) {
        const dist = Math.hypot(d.lat - lat, d.lon - lon);
        if (dist < bestDist) { bestDist = dist; best = d; }
      }
      if (best) report.selectedDept = best.code;
    }

    function geolocate() {
      if (!navigator.geolocation) {
        report.geoError = "La géolocalisation n'est pas supportée par ce navigateur.";
        return;
      }
      report.geoLoading = true;
      report.geoError   = null;
      report.geoSuccess = false;
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = parseFloat(pos.coords.latitude.toFixed(5));
          const lon = parseFloat(pos.coords.longitude.toFixed(5));
          if (lat < 6.0 || lat > 12.5 || lon < 0.7 || lon > 3.9) {
            report.geoError   = "Position hors du territoire du Bénin. Veuillez saisir les coordonnées manuellement.";
            report.geoLoading = false;
            return;
          }
          report.form.lat   = lat;
          report.form.lon   = lon;
          report.geoSuccess = true;
          report.geoLoading = false;
          fillDeptFromCoords(lat, lon);
        },
        (err) => {
          const msgs = {
            1: "Accès à la localisation refusé. Veuillez autoriser la géolocalisation dans votre navigateur.",
            2: "Position indisponible. Vérifiez que le GPS est activé.",
            3: "Délai d'attente dépassé. Réessayez ou saisissez les coordonnées manuellement.",
          };
          report.geoError   = msgs[err.code] || "Erreur de géolocalisation.";
          report.geoLoading = false;
        },
        { timeout: 10000, maximumAge: 60000 }
      );
    }

    async function loadRecentIncidents() {
      report.recentListError = null;
      try {
        const data = await apiGet("/incidents?hours=72");
        report.recentList = (data.incidents || []).slice(0, 5);
      } catch (err) {
        report.recentListError = "Impossible de charger les signalements récents.";
      }
    }

    // Heure de Cotonou (WAT = UTC+1, sans heure d'été)
    const WAT_TZ = "Africa/Porto-Novo";

    function formatTs(ts) {
      if (!ts) return "";
      try {
        return new Date(ts).toLocaleString("fr-FR", {
          timeZone: WAT_TZ,
          day: "2-digit", month: "2-digit", year: "numeric",
          hour: "2-digit", minute: "2-digit",
        });
      } catch (_) { return ts; }
    }

    function validateReport() {
      const f = report.form;
      const descLen = f.description.trim().length;
      report.errors.type        = !f.type;
      report.errors.description = descLen < 10 || descLen > 500;
      report.errors.lat         = f.lat == null || f.lat < 6.0  || f.lat > 12.5;
      report.errors.lon         = f.lon == null || f.lon < 0.7  || f.lon > 3.9;
      return !Object.values(report.errors).some(Boolean);
    }

    async function submitReport() {
      report.serverError = null;
      if (!validateReport()) return;
      report.submitting = true;
      try {
        const res = await apiPost("/incidents", {
          type: report.form.type, description: report.form.description.trim(),
          lat: report.form.lat, lon: report.form.lon,
          pseudo: report.form.pseudo || "anonyme",
          contact: report.form.contact || undefined,
          source: report.form.source,
        });
        report.lastId  = res.incident_id;
        report.success = true;
        showToast("Signalement enregistré avec succès.", "success");
        loadRecentIncidents();
        // Met à jour la carte en temps réel (incidents + GDELT)
        loadLiveMap();
      } catch (err) {
        report.serverError = `Erreur lors de l'envoi : ${err.message}`;
      } finally {
        report.submitting = false;
      }
    }

    function resetReport() {
      Object.assign(report, {
        success: false, lastId: null, serverError: null, selectedDept: "",
        geoLoading: false, geoError: null, geoSuccess: false,
        errors: { type: false, description: false, lat: false, lon: false },
        form:   { type: "", description: "", lat: null, lon: null, pseudo: "", contact: "", source: "citoyen" },
        submitting: false,
      });
    }

    // ── Watch routage ─────────────────────────────────────────────────────
    watch(currentRoute, (route) => {
      if (route === "#/live") {
        nextTick(() => {
          TerroirMap.init(updateMapStatus);
          // Toujours recharger les incidents quand on revient sur la carte
          loadLiveMap();
          loadGdeltStatus();
          if (_gdeltStatusInterval) clearInterval(_gdeltStatusInterval);
          _gdeltStatusInterval = setInterval(loadGdeltStatus, 120000);
          // Auto-refresh incidents toutes les 60 s pour tous les utilisateurs
          if (_mapRefreshInterval) clearInterval(_mapRefreshInterval);
          _mapRefreshInterval = setInterval(loadLiveMap, 60000);
        });
      } else {
        if (_gdeltStatusInterval) { clearInterval(_gdeltStatusInterval); _gdeltStatusInterval = null; }
        if (_mapRefreshInterval)  { clearInterval(_mapRefreshInterval);  _mapRefreshInterval  = null; }
      }
      if (route === "#/terroir") {
        if (!stt.scores.length) loadStt();
        else nextTick(() => { if (!_sttChartRendered) renderSttChart(); });
      }
      if (route === "#/analysis") {
        if (!stats.data.total_events) loadStats();
        if (!timeline.data.length)   loadTimeline();
      }
      if (route === "#/report") loadRecentIncidents();
    }, { immediate: true });

    // ─────────────────────────────────────────────────────────────────────
    return {
      currentRoute, toastMessage,
      // Map
      mapFilter, mapLimit, mapHours, mapHoursLabel, mapStatus,
      excludeNigeria, toggleNigeria,
      setMapFilter, setMapHours, loadLiveMap, refreshLiveMap,
      // GDELT
      gdelt, loadGdeltStatus, refreshGdelt, gdeltStatusClass, gdeltCoordLabel,
      // STT
      stt, sttTopAlert, sttAlertCount, loadStt,
      levelBadgeClass, levelColorClass, levelProgressClass, sttBarWidth,
      triggerPhrase, recommendedAction,
      // Stats
      stats, timeline, formatDateRange,
      // Report
      report, departments,
      fillCoordsFromDept, geolocate, loadRecentIncidents, formatTs,
      submitReport, resetReport,
    };
  },
}).mount("#app");
