import {
  app,
  BrowserWindow,
  clipboard,
  globalShortcut,
  ipcMain,
  Menu,
  nativeImage,
  Notification,
  Tray
} from "electron";
import { join } from "node:path";
import {
  DEFAULT_API_BASE_URL,
  type AudioDevice,
  type HealthResponse,
  type RecordingStatus,
  type StopRecordingResponse,
  type StructureResponse,
  type TranscribeResponse,
  type VoiceFinishResponse,
  type VoiceTranscribeResponse
} from "@liketypeless/shared";
import { getForegroundWindowHandle, pasteIntoWindow } from "./windows-input";

const API_BASE_URL = process.env.LIKETYPELESS_API_BASE_URL ?? DEFAULT_API_BASE_URL;
const RENDERER_DEV_URL = process.env.ELECTRON_RENDERER_URL ?? "http://localhost:5173";
const GLOBAL_HOTKEY = process.env.LIKETYPELESS_GLOBAL_HOTKEY ?? "Shift+Space";

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let isQuitting = false;
let hotkeyWorkflowRunning = false;
let targetWindowHandle: string | null = null;

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 980,
    height: 680,
    minWidth: 760,
    minHeight: 540,
    title: "liketypeless",
    backgroundColor: "#f7f7f4",
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.webContents.on("did-fail-load", (_event, errorCode, errorDescription, validatedURL) => {
    console.error(`Renderer load failed: ${errorCode} ${errorDescription} ${validatedURL}`);
  });

  mainWindow.webContents.on("console-message", (_event, level, message) => {
    console.log(`Renderer console [${level}]: ${message}`);
  });

  mainWindow.on("close", (event) => {
    if (isQuitting) {
      return;
    }

    event.preventDefault();
    mainWindow?.hide();
  });

  if (process.env.ELECTRON_RENDERER_URL || !app.isPackaged) {
    void mainWindow.loadURL(RENDERER_DEV_URL);
  } else {
    void mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
  }
}

function showMainWindow(): void {
  mainWindow?.show();
  mainWindow?.focus();
}

function createTray(): void {
  const icon = nativeImage.createEmpty();
  tray = new Tray(icon);
  tray.setToolTip("liketypeless");
  tray.setContextMenu(
    Menu.buildFromTemplate([
      {
        label: "Show liketypeless",
        click: showMainWindow
      },
      {
        label: `Hotkey: ${GLOBAL_HOTKEY}`,
        enabled: false
      },
      { type: "separator" },
      {
        label: "Quit",
        click: () => {
          isQuitting = true;
          app.quit();
        }
      }
    ])
  );
  tray.on("double-click", showMainWindow);
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`${path} failed with ${response.status}: ${await response.text()}`);
  }
  return (await response.json()) as T;
}

async function postJson<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: body === undefined ? undefined : JSON.stringify(body)
  });

  if (!response.ok) {
    throw new Error(`${path} failed with ${response.status}: ${await response.text()}`);
  }

  return (await response.json()) as T;
}

ipcMain.handle("api:health", async (): Promise<HealthResponse> => {
  return getJson<HealthResponse>("/health");
});

ipcMain.handle("api:audio-devices", async (): Promise<AudioDevice[]> => {
  return getJson<AudioDevice[]>("/audio/devices");
});

ipcMain.handle("api:recording-status", async (): Promise<RecordingStatus> => {
  return getJson<RecordingStatus>("/audio/recording/status");
});

ipcMain.handle("api:start-recording", async (): Promise<RecordingStatus> => {
  return postJson<RecordingStatus>("/audio/recording/start");
});

ipcMain.handle("api:stop-recording", async (): Promise<StopRecordingResponse> => {
  return postJson<StopRecordingResponse>("/audio/recording/stop");
});

ipcMain.handle("api:transcribe", async (_event, filePath: string, provider?: string): Promise<TranscribeResponse> => {
  return postJson<TranscribeResponse>("/stt/transcribe", { filePath, provider });
});

ipcMain.handle("api:transcribe-voice-recording", async (): Promise<VoiceTranscribeResponse> => {
  return postJson<VoiceTranscribeResponse>("/voice/recording/transcribe");
});

ipcMain.handle("api:finish-voice-recording", async (): Promise<VoiceFinishResponse> => {
  return postJson<VoiceFinishResponse>("/voice/recording/finish");
});

ipcMain.handle("api:structure", async (_event, text: string): Promise<StructureResponse> => {
  return postJson<StructureResponse>("/llm/structure", { text });
});

function notify(title: string, body: string): void {
  if (Notification.isSupported()) {
    new Notification({ title, body }).show();
  }
}

async function handleGlobalHotkey(): Promise<void> {
  if (hotkeyWorkflowRunning) {
    return;
  }

  hotkeyWorkflowRunning = true;

  try {
    if (!targetWindowHandle) {
      targetWindowHandle = await getForegroundWindowHandle();
      await postJson<RecordingStatus>("/audio/recording/start");
      notify("liketypeless", `开始录音，再按 ${GLOBAL_HOTKEY} 结束`);
      return;
    }

    const result = await postJson<VoiceFinishResponse>("/voice/recording/finish");
    const text = result.structuredText.trim() || result.transcript.trim();
    if (!text) {
      throw new Error("语音识别没有返回文本");
    }

    const previousClipboardText = clipboard.readText();
    clipboard.writeText(text);

    try {
      await pasteIntoWindow(targetWindowHandle);
    } finally {
      setTimeout(() => clipboard.writeText(previousClipboardText), 250);
    }

    notify("liketypeless", `已输入，耗时 ${result.totalElapsedMs} ms`);
    targetWindowHandle = null;
  } catch (error) {
    targetWindowHandle = null;
    const message = error instanceof Error ? error.message : String(error);
    console.error(`Global hotkey workflow failed: ${message}`);
    notify("liketypeless 失败", message);
  } finally {
    hotkeyWorkflowRunning = false;
  }
}

function registerGlobalHotkey(): void {
  const registered = globalShortcut.register(GLOBAL_HOTKEY, () => {
    void handleGlobalHotkey();
  });

  if (!registered) {
    console.error(`Unable to register global hotkey: ${GLOBAL_HOTKEY}`);
    notify("liketypeless", `快捷键注册失败：${GLOBAL_HOTKEY}`);
  } else {
    console.log(`Global hotkey registered: ${GLOBAL_HOTKEY}`);
  }
}

app.whenReady().then(() => {
  createWindow();
  createTray();
  registerGlobalHotkey();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else {
      showMainWindow();
    }
  });
});

app.on("will-quit", () => {
  globalShortcut.unregisterAll();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin" && isQuitting) {
    app.quit();
  }
});
