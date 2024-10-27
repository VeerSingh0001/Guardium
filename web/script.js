// const scanButton = document.getElementById("scanButton");
// const progressCircle = document.querySelector(".progress-circle");
// const progressFile = document.querySelector(".progress_file");
// const scan = document.getElementById("progressValue");
// const raw = document.getElementById("raw");
// const actionList = document.querySelector(".action-list");

const currentFile = document.querySelector(".current-file-container .current-file")
const spinner = document.querySelectorAll(".spinner")

console.log(spinner)

let total = 0;
let current = 0;
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
    progress = (current / total) * 100; // Increase progress
    // spinner.background = `conic-gradient(red ${progress}deg, #333 ${progress}deg)`;
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

// scanButton.addEventListener("click", startScan);

// Change text of main scan button according to clicked type on the sidebar.
// actionList.addEventListener("click", function (event) {
//   if (isScanning) return
//   const value = event.target.textContent;
//   if (event.target.textContent.includes("\n")) return;
//   scan.textContent = value
// });

// remove "Start Scan" span and insert span for inserting

// eel.expose(remove_raw);
// function remove_raw() {
//   raw.parentElement.removeChild(raw);
//   progressFile.insertAdjacentHTML("beforeend", '<span id="content"></span>');
// }

// get total number of files from the python file
eel.expose(total_files);
function total_files(num_of_files) {
  total = num_of_files;
  // total = 100;
  console.log(total);
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
