(function() {
  const MIN_ZOOM = 3;
  const MAX_ZOOM = 8;

  function clampZoomValue(value) {
    if (typeof value !== 'number') {
      return value;
    }
    if (value > MAX_ZOOM) {
      return MAX_ZOOM;
    }
    if (value < MIN_ZOOM) {
      return MIN_ZOOM;
    }
    return value;
  }

  function attachClampHandler(gd) {
    if (!gd || gd.dataset.zoomClampAttached === 'true') {
      return;
    }

    gd.dataset.zoomClampAttached = 'true';

    gd.on('plotly_relayout', function(ev) {
      if (!ev || typeof ev['mapbox.zoom'] === 'undefined') {
        return;
      }

      const requestedZoom = ev['mapbox.zoom'];
      const clampedZoom = clampZoomValue(requestedZoom);

      if (clampedZoom !== requestedZoom) {
        window.Plotly.relayout(gd, { 'mapbox.zoom': clampedZoom });
      }
    });
  }

  document.addEventListener('plotly_afterplot', function(event) {
    attachClampHandler(event.target);
  });

  window.addEventListener('load', function() {
    document.querySelectorAll('.js-plotly-plot').forEach(attachClampHandler);
  });
})();
