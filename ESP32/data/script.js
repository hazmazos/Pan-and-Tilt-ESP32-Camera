const panSlider = document.getElementById("panSlider");
const panDisplay=document.getElementById("panDisplay");

const tiltSlider = document.getElementById("tiltSlider");
const tiltDisplay= document.getElementById("tiltDisplay");

const mapInput = document.getElementById("gridXY");

const marker = document.getElementById("marker");

const homeButton = document.getElementById("homeButton");

const scaleFactor = 180/294;


// Pan Slider Logic
panSlider.addEventListener("input", function() {

    const angle = panSlider.value;
    panDisplay.textContent = angle;
    setMarker(angle,null);

});


// Tilt Slider Logic
tiltSlider.addEventListener("input", function(){
    
    angle = tiltSlider.value;
    tiltDisplay.textContent = angle;
    setMarker(null,angle);

});

mapInput.addEventListener("click", function(event){

    const rect = mapInput.getBoundingClientRect();

    xCoords = event.clientX - rect.left;
    yCoords = event.clientY - rect.top;

    marker.style.left = xCoords + "px";
    marker.style.top = yCoords + "px";

    xScaled = Math.round(xCoords * scaleFactor);
    yScaled = Math.round(yCoords * scaleFactor);

    updateAngle(panSlider,panDisplay,xScaled);
    updateAngle(tiltSlider,tiltDisplay,yScaled);

    

});

//Home Button Logic
homeButton.addEventListener("click", function(){

    updateAngle(panSlider,panDisplay,90);
    updateAngle(tiltSlider,tiltDisplay,90);
    setMarker(90,90);
});

function updateAngle(slider,display,value){

    slider.value = value;
    display.textContent = value;

};

function setMarker(panAngle,tiltAngle){

    if (panAngle !== null) {
        marker.style.left = Math.round(panAngle / scaleFactor) + "px";
    }

    if (tiltAngle !== null) {
        marker.style.top = Math.round(tiltAngle / scaleFactor) + "px";
    }

};