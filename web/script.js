const scanButton = document.getElementById("scanButton");
const progressCircle = document.querySelector(".progress-circle");

total = 100;
current = 0;
let progress = 0;
let intervalId;

function startScan() {
  // Reset progress and animation
  eel.start_scan()
  progress = 0;
  current = 0;
  progressCircle.style.background = "conic-gradient(red 0deg, #333 0deg)";

  // Start the progress
  intervalId = setInterval(() => {
    progress = (current / total) * 100; // Increase progress
    progressCircle.style.background = `conic-gradient(red ${progress}deg, #333 ${progress}deg)`;

    current += 1;
    if (progress >= 360) {
      clearInterval(intervalId);
      // alert("Scan Complete!");
      console.log("Scan complete");
    }
  }, 1);
}

scanButton.addEventListener("click", startScan);
