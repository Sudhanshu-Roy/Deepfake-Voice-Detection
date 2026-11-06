const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "")
  .trim()
  .replace(/\/$/, "");
const MAX_BYTES = 25 * 1024 * 1024;

const form = document.querySelector("#detector");
const drop = document.querySelector("#drop");
const fileInput = document.querySelector("#file");
const fileMeta = document.querySelector("#file-meta");
const player = document.querySelector("#player");
const predictButton = document.querySelector("#predict");
const sampleButtons = document.querySelectorAll(".sample");
const status = document.querySelector("#status");
const result = document.querySelector("#result");
const prediction = document.querySelector("#prediction");
const confidence = document.querySelector("#confidence");

let objectUrl = "";
let slowTimer = 0;

function setStatus(message, isError) {
  status.textContent = message;
  status.classList.toggle("error", Boolean(isError));
}

function clearResult() {
  result.hidden = true;
  result.classList.remove("real", "fake");
  prediction.textContent = "";
  confidence.textContent = "";
}

function formatSize(bytes) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function setFile(file) {
  clearResult();
  if (!file) {
    predictButton.disabled = true;
    fileMeta.hidden = true;
    player.hidden = true;
    return;
  }

  const name = file.name || "audio.wav";
  if (!name.toLowerCase().endsWith(".wav")) {
    setStatus("Please choose a WAV file.", true);
    fileInput.value = "";
    predictButton.disabled = true;
    return;
  }
  if (file.size > MAX_BYTES) {
    setStatus("That file is larger than 25 MB.", true);
    fileInput.value = "";
    predictButton.disabled = true;
    return;
  }

  if (objectUrl) {
    URL.revokeObjectURL(objectUrl);
  }
  objectUrl = URL.createObjectURL(file);
  player.src = objectUrl;
  player.hidden = false;
  fileMeta.hidden = false;
  fileMeta.textContent = `${name} · ${formatSize(file.size)}`;
  predictButton.disabled = !API_BASE_URL;
  setStatus("");
}

fileInput.addEventListener("change", () => {
  setFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach((eventName) => {
  drop.addEventListener(eventName, (event) => {
    event.preventDefault();
    drop.classList.add("drag");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  drop.addEventListener(eventName, (event) => {
    event.preventDefault();
    drop.classList.remove("drag");
  });
});

drop.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (!file) {
    return;
  }
  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;
  setFile(file);
});

player.addEventListener("loadedmetadata", () => {
  if (Number.isFinite(player.duration) && player.duration < 1) {
    setStatus("This clip is shorter than 1 second. The model needs a longer WAV.", true);
  }
});

function setBusy(busy) {
  predictButton.disabled = busy || !fileInput.files[0];
  sampleButtons.forEach((button) => {
    button.disabled = busy;
  });
}

async function predictFile(file) {
  if (!API_BASE_URL) {
    setStatus("This detector is not configured.", true);
    return;
  }

  clearResult();
  setBusy(true);
  setStatus("Running the model…", false);
  window.clearTimeout(slowTimer);
  slowTimer = window.setTimeout(() => {
    setStatus("Still working. The server can take a minute to wake up.", false);
  }, 8000);

  const body = new FormData();
  body.append("file", file, file.name);

  try {
    const response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      body,
    });
    let payload = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    if (!response.ok) {
      const detail = payload && payload.detail;
      const message = typeof detail === "string"
        ? detail
        : "The server could not score this file.";
      throw new Error(message);
    }

    prediction.textContent = payload.prediction;
    confidence.textContent = `${(Number(payload.confidence) * 100).toFixed(2)}%`;
    result.classList.add(payload.prediction === "FAKE" ? "fake" : "real");
    result.hidden = false;
    setStatus("");
  } catch (error) {
    const message = error && error.message === "Failed to fetch"
      ? "Could not reach the server. Try again in a moment."
      : (error.message || "Prediction failed.");
    setStatus(message, true);
  } finally {
    window.clearTimeout(slowTimer);
    setBusy(false);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) {
    return;
  }
  predictFile(file);
});

sampleButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    setBusy(true);
    setStatus("Loading sample…", false);
    try {
      const response = await fetch(button.dataset.sample);
      if (!response.ok) {
        throw new Error("The sample audio could not be loaded.");
      }
      const blob = await response.blob();
      const file = new File([blob], button.dataset.name, { type: "audio/wav" });
      const transfer = new DataTransfer();
      transfer.items.add(file);
      fileInput.files = transfer.files;
      setFile(file);
      await predictFile(file);
    } catch (error) {
      setStatus(error.message || "The sample audio could not be loaded.", true);
      setBusy(false);
    }
  });
});

if (!API_BASE_URL) {
  setStatus("This detector is not configured.", true);
}
