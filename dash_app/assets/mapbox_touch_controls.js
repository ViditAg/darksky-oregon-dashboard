window.dash_clientside = Object.assign({}, window.dash_clientside, {
    mapboxControls: {
        disableInteractions: function(fig) {
            if (!fig) {
                return window.dash_clientside.no_update;
            }

            window.requestAnimationFrame(function() {
                const graphDiv = document.getElementById('oregon-map');
                if (!graphDiv) {
                    return;
                }

                if (graphDiv.dataset.zoomGuardAttached === 'true') {
                    return;
                }

                const initialZoom = (fig && fig.layout && fig.layout.map && fig.layout.map.zoom) ?? 5;
                graphDiv.dataset.lastAllowedZoom = initialZoom;

                graphDiv.on('plotly_relayout', function (eventData) {
                    if (!eventData || !Object.prototype.hasOwnProperty.call(eventData, 'map.zoom')) {
                        return;
                    }

                    const lastZoom = parseFloat(graphDiv.dataset.lastAllowedZoom ?? initialZoom);
                    const requestedZoom = eventData['map.zoom'];

                    // If relayout triggered by our own reset, ignore to avoid loops
                    if (graphDiv.dataset.restoringZoom === 'true') {
                        graphDiv.dataset.restoringZoom = 'false';
                        return;
                    }

                    // Revert any user zoom change (pinch, double-tap, etc.)
                    if (requestedZoom !== lastZoom) {
                        graphDiv.dataset.restoringZoom = 'true';
                        window.Plotly.relayout(graphDiv, {'map.zoom': lastZoom});
                    }
                });

                graphDiv.dataset.zoomGuardAttached = 'true';
            });

            return window.dash_clientside.no_update;
        }
    }
});
