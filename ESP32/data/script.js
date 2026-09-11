const panSlider = document.getElementById("panSlider");
const panDisplay=document.getElementById("panDisplay");

const tiltSlider = document.getElementById("tiltSlider");
const tiltDisplay= document.getElementById("tiltDisplay");

const mapInput = document.getElementById("gridXY");

//const marker = document.getElementById("marker");

const homeButton = document.getElementById("homeButton");


const camera = document.getElementById("camera");


let currentFrame = 0;
const testEnd = 100;

// data for testing stream

let streamFrameTimes = [];
let lastStreamFrameTime = null;

async function getStream(){
    
    const response = await fetch("/stream")

    if(!response.ok){
        console.log("Stream request did not work");
        return;
    }

    const reader = response.body.getReader();
    let buffer = new Uint8Array(0);

    // read data
    while(true){

        const {value, done} = await reader.read();

        // in case if esp32 ends the stream (crashes or something)
        if(done){

            break;
        }

        const newBuffer = new Uint8Array(buffer.length + value.length);
        newBuffer.set(buffer);
        newBuffer.set(value, buffer.length);

        buffer = newBuffer;

        // find jpeg
        while(true){

            // search bytes for bytes (has to be converted first)
            const headerStart = findBytes(buffer, new TextEncoder().encode("\r\n\r\n"));

            // havent received all the header yet
            if(headerStart == -1){
                break;
            }

            // back to text
            const header = new TextDecoder().decode(buffer.slice(0,headerStart));
            const match = header.match(/Content-Length:\s*(\d+)/i)

            // found header did not find content-length
            if(!match){

                buffer = buffer.slice(headerStart + 4);
                continue;
            }

            const jpegLength = parseInt(match[1]);
            const jpegStart = headerStart + 4;
            
            if(buffer.length < jpegStart + jpegLength){

                break;
            }

            const jpegData = buffer.slice(jpegStart, jpegStart + jpegLength);
            buffer = buffer.slice(jpegStart + jpegLength);

            const end = performance.now();

            if( lastStreamFrameTime !== null){

                const frameTime = end - lastStreamFrameTime;
                streamFrameTimes.push(frameTime);
            }

            lastStreamFrameTime = end;

            // display the stream
            const blob = new Blob([jpegData], { type: "image/jpeg"});
            const imageUrl = URL.createObjectURL(blob);
            camera.src = imageUrl;
            
            // still need the image
            setTimeout(() => {

                URL.revokeObjectURL(imageUrl);
            }, 1000);

            if(streamFrameTimes.length >= testEnd){

                reader.cancel();                
                calculateResults(streamFrameTimes);

                return;
            }

        }
    }
}


function findBytes(data , search){

    // search only where its possible to appear
    for(let i=0; i<=data.length - search.length; i++){

        let found = true;

        for( let j=0; j<search.length; j++){

            if(data[i+j] !== search[j]){

                found = false;
                break;
            }
        }

        if(found){
            
            return i;
        }
    }
    return -1;
}

function calculateResults(frameTimes){
    
    const meanFrameTime = frameTimes.reduce((total, value) => total + value, 0) / frameTimes.length;
    const frameTimesVariance = frameTimes.reduce((total, value) => total + (value - meanFrameTime)**2, 0) / frameTimes.length;
    const frameTimeStdv = Math.sqrt(frameTimesVariance);

    const fpsValues = frameTimes.map(frameTimes => 1000 / frameTimes);
    const meanFps = fpsValues.reduce((total, value) => total + value, 0) / fpsValues.length;
    const fpsVariance = fpsValues.reduce((total, value) => total + (value - meanFps)**2, 0) / fpsValues.length;
    const fpsStdv = Math.sqrt(fpsVariance);

    console.log("The mean frame time is: ", meanFrameTime);
    console.log("The frame time standard deviation is: ", frameTimeStdv);

    console.log("The mean fps: ", meanFps);
    console.log("The fps standard deviation is: ", fpsStdv);

}

// data for testing capture
let captureFrameTimes = [];

function getCapture(){

    const start = performance.now();
    
    fetch("/capture")
    .then(respone => respone.blob())
    .then( blob => {
        
        const imageURL = URL.createObjectURL(blob);
        camera.src = imageURL;

        const end = performance.now();

        const frameTime = end - start;

        captureFrameTimes.push(frameTime);

        currentFrame++;

        if(currentFrame < testEnd){

            getCapture();
        }

        else{
            
            calculateResults(captureFrameTimes);            
        }
    })

};

//getCapture();
//getStream();


//Pan Slider Logic
panSlider.addEventListener("input", function(){

    const angle = panSlider.value;
    panDisplay.textContent = angle;
    //setMarker(angle,null);

    fetch("/pan?angle="+angle);

});

// Tilt Slider Logic
tiltSlider.addEventListener("input", function(){
    
    const angle = tiltSlider.value;
    tiltDisplay.textContent = angle;
    //setMarker(null,angle);

    fetch("/tilt?angle="+angle);

});

//Click to move servo and target
mapInput.addEventListener("click", function(event){

    const rect = mapInput.getBoundingClientRect();

    const xCoords = event.clientX - rect.left;
    const yCoords = event.clientY - rect.top;

    //marker.style.left = xCoords + "px";
    //marker.style.top = yCoords + "px";

    const panAngle = Math.round(xCoords * 180 / rect.width);
    const tiltAngle = Math.round(yCoords * 180 / rect.height);

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


/*
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
*/
