const panSlider = document.getElementById("panSlider");
const panDisplay=document.getElementById("panDisplay");

const tiltSlider = document.getElementById("tiltSlider");
const tiltDisplay= document.getElementById("tiltDisplay");

const mapInput = document.getElementById("gridXY");

//const marker = document.getElementById("marker");

const homeButton = document.getElementById("homeButton");


const camera = document.getElementById("camera");

/*
function getFrame(){
    
    fetch("/capture")
    .then(respone => respone.blob())
    .then( blob => {
        
        const imageURL = URL.createObjectURL(blob);
        camera.src = imageURL;
        
        getFrame();
        
    })

};

getFrame();
*/


// Pan Slider Logic
panSlider.addEventListener("input", function(){

    const angle = panSlider.value;
    panDisplay.textContent = angle;
    //setMarker(angle,null);

    fetch("/pan?angle="+angle);

});

// Tilt Slider Logic
tiltSlider.addEventListener("input", function(){
    
    angle = tiltSlider.value;
    tiltDisplay.textContent = angle;
    //setMarker(null,angle);

    fetch("/tilt?angle="+angle);

});

//Click to move servo and target
mapInput.addEventListener("click", function(event){

    const rect = mapInput.getBoundingClientRect();

    xCoords = event.clientX - rect.left;
    yCoords = event.clientY - rect.top;

    //marker.style.left = xCoords + "px";
    //marker.style.top = yCoords + "px";

    panAngle = Math.round(xCoords * 180 / rect.width);
    tiltAngle = Math.round(yCoords * 180 / rect.height);

    updateAngle(panSlider,panDisplay,panAngle);
    updateAngle(tiltSlider,tiltDisplay,tiltAngle);

    fetch("/pan?angle="+panAngle);
    fetch("/tilt?angle="+tiltAngle);

    

});

//Home Button Logic
homeButton.addEventListener("click", function(){

    updateAngle(panSlider,panDisplay,90);
    updateAngle(tiltSlider,tiltDisplay,90);
    //setMarker(90,90);

    fetch("/pan?angle=90");
    fetch("/tilt?angle=90");
});

function updateAngle(slider,display,value){

    slider.value = value;
    display.textContent = value;

};

// Get slider angle to target x,y
function setMarker(panAngle,tiltAngle){

    const rect = mapInput.getBoundingClientRect();

    if (panAngle !== null) {
        marker.style.left = Math.round(panAngle * rect.width / 180 ) + "px";
    }

    if (tiltAngle !== null) {
        marker.style.top = Math.round(tiltAngle * rect.height / 180 ) + "px";
    }

};

