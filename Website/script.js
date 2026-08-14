const panSlider = document.getElementById("panSlider");
const panDisplay=document.getElementById("panDisplay");

const tiltSlider = document.getElementById("tiltSlider");
const tiltDisplay= document.getElementById("tiltDisplay");

const homeButton = document.getElementById("homeButton");


// Pan Slider Logic
panSlider.addEventListener("input", function() {

    const angle = panSlider.value;
    panDisplay.textContent = angle;

});


// Tilt Slider Logic
tiltSlider.addEventListener("input", function(){
    
    angle = tiltSlider.value;
    tiltDisplay.textContent = angle;

});


//Home Button Logic
homeButton.addEventListener("click", function(){

    panSlider.value = 90;
    panDisplay.textContent = 90;


    tiltSlider.value = 90;
    tiltDisplay.textContent = 90;
});
