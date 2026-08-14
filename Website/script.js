const panSlider = document.getElementById("panSlider");
const panAngle = document.getElementById("panAngle");
const panDisplay=document.getElementById("panDisplay");

const tiltSlider = document.getElementById("tiltSlider");
const tiltAngle = document.getElementById("tiltAngle");
const tiltDisplay= document.getElementById("tiltDisplay");

const homeButton = document.getElementById("homeButton");


// Pan Slider Logic
panSlider.addEventListener("input", function() {

    const angle = panSlider.value;
    panAngle.value = angle;
    panDisplay.textContent = angle;

});

// Pan Number Logic
panAngle.addEventListener("input", function(){

    const angle = panAngle.value;
    panSlider.value = angle;
    panDisplay.textContent = angle;
});

// Tilt Slider Logic
tiltSlider.addEventListener("input", function(){
    
    angle = tiltSlider.value;
    tiltAngle.value = angle;
    tiltDisplay.textContent = angle;

});

// Tilt Number Logic
tiltAngle.addEventListener("input", function(){
    
    angle = tiltAngle.value;
    tiltSlider.value = angle;
    tiltDisplay.textContent = angle;

});

//Home Button Logic
homeButton.addEventListener("click", function(){

    panAngle.value = 90;
    panSlider.value = 90;
    panDisplay.textContent = 90;

    tiltAngle.value = 90;
    tiltSlider.value = 90;
    tiltDisplay.textContent = 90;
});
