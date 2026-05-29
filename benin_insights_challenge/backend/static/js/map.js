// backend/static/js/map.js — TERROIR BeninScope
// Module Leaflet isolé du reste de l'app Vue.
// Exposé globalement via window.TerroirMap.

"use strict";

window.TerroirMap = (() => {

  // ── État privé ─────────────────────────────────────────────────────────
  let _map       = null;
  let _gdelt     = null;
  let _incidents = null;
  let _onStatus  = null;

  // ── Helpers date ───────────────────────────────────────────────────────

  function parseGdeltDate(d) {
    const s = String(d || "").replace(/-/g, "").slice(0, 8);
    if (s.length < 8) return null;
    try {
      return new Date(`${s.slice(0,4)}-${s.slice(4,6)}-${s.slice(6,8)}T12:00:00Z`);
    } catch (_) { return null; }
  }

  function fmtDate(d) {
    if (!d) return "N/A";
    return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit", year: "numeric" });
  }

  // ── Helpers couleur / taille ───────────────────────────────────────────

  function getMarkerColor(ev) {
    if (ev.is_security) {
      const g = ev.goldstein ?? 0;
      const t = ev.tone      ?? 0;
      if (g <= -7 || t <= -8) return "#6d0000";
      if (g <= -5 || t <= -6) return "#c0392b";
      return "#e74c3c";
    }
    const t = ev.tone ?? 0;
    if (t < -3) return "#e67e22";
    if (t < -1) return "#f1c40f";
    return "#2980b9";
  }

  function isCritical(color) {
    return color === "#6d0000" || color === "#c0392b";
  }

  function getMarkerRadius(ev) {
    const base  = ev.is_security ? 7 : 5;
    const bonus = Math.min(5, Math.floor((ev.mentions ?? 0) / 8));
    return base + bonus;
  }

  // ── Popup helpers ──────────────────────────────────────────────────────

  function fmtVal(v, d = 1) {
    return (v !== undefined && v !== null) ? Number(v).toFixed(d) : "N/A";
  }

  function srcDomain(url) {
    if (!url) return "Non disponible";
    try { return new URL(url).hostname.replace(/^www\./, ""); }
    catch (_) { return (url + "").slice(0, 40); }
  }

  function newBadgeHtml() {
    return `<span class="pp-badge-new ms-1">Nouveau</span>`;
  }

  const COORD_SOURCE_INFO = {
    action_geo:       { label: "Position exacte du lieu",        cls: "pp-coord-exact",   note: null },
    actor1_geo:       { label: "Acteur principal béninois",       cls: "pp-coord-actor",   note: null },
    actor2_geo:       { label: "Acteur secondaire béninois",      cls: "pp-coord-actor",   note: null },
    centroid_adm1:    { label: "Département estimé",              cls: "pp-coord-dept",    note: null },
    centroid_country: { label: "Pays approximatif",               cls: "pp-coord-country", note: "Ce point représente une zone générale, pas le lieu exact." },
  };

  function coordPrecisionHtml(source) {
    const info = COORD_SOURCE_INFO[source];
    if (!info) return "";
    const note = info.note
      ? `<div class="pp-coord-note">${info.note}</div>`
      : "";
    return `<span class="pp-coord-badge ${info.cls}">${info.label}</span>${note}`;
  }

  function buildGdeltPopup(ev, isNew) {
    const secBadge = ev.is_security
      ? `<span class="pp-badge-sec">Sécurité</span>`
      : `<span class="pp-badge-info">Info</span>`;
    const actorRow = ev.actor1
      ? `<tr><td class="pp-label">Acteur</td><td>${ev.actor1}${ev.actor2 ? " / " + ev.actor2 : ""}</td></tr>`
      : "";
    const coordRow = ev.coord_source
      ? `<tr><td class="pp-label">Précision</td><td>${coordPrecisionHtml(ev.coord_source)}</td></tr>`
      : "";
    const srcLine = ev.url
      ? `<div class="pp-src"><a href="${ev.url}" target="_blank" rel="noopener">Lire la source &rarr;</a></div>`
      : "";
    return `
      <div class="terroir-popup">
        <div class="pp-header pp-header-gdelt">
          ${ev.event_label || "Événement"} ${secBadge}${isNew ? newBadgeHtml() : ""}
        </div>
        <table class="pp-table">
          <tr><td class="pp-label">Zone</td>
              <td>${ev.location || ev.adm1 || "Non disponible"}</td></tr>
          <tr><td class="pp-label">Date</td>
              <td>${ev.date || "N/A"}</td></tr>
          <tr><td class="pp-label">Ton moyen</td>
              <td class="${(ev.tone ?? 0) < -3 ? "pp-danger" : ""}">${fmtVal(ev.tone)}</td></tr>
          <tr><td class="pp-label">Goldstein</td>
              <td class="${(ev.goldstein ?? 0) < -3 ? "pp-danger" : ""}">${fmtVal(ev.goldstein)}</td></tr>
          <tr><td class="pp-label">Mentions</td>
              <td>${ev.mentions ?? "N/A"}</td></tr>
          <tr><td class="pp-label">Source</td>
              <td>${srcDomain(ev.url)}</td></tr>
          ${actorRow}
          ${coordRow}
        </table>
        ${srcLine}
      </div>`;
  }

  function buildIncidentPopup(inc, isNew) {
    const statusHtml = inc.validated
      ? `<span class="pp-ok">&#10003; Vérifié</span>`
      : `<span class="pp-pending">En attente de validation</span>`;
    const desc = (inc.description || "").slice(0, 160) || "N/A";
    const ts   = inc.timestamp
      ? inc.timestamp.slice(0, 16).replace("T", " ")
      : "N/A";
    return `
      <div class="terroir-popup">
        <div class="pp-header pp-header-citizen">
          SIGNALEMENT TERRAIN${isNew ? newBadgeHtml() : ""}
        </div>
        <table class="pp-table">
          <tr><td class="pp-label">Type</td>
              <td>${inc.type || "N/A"}</td></tr>
          <tr><td class="pp-label">Département</td>
              <td>${inc.departement || inc.adm1_code || "N/A"}</td></tr>
          <tr><td class="pp-label">Description</td>
              <td>${desc}</td></tr>
          <tr><td class="pp-label">Signalé le</td>
              <td>${ts}</td></tr>
          <tr><td class="pp-label">Statut</td>
              <td>${statusHtml}</td></tr>
        </table>
      </div>`;
  }

  // ── Icône citoyen (avec anneau de pulse si nouveau) ────────────────────

  function citizenIcon(validated, isNew) {
    const bg  = validated ? "#198754" : "#fd7e14";
    const sym = validated ? "&#10003;" : "!";
    const ring = isNew
      ? `<div style="position:absolute;top:-7px;left:-7px;width:36px;height:36px;border-radius:50%;border:2px solid ${bg};animation:citizen-pulse 2s ease-in-out infinite;pointer-events:none"></div>`
      : "";
    return L.divIcon({
      html: `<div style="position:relative;width:22px;height:22px">${ring}<div style="position:absolute;top:0;left:0;width:22px;height:22px;display:flex;align-items:center;justify-content:center;background:${bg};border-radius:50%;border:2.5px solid white;box-shadow:0 1px 6px rgba(0,0,0,.35);color:white;font-weight:700;font-size:13px;line-height:1">${sym}</div></div>`,
      className:   "",
      iconSize:    [22, 22],
      iconAnchor:  [11, 11],
      popupAnchor: [0, -13],
    });
  }

  // ── Rendu markers ──────────────────────────────────────────────────────

  function renderGdeltMarkers(events) {
    _gdelt.clearLayers();
    let secCount = 0;

    // Détecter les événements "nouveaux" : dans le dernier jour de la fenêtre affichée
    const parsedDates = (events || [])
      .map(e => parseGdeltDate(e.date))
      .filter(Boolean);
    const maxTs      = parsedDates.length ? Math.max(...parsedDates.map(d => d.getTime())) : 0;
    const newCutofMs = 24 * 3600 * 1000;

    (events || []).forEach(ev => {
      if (ev.lat == null || ev.lon == null) return;
      if (ev.is_security) secCount++;

      const color    = getMarkerColor(ev);
      const radius   = getMarkerRadius(ev);
      const critical = isCritical(color);
      const evDate   = parseGdeltDate(ev.date);
      const isNew    = !!(evDate && maxTs > 0 && (maxTs - evDate.getTime()) <= newCutofMs);

      const m = L.circleMarker([ev.lat, ev.lon], {
        radius,
        color,
        weight:      critical ? 2.0 : 1.2,
        fillColor:   color,
        fillOpacity: ev.is_security ? 0.80 : 0.48,
        className:   critical ? "marker-critical-pulse" : "",
      });

      const zone   = ev.location || ev.adm1 || "Bénin";
      const newTag = isNew ? " &bull; <span style='color:#fd7e14;font-weight:700'>Nouveau</span>" : "";
      m.bindTooltip(
        `<strong>${ev.event_label || "Événement"}</strong>${newTag}<br>${zone}<br>${ev.date || ""} &bull; Ton&nbsp;: ${fmtVal(ev.tone)}`,
        { direction: "top", offset: [0, -radius - 2], className: "terroir-tooltip" }
      );
      m.bindPopup(buildGdeltPopup(ev, isNew), { maxWidth: 300 });
      _gdelt.addLayer(m);
    });

    // Infos fenêtre pour la barre de statut
    const minTs = parsedDates.length ? Math.min(...parsedDates.map(d => d.getTime())) : 0;
    const windowInfo = (minTs && maxTs)
      ? { start: fmtDate(new Date(minTs)), end: fmtDate(new Date(maxTs)) }
      : null;

    return { secCount, windowInfo };
  }

  function renderIncidentMarkers(incidents) {
    _incidents.clearLayers();
    const newCutoffMs = 24 * 3600 * 1000;

    (incidents || []).forEach(inc => {
      if (inc.lat == null || inc.lon == null) return;
      const age   = inc.timestamp
        ? (Date.now() - new Date(inc.timestamp).getTime())
        : Infinity;
      const isNew = age < newCutoffMs;

      const m = L.marker([inc.lat, inc.lon], { icon: citizenIcon(inc.validated, isNew) });
      const newTag = isNew ? " &bull; <span style='color:#fd7e14;font-weight:700'>Nouveau</span>" : "";
      m.bindTooltip(
        `<strong>Signalement</strong>&nbsp;: ${inc.type || ""}${newTag}`,
        { direction: "top", className: "terroir-tooltip" }
      );
      m.bindPopup(buildIncidentPopup(inc, isNew), { maxWidth: 300 });
      _incidents.addLayer(m);
    });
  }

  // ── API publique ───────────────────────────────────────────────────────

  function init(onStatusCallback) {
    _onStatus = onStatusCallback || null;
    if (_map) { _map.invalidateSize(); return; }

    _map = L.map("terroir-map", {
      zoomControl: true,
      attributionControl: true,
    }).setView([9.3077, 2.3158], 7);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>',
      maxZoom: 18,
    }).addTo(_map);

    // MarkerClusterGroup : regroupe les points proches en bulles numérotées.
    // Zoom ≥ 9 → points individuels avec hover normal.
    // Zoom < 9 → clusters cliquables qui zooment + spiderfient.
    _gdelt = L.markerClusterGroup({
      maxClusterRadius:        50,
      disableClusteringAtZoom: 9,
      spiderfyOnMaxZoom:       true,
      showCoverageOnHover:     false,
      zoomToBoundsOnClick:     true,
      iconCreateFunction(cluster) {
        const n   = cluster.getChildCount();
        const cls = n >= 20 ? "cluster-lg" : n >= 5 ? "cluster-md" : "cluster-sm";
        return L.divIcon({
          html:      `<div class="terroir-cluster ${cls}">${n}</div>`,
          className: "",
          iconSize:  [36, 36],
        });
      },
    }).addTo(_map);
    _incidents = L.layerGroup().addTo(_map);
  }

  async function loadLiveMap(filter, limit, hours, excludeNigeria) {
    if (!_map) return;
    if (_onStatus) _onStatus({ loading: true, error: null, incidentError: null });

    const showGdelt     = filter !== "incidents";
    const showIncidents = filter !== "security";
    const secOnly       = filter === "security";
    const hoursParam    = (hours != null) ? `&hours=${hours}` : "";
    const incHours      = (hours != null) ? Math.max(hours, 48) : 48;
    const ngParam       = excludeNigeria ? "&exclude_nigeria=true" : "";

    try {
      const gdeltReq = showGdelt
        ? apiGet(`/events/map?limit=${limit}${secOnly ? "&security_only=true" : ""}${hoursParam}${ngParam}`)
        : Promise.resolve({ events: [], count: 0, idn_pct: null });

      const incReq = showIncidents
        ? apiGet(`/incidents?hours=${incHours}`)
        : Promise.resolve({ incidents: [], count: 0 });

      const [evData, incData] = await Promise.all([gdeltReq, incReq]);

      const { secCount, windowInfo } = renderGdeltMarkers(evData.events);
      renderIncidentMarkers(incData.incidents);

      if (_onStatus) _onStatus({
        loading:       false,
        error:         null,
        incidentError: null,
        gdeltCount:    evData.count  ?? 0,
        securityCount: secCount,
        incidentCount: incData.count ?? 0,
        idnPct:        evData.idn_pct ?? null,
        windowInfo,
        lastUpdate: new Date().toLocaleTimeString("fr-FR", {
          hour: "2-digit", minute: "2-digit",
        }),
      });
    } catch (err) {
      console.error("Map error:", err);
      if (_onStatus) _onStatus({ loading: false, error: err.message });
    }
  }

  function invalidate() {
    if (_map) _map.invalidateSize();
  }

  return { init, loadLiveMap, invalidate };

})();
