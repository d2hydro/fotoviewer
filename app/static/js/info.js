// Function to toggle the visibility of the div and fetch content from "/info"
async function openInfo(feature) {
    var infoContainer = document.getElementById("info-container");
    var infoDiv = document.getElementById("info");

    // make info visible
    infoContainer.style.display = 'block';

    // set layer-selector position
    var currentWidth = infoContainer.offsetWidth;
    var layerSelector = document.getElementById("layer-selector");
    layerSelector.style.left = (currentWidth + 20) + 'px';

    var fotoUrl = './static/data/' + feature.get('file_name');
    var dateTime = new Date(feature.get('date_time')).toLocaleString()
    var subject = feature.get('subject')
    var body = feature.get('body')

    if (infoContainer.style.display === 'block') {
        infoDiv.innerHTML = `
            <h3>${subject}</h3>
            <img src="${fotoUrl}" alt="Image" style="width: 100%; height: auto;">
            <hr>
            <strong>Tijdstip foto:</strong> ${dateTime}
            <hr>
            <strong>Beschrijving:</strong><br>
            ${body}
            <hr>
        `;
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