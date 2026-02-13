import { invoke as tauriInvoke } from '@tauri-apps/api/core'

/**
 * Type-safe wrapper for Tauri invoke
 *
 * Usage:
 *   const result = await invoke<string>('greet', { name: 'World' })
 */
export async function invoke<T>(cmd: string, args?: Record<string, unknown>): Promise<T> {
  return tauriInvoke<T>(cmd, args)
}

/**
 * Available commands (add types as you create new commands):
 *
 * greet: (args: { name: string }) => string
 */
