const scanButton = document.getElementById("scanButton");
const progressCircle = document.querySelector(".progress-circle");
const progressFile = document.querySelector(".progress_file")
// const progressFile = document.querySelector(".progress_file span")
const scan = document.getElementById("progressValue")
const raw = document.getElementById("raw")

let total = 0;
let current = 0;
let progress = 0;
let intervalId;

function startScan() {
  // Reset progress and animation
  scan.textContent = "Scanning"
  raw.textContent = "Starting Scan..."

  

  eel.start_scan("quick")
  progress = 0;
  // current = 0;
  progressCircle.style.background = "conic-gradient(red 0deg, #333 0deg)";

  // Start the progress
  intervalId = setInterval(() => {
    progress = (current / total) * 100; // Increase progress
    progressCircle.style.background = `conic-gradient(red ${progress}deg, #333 ${progress}deg)`;

    
    if (progress >= 360) {
      clearInterval(intervalId);
      // alert("Scan Complete!");
      console.log("Scan complete");
    }
  }, 0.05);
}

function limitString(str, noOfChars) {
  if (str.length <= noOfChars) return str

  return `${str.split('').slice(0,noOfChars).join('')}...`
}

scanButton.addEventListener("click", startScan);

eel.expose(remove_raw)
function remove_raw(){
  raw.parentElement.removeChild(raw)
  progressFile.insertAdjacentHTML('beforeend','<span id="content"></span>')
}

eel.expose(current_file)
function current_file(file_name){
  current += 1;
  file = file_name;
  const content = document.getElementById("content")
  content.textContent = limitString(file_name,35);
  console.log(file_name);
}

eel.expose(total_files)
function total_files(num_of_files){
  total = num_of_files;
  console.log(total);
}