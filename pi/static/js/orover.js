/*  o R o v e r  Object Recognition and Versatile Exploration Robot
     License      MIT License, Copyright (C) 2026 C v Kruijsdijk & P. Zengers
     Description  javascript library for oRover web interface
*/

// Socket.IO client setup
const socket = io()
socket.on("connect", () => {
  console.log("Connected to server");
});

function asFixed(value, digits = 2, fallback = "--") {
  const n = Number(value);
  return Number.isFinite(n) ? n.toFixed(digits) : fallback;
}

socket.on("statusUpdate", (data) => {
  console.log("Received statusUpdate:", data);
  //document.getElementById("temperature").textContent = asFixed(data.temperature);
  //d/ocument.getElementById("speed").textContent = asFixed(data.speed);
  //document.getElementById("angle").textContent = asFixed(data.angle);
});

//socket.on("imu_state", (data) => {
//  //  socketio.emit("imu_state", {"heading": heading, "pitch": pitch, "roll": roll})
//  console.log("Received:", data);
//  document.getElementById("imuHeading").textContent = asFixed(data.heading);
//  document.getElementById("imuPitch").textContent = asFixed(data.pitch);
//  document.getElementById("imuRoll").textContent = asFixed(data.roll);
//});

//socket.on("battery_state", (data) => {
//  console.log("Received:", data);
//  document.getElementById("voltage").textContent = asFixed(data.voltage);
//});
//socket.on("nav_state", (data) => {
//  const pose = data.pose || {};
//  const speed = data.speed || {};
//  const grid = data.grid || {};
//
//  document.getElementById("navPose").textContent =
//    `x=${Number(pose.x_m || 0).toFixed(2)}, y=${Number(pose.y_m || 0).toFixed(2)}, h=${Number(pose.heading_deg || 0).toFixed(2)}`;
//  document.getElementById("navSpeed").textContent =
//    `L=${speed.left_mps ?? '--'}, R=${speed.right_mps ?? '--'}`;
//  document.getElementById("navObstacles").textContent = String(data.obstacle_count ?? 0);
//
//  const preview = Array.isArray(grid.preview) ? grid.preview : [];
//  document.getElementById("navGridMeta").textContent =
//    `${preview.length}x${preview[0] ? preview[0].length : 0}, res=${grid.resolution_m ?? '--'}m`;
//
//  const chars = preview.map((row) =>
//    row.map((v) => {
//      if (v >= 0.8) return "#";
//      if (v >= 0.2) return "+";
//      return ".";
//    }).join("")
//  ).join("\n");
//  document.getElementById("navGrid").textContent = chars;
//});

const HB_INTERVAL_MS = {{ heartbeat_interval }} * 1000;
const HB_STALE_MS    = HB_INTERVAL_MS * 1.2;

//socket.on("heartbeat", (data) => {
//  const tbody = document.getElementById("heartbeat");
//  // Extract HH:MM:SS from ISO timestamp e.g. "2026-04-12T14:23:01.123456"
//  const ts = data.timestamp && data.timestamp.includes("T")
//    ? data.timestamp.split("T")[1].substring(0, 8)
//    : data.timestamp;
//  let row = tbody.querySelector(`tr[data-name="${data.me}"]`);
//  if (!row) {
//    row = document.createElement("tr");
//    row.dataset.name = data.me;
//    row.innerHTML = `<td style="text-align:left">${data.me}</td><td class="hb-ts"></td>`;
//    tbody.appendChild(row)//;
//  }
//  const tsCell = row.querySelector(".hb-ts");
//  tsCell.textContent = ts;
//  tsCell.style.color = "";
//  row.dataset.lastSeen = Date.now();
//});

// Periodically mark timestamps red when no heartbeat received within interval * 1.2
setInterval(() => {
  const now = Date.now();
  document.querySelectorAll("#heartbeat tr[data-last-seen]").forEach(row => {
    const tsCell = row.querySelector(".hb-ts");
    const age = now - Number(row.dataset.lastSeen);
    tsCell.style.color = age > HB_STALE_MS ? "red" : "";
  });
}, 1000);

async function sendAction(action) {
  try {
    const res = await fetch('/control', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({action})
    });
    if (!res.ok) {
      const err = await res.json().catch(()=>({}));
      console.error('Control error', err);

    } else {
      // optionally update status immediately after action
      //updateStatus();
    }
  } catch (e) {
    console.error(e);
  }
}

let route = [];

function addStep() {
  const distance = document.getElementById('afstandInput').value;
  const angle = document.getElementById('hoekInput').value;

  if (distance === '' || angle === '') return;

  route.push({ distance: Number(distance), angle: Number(angle) });

  const li = document.createElement('li');
  li.textContent = `Distance: ${distance}, Angle: ${angle}°`;
  document.getElementById('routeList').appendChild(li);

  document.getElementById('afstandInput').value = '';
  document.getElementById('hoekInput').value = '';
}

function askRouteFilename(actionLabel) {
  const name = prompt(`Enter filename to ${actionLabel} route:`, "commands.csv");
  if (name === null) {
    return null;
  }
  const trimmed = name.trim();
  if (!trimmed) {
    alert('Filename is required.');
    return null;
  }
  return trimmed;
}

async function saveRoute() {
  const filename = askRouteFilename('save');
  if (!filename) {
    return;
  }

  try {
    const res = await fetch('/route', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ route, filename })
    });

    if (res.ok) {
      alert(`Route saved as ${filename}!`);
      route = [];
      document.getElementById('routeList').innerHTML = '';
    }
  } catch (e) {
    console.error(e);
  }
}

async function readRoute() {
  try {
    const res = await fetch('/route-files');
    const data = await res.json();
    const files = data.files || [];
    const list = document.getElementById('routeFileList');
    list.innerHTML = '';
    if (files.length === 0) {
      list.innerHTML = '<li style="padding:8px; color:#888;">No route files found.</li>';
    } else {
      files.forEach(f => {
        const li = document.createElement('li');
        li.textContent = f;
        li.style.cssText = 'padding:8px 12px; cursor:pointer; border-bottom:1px solid #eee;';
        li.addEventListener('mouseenter', () => li.style.background = '#f0f4ff');
        li.addEventListener('mouseleave', () => li.style.background = '');
        li.addEventListener('click', () => loadRouteFile(f));
        list.appendChild(li);
      });
    }
    const overlay = document.getElementById('routePickerOverlay');
    overlay.style.display = 'flex';
  } catch (e) {
    console.error(e);
    alert('Could not fetch route files.');
  }
}

function closeRoutePicker() {
  document.getElementById('routePickerOverlay').style.display = 'none';
}

async function loadRouteFile(filename) {
  closeRoutePicker();
  try {
    const res = await fetch('/readroute', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ filename })
    });
    if (res.ok) {
      alert(`Route "${filename}" loaded!`);
    } else {
      const err = await res.json().catch(() => ({}));
      alert(`Error loading route: ${err.error || res.statusText}`);
    }
  } catch (e) {
    console.error(e);
  }
}

/*    let intervalId = null;

    function startRepeating() {
        if (intervalId === null) {
            intervalId = setInterval(() => {
                sendAction('forward');
            }, 300); // elke 300 ms
        }
    }

    function stopRepeating() {
        if (intervalId !== null) {
            clearInterval(intervalId);
            intervalId = null;
            sendAction('stop');
        }
    }

    const btn = document.getElementById("fwdBtn");

    // Desktop
    btn.addEventListener("mousedown", startRepeating);
    btn.addEventListener("mouseup", stopRepeating);
    btn.addEventListener("mouseleave", stopRepeating);

    // Mobile
    btn.addEventListener("touchstart", startRepeating);
    btn.addEventListener("touchend", stopRepeating);
*/

const intervals = {};   // store interval per action
const INTERVAL_MS = 100; // faster = more responsive stop

function startRepeating(action) {
    //if (!intervals[action]) {
        sendAction(action); // immediate first command
     //   intervals[action] = setInterval(() => {
    //        sendAction(action);
   //     }, INTERVAL_MS);
 //   }
}

function stopRepeating(action) {
  //  if (intervals[action]) {
  //      clearInterval(intervals[action]);
  //      delete intervals[action];
        sendAction('stop');
  //  }
}

function bindButton(buttonId) {
    const btn = document.getElementById(buttonId);
    const action = btn.dataset.action;

    // Desktop
    btn.addEventListener("mousedown", () => startRepeating(action));
    btn.addEventListener("mouseup",   () => stopRepeating(action));
    //btn.addEventListener("mouseleave",() => stopRepeating(action));

    // Mobile
    btn.addEventListener("touchstart", e => {
        e.preventDefault(); // important for mobile!
        startRepeating(action);
    });
    btn.addEventListener("touchend", () => stopRepeating(action));
}

// Bind all buttons
["fwdBtn", "backBtn", "leftBtn", "rightBtn"].forEach(bindButton);