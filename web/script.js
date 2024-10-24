const scanButton = document.getElementById("scanButton");
const progressCircle = document.querySelector(".progress-circle");
const progressFile = document.querySelector(".progress_file");
// const progressFile = document.querySelector(".progress_file span")
const scan = document.getElementById("progressValue");
const raw = document.getElementById("raw");
const actionList = document.querySelector(".action-list");

let total = 0;
let current = 0;
let progress = 0;
let isScanning = false;
let intervalId;

function startScan() {
  // Reset progress and animation
  type = scan.textContent.split(' ')[0].toLowerCase()
  scan.textContent = "Scanning";
  raw.textContent = "Starting Scan...";
  isScanning = true;

  eel.start_scan(type);
  
  progress = 0;
  // current = 0;
  progressCircle.style.background = "conic-gradient(red 0deg, #333 0deg)";

  // Start the progress
  intervalId = setInterval(() => {
    progress = (current / total) * 100; // Increase progress
    progressCircle.style.background = `conic-gradient(red ${progress}deg, #333 ${progress}deg)`;

    if (progress >= 360) {
      isScanning = false;
      clearInterval(intervalId);
      // alert("Scan Complete!");
      console.log("Scan complete");
    }
  }, 0.05);
}

scanButton.addEventListener("click", startScan);


actionList.addEventListener("click", function (event) {
  if (isScanning) return
  const value = event.target.textContent;
  if (event.target.textContent.includes("\n")) return;
  scan.textContent = value
});

eel.expose(remove_raw);
function remove_raw() {
  raw.parentElement.removeChild(raw);
  progressFile.insertAdjacentHTML("beforeend", '<span id="content"></span>');
}

eel.expose(current_file);
function current_file(file_name) {
  current += 1;
  file = file_name;
  const content = document.getElementById("content");
  content.textContent = limitString(file_name, 35);
  console.log(file_name);
}

eel.expose(total_files);
function total_files(num_of_files) {
  // total = num_of_files;
  total = 100;
  console.log(total);
}

function limitString(str, noOfChars) {
  if (str.length <= noOfChars) return str;

  return `${str.split("").slice(0, noOfChars).join("")}...`;
}
