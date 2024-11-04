const currentFileContainer = document.querySelector(".current-file-container");
const currentFile = document.querySelector(
  ".current-file-container .current-file"
);
const spinner = document.querySelectorAll(".spinner");
const cancel = document.querySelector(".center button");
const scanResult = document.getElementsByClassName("virus-detect")[0];
const swiperButtons = document.querySelectorAll(".swiper-btn");

let total = 0;
let degreePerFile = 0;
let progress = 0;
let intervalId;
let isScanning = false;
let scanType = "quick"

function setNav(type, hide){
    if (hide) {
      // 
      if (type == "quick"){
        swiperButtons[1].classList.add('swiper-button-disabled')
      }
      else if (type == "full"){
        swiperButtons[0].classList.add('swiper-button-disabled')
        swiperButtons[1].classList.add('swiper-button-disabled')
      }
      else{
        swiperButtons[0].classList.add('swiper-button-disabled')
      }
    } else {
      if (type == "quick"){
        swiperButtons[1].classList.remove('swiper-button-disabled')
      }
      else if (type == "full"){
        swiperButtons[0].classList.remove('swiper-button-disabled')
        swiperButtons[1].classList.remove('swiper-button-disabled')
      }
      else{
        swiperButtons[0].classList.remove('swiper-button-disabled')
      }
    }

}


function startScan(type) {
  // Reset progress and animation
  scanType = type
  if (isScanning) return;
  setNav(type, true)
  // swiperNext.classList.add('swiper-button-disabled')
  // swiperPrev.classList.add('swiper-button-disabled')

  isScanning = true;
  currentFile.textContent = "Starting Scan...";
  const spinner = document.querySelector(
    `.spinner${type === "quick" ? "" : `.${type}`}`
  );
  isScanning = true;

  eel.run_scan(type);

  const colors = {
    quick: "--blue",
    full: "--red",
    custom: "--purple",
  };

  progress = 0;
  // Start the progress
  intervalId = setInterval(() => {
    spinner.style.background = `conic-gradient(var(${colors[type]}) ${progress}deg, var(--black) ${progress}deg)`;
    // spinner[0].style.background = `conic-gradient(var(--blue) ${progress}deg, var(--black) ${progress}deg)`;
    // spinner[1].style.background = `conic-gradient(var(--red) ${progress}deg, var(--black) ${progress}deg)`;
    // spinner[2].style.background = `conic-gradient(var(--purple) ${progress}deg, var(--black) ${progress}deg)`;

    if (progress > 360) {
      console.log("Scan complete");
      eel.show_result();
      clearInterval(intervalId);
      isScanning = false;
      setNav(type, false)
      // swiperNext.classList.remove('swiper-button-disabled')
      // swiperPrev.classList.remove('swiper-button-disabled')
    }
  }, 1);
}

function cancelScan() {
  progress = 0;
  spinner[0].style.background = `conic-gradient(var(--blue) ${0}deg, var(--black) ${0}deg)`;
  spinner[1].style.background = `conic-gradient(var(--red) ${0}deg, var(--black) ${0}deg)`;
  spinner[2].style.background = `conic-gradient(var(--purple) ${0}deg, var(--black) ${0}deg)`;
  // swiperNext.classList.remove('swiper-button-disabled')
  // swiperPrev.classList.remove('swiper-button-disabled')
  setNav(scanType, false)
  eel.cancel_scan(); // Call the Python cancel_scan method
  clearInterval(intervalId);
  currentFile.textContent = "Scanning Stopped";
}
cancel.addEventListener("click", cancelScan);

// Get total number of files from the python file
eel.expose(total_files);
function total_files(num_of_files) {
  total = num_of_files;
  degreePerFile = 360 / total;
}

// Show the current scanning file on the front-end
eel.expose(current_file);
function current_file(file_name) {
  if (currentFileContainer.classList.contains("hide")) {
    currentFileContainer.classList.remove("hide");
  }
  progress += degreePerFile; // Increase progress
  file = file_name;
  currentFile.textContent = limitString(file_name, 30);
}

// Limiting the length the file path showing on the front-end
function limitString(str, noOfChars) {
  if (str.length <= noOfChars) return str;

  return `${str.split("").slice(0, noOfChars).join("")}...`;
}

// Show detected viruses
eel.expose(showResult);
function showResult(result) {
  scanResult.innerHTML = "";
  scanResult.insertAdjacentHTML(
    "beforeend",
    `<div class="threats">
      <div class="row title">
        <div class="col title">Threat</div>
        <div class="col risk">Risk</div>
        <div class="col actions">Action</div>
      </div>
      <div class="scrolls">
      </div>
    </div>`
  );
  const scrolls = document.getElementsByClassName("scrolls")[0];
  if (result.length < 1) {
    scrolls.insertAdjacentHTML(
      "beforeend",
      `<div class="result">No virus founded</div>`
    );
  } else {
    result.forEach((res) => {
      scrolls.insertAdjacentHTML(
        "beforeend",
        `<div class="row">
          <div class="col title">${res["virus_name"]}</div>
          <div class="col risk risk-${res["severity"].toLowerCase()}">${
          res["severity"]
        }</div>
          <div class="col actions">
              <button class="btn" onclick="action('remove')">Remove</button>
              <button class="btn" onclick="action('Quarantine')">Quarantine</button>
              <button class="btn" onclick="action('allow')">Allow</button>
          </div>
        </div>
      `
      );
    });
  }
}
