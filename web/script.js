const scanButton = document.getElementById("scanButton");
const progressCircle = document.querySelector(".progress-circle");
const progressFile = document.querySelector(".progress_file span")
const scan = document.getElementById("progressValue")

let total = 0;
let current = 0;
let progress = 0;
let intervalId;

function startScan() {
  // Reset progress and animation
  scan.textContent = "Scanning"
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
  }, 1);
}

scanButton.addEventListener("click", startScan);

eel.expose(current_file)
function current_file(file_name){
  current += 1;
  file = file_name;
  progressFile.textContent = file_name;
  console.log(file_name);
}

eel.expose(total_files)
function total_files(num_of_files){
  total = num_of_files;
  console.log(total);
}