// const scanButton = document.getElementById("scanButton");
// const progressCircle = document.querySelector(".progress-circle");
// const progressFile = document.querySelector(".progress_file");
// const scan = document.getElementById("progressValue");
// const raw = document.getElementById("raw");
// const actionList = document.querySelector(".action-list");

const currentFile = document.querySelector(".current-file-container .current-file")
const spinner = document.querySelectorAll(".spinner")
const cancle = document.querySelector(".center button")

// console.log(cancle)

let total = 0;
let current = 0;
let degreePerFile = 0;
let progress = 0;
let isScanning = false;
let intervalId;

function startScan(type) {
  // Reset progress and animation
  // type = scan.textContent.split(' ')[0].toLowerCase()
  // scan.textContent = "Scanning";
  currentFile.textContent = "Starting Scan...";
  isScanning = true;

  eel.start_scan(type);
  
  progress = 0;
  // progressCircle.style.background = "conic-gradient(red 0deg, #333 0deg)";

  // Start the progress
  intervalId = setInterval(() => {
    progress += degreePerFile; // Increase progress
    // console.log(progress)
    spinner[0].style.background = `conic-gradient(var(--blue) ${progress}deg, var(--black) ${progress}deg)`;
    spinner[1].style.background = `conic-gradient(var(--red) ${progress}deg, var(--black) ${progress}deg)`;
    spinner[2].style.background = `conic-gradient(var(--purple) ${progress}deg, var(--black) ${progress}deg)`;

    if (progress >= 360) {
      isScanning = false;
      console.log("Scan complete");
      clearInterval(intervalId);
    }
  }, 1);
}


cancle.addEventListener("click", function(event){eel.cancel_scanning()})
eel.expose(logging)
function logging(logs){
  console.log(logs)
}

// get total number of files from the python file
eel.expose(total_files);
function total_files(num_of_files) {
  total = num_of_files;
  // total = 100;
  degreePerFile = 360 / total
  console.log(total,degreePerFile);
}

// show the current scanning file on the front-end
eel.expose(current_file);
function current_file(file_name) {
  current += 1;
  file = file_name;
  currentFile.textContent = limitString(file_name, 40);
  // console.log(currentFile)
  // console.log(file_name);
}

// limiting the length the file path showing on the front-end
function limitString(str, noOfChars) {
  if (str.length <= noOfChars) return str;

  return `${str.split("").slice(0, noOfChars).join("")}...`;
}
