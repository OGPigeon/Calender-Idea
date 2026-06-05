const { contextBridge, ipcRenderer } = require('electron')

/**
 * Exposes a safe subset of Electron APIs to the React renderer.
 * Access via window.electronAPI in the browser context.
 */
contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,
  platform: process.platform,

  /**
   * Show a native OS notification.
   * @param {string} title
   * @param {string} body
   */
  notify: (title, body) => ipcRenderer.send('notify', { title, body }),
})
