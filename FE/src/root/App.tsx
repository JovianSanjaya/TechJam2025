import { Form } from '@/screens/Form'
import { Toaster } from '@/components/ui/toaster'

export function App() {
  return (
    <div className="min-h-screen p-2 sm:p-4 md:p-6">
      <div className="mx-auto max-w-6xl">
        <Form />
      </div>
      <Toaster />
    </div>
  )
}


