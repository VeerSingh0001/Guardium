const currentFileContainer = document.querySelector('.current-file-container');
const currentFile = document.getElementById('file-name');
const spinner = document.querySelectorAll('.spinner');
const cancel = document.querySelector('.center button');
const swiperButtons = document.querySelectorAll('.swiper-btn');
const currentProgress = document.getElementById('progress');
const scrolls = document.getElementsByClassName('scrolls')[0];
const updateBtn = document.getElementsByClassName('btn-update')[0];
const historyBtn = document.querySelector('.btn-history');
const historyPage = document.getElementById('history');
const threatSelector = document.getElementById('threat-option');
const globalActionsContainer = document.querySelector('.global-actions');
const quarantineAllBtn = document.getElementById('quarantine-all-btn');
const restoreAllBtn = document.getElementById('restore-all-btn');
const removeAllBtn = document.getElementById('remove-all-btn');
let progressId = '';

let total = 0;
let degreePerFile = 0;
let progress = 0;
let currentFileNumber = 0;
let intervalId = 0;
let isScanning = false;
let scanType = 'quick';
let percentage = 0;

eel.expose(noVirusFound);
function noVirusFound() {
  scrolls.insertAdjacentHTML(
    'beforeend',
    `<div class="result">No virus founded</div>`
  );
}

if (historyBtn)
  historyBtn.addEventListener('click', (event) => {
    if (isScanning) return;
    window.location.href = '/history.html';
  });

if (historyPage) showAllowd();

function threatCollector(type) {
  const rows = document.getElementsByClassName('row');
  if (rows.length < 1) return;

  const threats = Array.from(rows).map((row) => {
    return {
      id: row.id,
      path: row.getAttribute('path'),
      name: row.getAttribute('name'),
      severity: row.getAttribute('severity'),
      history: row.getAttribute('history'),
      catogry: row.getAttribute('category'),
      type,
    };
  });

  return threats;
}

if (removeAllBtn)
  removeAllBtn.addEventListener('click', function (event) {
    const threats = threatCollector('remove');
    for (threat of threats) {
      if (threat.name == null) continue;
      action(
        threat.type,
        threat.id,
        threat.name,
        threat.severity,
        threat.history,
        threat.catogry
      );
    }
    globalActionsContainer.classList.add('hide');
  });

if (quarantineAllBtn)
  quarantineAllBtn.addEventListener('click', function (event) {
    const threats = threatCollector('quarantine');
    for (threat of threats) {
      if (threat.name == null) continue;
      action(
        threat.type,
        threat.id,
        threat.name,
        threat.severity,
        threat.history,
        threat.catogry
      );
    }
    globalActionsContainer.classList.add('hide');
  });

if (restoreAllBtn)
  restoreAllBtn.addEventListener('click', function (event) {
    const threats = threatCollector('restore');
    for (threat of threats) {
      if (threat.name == null) continue;
      action(
        threat.type,
        threat.id,
        threat.name,
        threat.severity,
        threat.history,
        threat.catogry
      );
    }
    globalActionsContainer.classList.add('hide');
  });

// history page initialization/start-up function
function showAllowd(type = 'allowed') {
  if (scrolls) scrolls.innerHTML = '';

  if (type == 'allowed') eel.show_allowed();
  if (type == 'quarantined') eel.show_quarantined();
}

if (threatSelector)
  threatSelector.addEventListener('change', (event) => {
    showAllowd(event.target.value);

    quarantineAllBtn.classList.toggle('hide');
    restoreAllBtn.classList.toggle('hide');
  });

eel.expose(alertUser);
function alertUser() {
  alert("Please run 'service.cmd' file as an adminstartor first");
}

function setNav(type, hide) {
  if (hide) {
    //
    if (type == 'quick') {
      swiperButtons[1].classList.add('swiper-button-disabled');
    } else if (type == 'full') {
      swiperButtons[0].classList.add('swiper-button-disabled');
      swiperButtons[1].classList.add('swiper-button-disabled');
    } else {
      swiperButtons[0].classList.add('swiper-button-disabled');
    }
  } else {
    if (type == 'quick') {
      swiperButtons[1].classList.remove('swiper-button-disabled');
    } else if (type == 'full') {
      swiperButtons[0].classList.remove('swiper-button-disabled');
      swiperButtons[1].classList.remove('swiper-button-disabled');
    } else {
      swiperButtons[0].classList.remove('swiper-button-disabled');
    }
  }
}

function startScan(type) {
  // Reset progress and animation
  scanType = type;
  if (isScanning) return;
  setNav(type, true);

  isScanning = true;
  progressId = document.getElementById(`progress-${type}`);
  progressId.classList.remove('hide');
  progressId.textContent = 'Counting Files...';
  currentFile.textContent = 'Starting Scan...';

  const spinner = document.querySelector(
    `.spinner${type === 'quick' ? '' : `.${type}`}`
  );

  eel.run_scan(type);

  const colors = {
    quick: '--blue',
    full: '--red',
    custom: '--purple',
  };

  progress = 0;
  // Start the progress
  intervalId = setInterval(() => {
    spinner.style.background = `conic-gradient(var(${colors[type]}) ${progress}deg, var(--black) ${progress}deg)`;
    if (percentage != 0) {
      progressId.textContent = percentage;
    }

    if (progress > 360) {
      clearInterval(intervalId);
      isScanning = false;
      setNav(type, false);
      progressId.textContent = 'Scan Completed';
      total = 0;
      degreePerFile = 0;
      progress = 0;
      currentFileNumber = 0;
      percentage = 0;
    }
  }, 1);
}

function cancelScan() {
  progressId.textContent = 'Cancelling';
  eel.cancel_scan(); // Call the Python cancel_scan method
  clearInterval(intervalId);

  intervalId = 0;
}
if (cancel) cancel.addEventListener('click', cancelScan);

function updateDB() {
  if (isScanning) return;
  eel.update_db();
}

if (updateBtn) updateBtn.addEventListener('click', updateDB);

eel.expose(update_interface);
function update_interface() {
  isScanning = false;
  total = 0;
  degreePerFile = 0;
  progress = 0;
  currentFileNumber = 0;
  percentage = 0;
  spinner[0].style.background = `conic-gradient(var(--blue) ${0}deg, var(--black) ${0}deg)`;
  spinner[1].style.background = `conic-gradient(var(--red) ${0}deg, var(--black) ${0}deg)`;
  spinner[2].style.background = `conic-gradient(var(--purple) ${0}deg, var(--black) ${0}deg)`;
  setNav(scanType, false);
  currentFileContainer.classList.add('hide');
  currentFile.textContent = 'Scanning Stopped';
  progressId.classList.add('hide');
}

// Get total number of files from the python file
eel.expose(total_files);
function total_files(num_of_files) {
  total = num_of_files;
  degreePerFile = 360 / total;
}

// Show the current scanning file on the front-end
eel.expose(current_file);
function current_file(file_name) {
  if (currentFileContainer.classList.contains('hide')) {
    currentFileContainer.classList.remove('hide');
  }
  currentFileNumber += 1;
  progress += degreePerFile; // Increase progress
  file = file_name;
  if (intervalId != 0) {
    currentFile.textContent = limitString(file_name, 30);
    percentage = `${Math.round((currentFileNumber / total) * 100) || 0}%`;
  }
}

// Limiting the length the file path showing on the front-end
function limitString(str, noOfChars) {
  if (str.length <= noOfChars) return str;

  return `${str.split('').slice(0, noOfChars).join('')}...`;
}

// Show detected viruses
eel.expose(showResult);
function showResult(result, history, type = NaN) {
  present = document.getElementsByClassName(result['virus_path'])[0];
  if ((intervalId == 0 || present) && !history) return;

  const res = document.getElementsByClassName('result')[0];
  if (res) res.classList.add('hide');

  const id = `${Math.round(Math.random() * 1_000_000)}${Date.now()}`;

  scrolls.insertAdjacentHTML(
    'beforeend',
    `<div class="row ${result['virus_path']}" 
      id="${id}" 
      path="${result['virus_path']}"
      name="${result['virus_name']}"
      severity="${result['severity']}"
      history="${history === true ? true : false}"
      category="${type === 'allowed' ? 'allowed' : 'quarantined'}"
      >
          <div class="col title">${result['virus_name']}</div>
            <div class="col risk risk-${result['severity'].toLowerCase()}">${
      result['severity']
    }</div>
          <div class="col actions">
            <button class="btn" onclick="action('remove', '${id}', '${
      result['virus_name']
    }' , '${result['severity']}', '${history === true ? true : false}', '${
      type === 'allowed' ? 'allowed' : 'quarantined'
    }')">Remove</button>
            
            
            ${
              type !== 'quarantined'
                ? `<button class="btn" onclick="action('quarantine', '${id}', '${
                    result['virus_name']
                  }' , '${result['severity']}', '${
                    history === true ? true : false
                  }', '${
                    type === 'allowed' ? 'allowed' : 'quarantined'
                  }')">Quarantine</button>`
                : ''
            }
            
    
        ${
          historyPage && type === 'quarantined'
            ? `<button class="btn" onclick="action('restore', '${id}', '${
                result['virus_name']
              }' , '${result['severity']}', '${
                history === true ? true : false
              }')">Restore</button>`
            : ''
        }
    
    ${
      type !== 'allowed'
        ? `<button class="btn" onclick="action('allow', '${id}', '${
            result['virus_name']
          }' , '${result['severity']}', '${
            history === true ? true : false
          }')">Allow</button>`
        : ''
    }
          </div>
        </div>`
  );

  globalActionsContainer.classList.remove('hide');
}

function action(type, id, vname, vseverity, history = false, catogry = '') {
  const el = document.getElementById(id);
  let path = el.classList[1];
  eel.actions(type, id, vname, path, vseverity, history, catogry);

  el.parentElement.removeChild(el);
}

eel.expose(showGlobalBtns);
function showGlobalBtns(type = 'allowed') {
  if (type == 'quarantined') {
    quarantineAllBtn.classList.add('hide');
    restoreAllBtn.classList.remove('hide');
  }
}
