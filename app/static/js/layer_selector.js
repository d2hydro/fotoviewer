    document.addEventListener('DOMContentLoaded', function() {
      let switchImage = document.getElementById('switchImage');
      let switchText = document.getElementById('switchText');
      switchImage.addEventListener('click', function() {
        if (switchImage.getAttribute('src') === 'static/images/brt_water.png') {
          switchImage.setAttribute('src', 'static/images/lufo.png');
          map.getLayers().setAt(0, brtWaterLayer);
          switchText.textContent = "Luchtfoto";
        } else {
          switchImage.setAttribute('src', 'static/images/brt_water.png');
          map.getLayers().setAt(0, lufoLayer);
          switchText.textContent = "Map";
        }
      });
    });