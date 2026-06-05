const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require('electron')
const path = require('path')

const isDev = !app.isPackaged

/**
 * Creates the main calendar window.
 * @returns {BrowserWindow}
 */
function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false,
  })

  if (isDev) {
    win.loadURL('http://localhost:5173')
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  win.once('ready-to-show', () => win.show())
  return win
}

/**
 * Loads the tray icon; falls back to empty image so the tray is still created.
 * @returns {Electron.NativeImage}
 */
function loadTrayIcon() {
  const candidates = [
    path.join(__dirname, isDev ? '../public/favicon.svg' : '../dist/favicon.svg'),
  ]
  for (const p of candidates) {
    try {
      const img = nativeImage.createFromPath(p)
      if (!img.isEmpty()) return img
    } catch (_) {}
  }
  // 1×1 transparent PNG fallback so Tray() never crashes
  return nativeImage.createFromDataURL(
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQ' +
    'AABjkB6QAAAABJRU5ErkJggg=='
  )
}

let tray = null
let mainWindow = null

app.whenReady().then(() => {
  mainWindow = createWindow()

  tray = new Tray(loadTrayIcon())
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Open Calendar', click: () => { mainWindow.show(); mainWindow.focus() } },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ])
  tray.setToolTip('My Calendar')
  tray.setContextMenu(contextMenu)
  tray.on('click', () => {
    mainWindow.isVisible() ? mainWindow.focus() : mainWindow.show()
  })

  // IPC: fire a native OS notification from the renderer
  ipcMain.on('notify', (_event, { title, body }) => {
    const { Notification } = require('electron')
    if (Notification.isSupported()) {
      new Notification({ title, body }).show()
    }
  })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      mainWindow = createWindow()
    } else {
      mainWindow.show()
    }
  })
})

// On macOS keep the process alive when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
