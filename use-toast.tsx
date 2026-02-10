import * as React from "react"

// 1. Define types locally to avoid import errors
type ToastProps = {
  id?: string
  title?: string
  description?: string
  action?: React.ReactNode
  variant?: "default" | "destructive"
}

// 2. Simple state management
let count = 0
function genId() {
  count = (count + 1) % Number.MAX_SAFE_INTEGER
  return count.toString()
}

const listeners: Array<(state: any) => void> = []
let memoryState = { toasts: [] as ToastProps[] }

function dispatch(action: any) {
  if (action.type === "ADD_TOAST") {
    memoryState = { 
      ...memoryState, 
      toasts: [action.toast, ...memoryState.toasts].slice(0, 1) // Limit to 1 toast for simplicity
    }
  }
  if (action.type === "DISMISS_TOAST") {
    memoryState = {
      ...memoryState,
      toasts: memoryState.toasts.filter((t) => t.id !== action.toastId),
    }
  }
  listeners.forEach((listener) => listener(memoryState))
}

// 3. The named export you need
export function useToast() {
  const [state, setState] = React.useState(memoryState)

  React.useEffect(() => {
    listeners.push(setState)
    return () => {
      const index = listeners.indexOf(setState)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }, [state])

  return {
    toast,
    dismiss: (toastId?: string) => dispatch({ type: "DISMISS_TOAST", toastId }),
    toasts: state.toasts,
  }
}

// 4. The standalone toast function export
export const toast = (props: Omit<ToastProps, "id">) => {
  const id = genId()
  const update = { ...props, id }
  dispatch({ type: "ADD_TOAST", toast: update })
  
  // Auto-dismiss after 3 seconds
  setTimeout(() => {
    dispatch({ type: "DISMISS_TOAST", toastId: id })
  }, 3000)
  
  return {
    id,
    dismiss: () => dispatch({ type: "DISMISS_TOAST", toastId: id }),
    update: (props: ToastProps) => dispatch({ type: "UPDATE_TOAST", toast: { ...props, id } }),
  }
}