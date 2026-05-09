#!/usr/bin/env node
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");

const candidates = [
  process.env.CHROME_BIN,
  "/Users/thierryc/Library/Caches/ms-playwright/chromium-1208/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
].filter(Boolean);

const chromeBin = candidates.find((candidate) => existsSync(candidate));
if (!chromeBin) {
  console.error("No Chromium/Chrome binary found. Set CHROME_BIN to a local browser binary.");
  process.exit(1);
}

const jobs = [
  {
    name: "a4",
    html: path.join(root, "specimen-squarebot-sans.html"),
    pdf: path.join(root, "specimen-squarebot-sans.pdf"),
    screenshots: [1, 5, 6, 7, 9, 12, 17, 18, 19, 20, 21, 23, 25, 26, 27],
  },
  {
    name: "letter",
    html: path.join(root, "specimen-squarebot-sans-letter.html"),
    pdf: path.join(root, "specimen-squarebot-sans-letter.pdf"),
    screenshots: [1, 5, 6, 7, 9, 12, 17, 18, 19, 20, 21, 23, 25, 26, 27],
  },
];

const screenshotDir = path.join(root, "tmp", "pdfs", "specimen-checks");
mkdirSync(screenshotDir, { recursive: true });

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForJson(url, timeoutMs = 10000) {
  const start = Date.now();
  let lastError;
  while (Date.now() - start < timeoutMs) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
      lastError = new Error(`${response.status} ${response.statusText}`);
    } catch (error) {
      lastError = error;
    }
    await delay(120);
  }
  throw lastError ?? new Error(`Timed out waiting for ${url}`);
}

class Cdp {
  constructor(url) {
    this.url = url;
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
  }

  async open() {
    this.ws = new WebSocket(this.url);
    this.ws.addEventListener("message", (event) => this.handleMessage(event.data));
    await new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
    });
  }

  handleMessage(data) {
    const message = JSON.parse(data);
    if (message.id && this.pending.has(message.id)) {
      const { resolve, reject } = this.pending.get(message.id);
      this.pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result);
      return;
    }
    const callbacks = this.listeners.get(message.method);
    if (callbacks) callbacks.forEach((callback) => callback(message.params));
  }

  send(method, params = {}, sessionId) {
    const id = this.nextId++;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    this.ws.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
    });
  }

  once(method) {
    return new Promise((resolve) => {
      const callback = (params) => {
        this.off(method, callback);
        resolve(params);
      };
      this.on(method, callback);
    });
  }

  on(method, callback) {
    if (!this.listeners.has(method)) this.listeners.set(method, new Set());
    this.listeners.get(method).add(callback);
  }

  off(method, callback) {
    const callbacks = this.listeners.get(method);
    if (callbacks) callbacks.delete(callback);
  }

  close() {
    this.ws.close();
  }
}

async function createTarget(cdp, url) {
  const { targetId } = await cdp.send("Target.createTarget", { url: "about:blank" });
  const { sessionId } = await cdp.send("Target.attachToTarget", { targetId, flatten: true });
  await cdp.send("Page.enable", {}, sessionId);
  await cdp.send("Runtime.enable", {}, sessionId);
  await cdp.send("Emulation.setEmulatedMedia", { media: "print" }, sessionId);
  const load = cdp.once("Page.loadEventFired");
  await cdp.send("Page.navigate", { url }, sessionId);
  await load;
  await cdp.send(
    "Runtime.evaluate",
    {
      expression: "document.fonts.ready.then(() => true)",
      awaitPromise: true,
      returnByValue: true,
    },
    sessionId,
  );
  await delay(250);
  return { targetId, sessionId };
}

async function exportPdf(cdp, job) {
  const fileUrl = pathToFileURL(job.html).href;
  const { targetId, sessionId } = await createTarget(cdp, fileUrl);
  const result = await cdp.send(
    "Page.printToPDF",
    {
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: false,
      marginTop: 0,
      marginRight: 0,
      marginBottom: 0,
      marginLeft: 0,
      scale: 1,
      transferMode: "ReturnAsBase64",
    },
    sessionId,
  );
  writeFileSync(job.pdf, Buffer.from(result.data, "base64"));
  await cdp.send("Target.closeTarget", { targetId });
}

async function exportScreenshots(cdp, job) {
  for (const entry of readdirSync(screenshotDir)) {
    if (entry.startsWith(`specimen-${job.name}-page-`) && entry.endsWith(".png")) {
      rmSync(path.join(screenshotDir, entry), { force: true });
    }
  }
  const fileUrl = pathToFileURL(job.html).href;
  const { targetId, sessionId } = await createTarget(cdp, fileUrl);
  await cdp.send(
    "Emulation.setEmulatedMedia",
    { media: "screen" },
    sessionId,
  );
  await cdp.send(
    "Emulation.setDeviceMetricsOverride",
    { width: 1400, height: 1000, deviceScaleFactor: 1, mobile: false },
    sessionId,
  );
  const reload = cdp.once("Page.loadEventFired");
  await cdp.send("Page.reload", { ignoreCache: true }, sessionId);
  await reload;
  await cdp.send(
    "Runtime.evaluate",
    {
      expression: "document.fonts.ready.then(() => true)",
      awaitPromise: true,
      returnByValue: true,
    },
    sessionId,
  );
  await delay(250);
  const rectResult = await cdp.send(
    "Runtime.evaluate",
    {
      expression: `Array.from(document.querySelectorAll(".page")).map((page) => {
        const r = page.getBoundingClientRect();
        return { x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height };
      })`,
      returnByValue: true,
    },
    sessionId,
  );
  const rects = rectResult.result.value;
  for (const pageNumber of job.screenshots) {
    const rect = rects[pageNumber - 1];
    const png = await cdp.send(
      "Page.captureScreenshot",
      {
        format: "png",
        captureBeyondViewport: true,
        clip: {
          x: Math.max(0, rect.x),
          y: Math.max(0, rect.y),
          width: rect.width,
          height: rect.height,
          scale: 1,
        },
      },
      sessionId,
    );
    const output = path.join(screenshotDir, `specimen-${job.name}-page-${String(pageNumber).padStart(2, "0")}.png`);
    writeFileSync(output, Buffer.from(png.data, "base64"));
  }
  await cdp.send("Target.closeTarget", { targetId });
}

async function main() {
  for (const job of jobs) {
    if (!existsSync(job.html)) {
      throw new Error(`Missing ${path.relative(root, job.html)}. Run tools/build_specimen.py first.`);
    }
  }

  const userDataDir = path.join(tmpdir(), `squarebot-specimen-chrome-${process.pid}`);
  const port = 40000 + Math.floor(Math.random() * 10000);
  const chrome = spawn(chromeBin, [
    "--headless=new",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-sync",
    "--disable-gpu",
    "--use-mock-keychain",
    "--password-store=basic",
    "about:blank",
  ], {
    stdio: ["ignore", "ignore", "pipe"],
  });

  let stderr = "";
  chrome.stderr.on("data", (chunk) => {
    stderr += chunk.toString();
  });

  try {
    const version = await waitForJson(`http://127.0.0.1:${port}/json/version`, 30000);
    const cdp = new Cdp(version.webSocketDebuggerUrl);
    await cdp.open();
    for (const job of jobs) {
      await exportPdf(cdp, job);
      await exportScreenshots(cdp, job);
      console.log(`wrote ${path.relative(root, job.pdf)}`);
    }
    cdp.close();
  } finally {
    chrome.kill("SIGTERM");
    await delay(300);
    if (!chrome.killed) chrome.kill("SIGKILL");
    rmSync(userDataDir, { recursive: true, force: true });
  }

  if (stderr.includes("ERROR")) {
    const filtered = stderr
      .split("\n")
      .filter((line) => line.includes("ERROR"))
      .slice(0, 8)
      .join("\n");
    if (filtered) console.warn(filtered);
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
