import { useCallback } from 'react'
import toast from 'react-hot-toast'

interface ToastOptions {
  title: string
  description?: string
  variant?: 'default' | 'destructive' | 'success'
}

export function useToast() {
  const showToast = useCallback(({ title, description, variant = 'default' }: ToastOptions) => {
    const message = description ? `${title}: ${description}` : title
    
    switch (variant) {
      case 'success':
        toast.success(message)
        break
      case 'destructive':
        toast.error(message)
        break
      default:
        toast(message)
        break
    }
  }, [])

  return { toast: showToast }
}
