window.dash_clientside = Object.assign({}, window.dash_clientside, {
  deviceUtils: {
    detectMobile: function(fig) {
      if (typeof window === 'undefined') {
        return { isMobile: false };
      }
      const pointerCoarse = window.matchMedia('(pointer: coarse)').matches;
      const smallWidth = window.innerWidth <= 820;
      return { isMobile: pointerCoarse || smallWidth };
    }
  }
});
