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

                // Guard against duplicate listener attachment
                if (graphDiv.dataset.pinchDisabled === 'true') {
                    return;
                }

                const preventPinch = function (event) {
                    if (event.touches && event.touches.length > 1) {
                        event.preventDefault();
                    }
                };

                graphDiv.addEventListener('touchstart', preventPinch, { passive: false });
                graphDiv.addEventListener('touchmove', preventPinch, { passive: false });
                graphDiv.dataset.pinchDisabled = 'true';
            });

            return window.dash_clientside.no_update;
        }
    }
});
