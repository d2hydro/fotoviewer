  // perform search on button-click or enter
  document.getElementById('search-input').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    searchAndCenterMap();
  }
});

document.getElementById('search-button').addEventListener('click', searchAndCenterMap);

function searchAndCenterMap() {
    const searchTerm = document.getElementById('search-input').value;
    fetch(`./search?search_term=${encodeURIComponent(searchTerm)}&output_format=geojson`).then(response => response.json()).then(data => {
      geoJsonObj = data; // Update geoJsonObj with the new data
      console.log(geoJsonObj)
      extent = geoJsonObj.bbox
      console.log(extent)
      searchSource.clear(); // Clear the existing features
      const newFeatures = new ol.format.GeoJSON().readFeatures(geoJsonObj, {
        featureProjection: 'EPSG:28992'
      });
      searchSource.addFeatures(newFeatures); // Add the new features
      const centroid = [
        (extent[0] + extent[2]) / 2,
        (extent[1] + extent[3]) / 2,
      ];
      map.getView().animate({ center: centroid, duration: 1000 });
    }).catch(error => console.error('Error fetching the GeoJSON data:', error));
  };

  // perform search on input
  let searchResults = [];

const inputElement = document.getElementById('search-input');
const resultsContainer = document.getElementById('search-results');
inputElement.addEventListener('input', async () => {
  const searchTerm = inputElement.value;
  if (searchTerm === '') {
    resultsContainer.style.display = 'none';
    return;
  }
  try {
    const response = await fetch(`http://127.0.0.1:3000/search?search_term=${encodeURIComponent(searchTerm)}`);
    searchResults = await response.json();
    //console.log(searchResults)
    resultsContainer.innerHTML = '';
    searchResults.forEach((result, index) => {
      console.log(result.naam)
      const resultDiv = document.createElement('div');
      resultDiv.textContent = result.naam;
      resultDiv.addEventListener('click', () => {
        inputElement.value = result.naam;
        resultsContainer.style.display = 'none';
        console.log('Selected global ID:', result.globalid);
      });
      resultsContainer.appendChild(resultDiv);
    });
    resultsContainer.style.display = 'block';
  } catch (error) {
    console.error('Error fetching search results:', error);
  }
});