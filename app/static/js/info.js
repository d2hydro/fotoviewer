// Function to toggle the visibility of the div and fetch content from "/info"
async function openInfo(foto_url) {
    var infoContainer = document.getElementById("info-container");
    var infoDiv = document.getElementById("info");

    // make info visible
    infoContainer.style.display = 'block';

    // set layer-selector position
    var currentWidth = infoContainer.offsetWidth;
    var layerSelector = document.getElementById("layer-selector");
    layerSelector.style.left = (currentWidth + 20) + 'px';

    if (infoContainer.style.display === 'block') {
        infoDiv.innerHTML = `<img src="${foto_url}" alt="Image" style="width: 100%; height: 100%;">` ;
    }
}


// Function to close the div
function closeInfo() {
    var infoContainer = document.getElementById("info-container");
    var infoDiv = document.getElementById("info");

    // make info invisible
    infoDiv.innerHTML = "";
    infoContainer.style.display = 'none';

    // set layer-selector position
    var currentWidth = infoContainer.offsetWidth;
    var layerSelector = document.getElementById("layer-selector");
    layerSelector.style.left = '20px';
}