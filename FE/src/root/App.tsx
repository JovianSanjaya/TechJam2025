import { Form } from '@/screens/Form'
import { Toaster } from '@/components/ui/toaster'
import { FormNotion } from "@/screens/FormNotion"

export function App() {
  return (
    <div className="min-h-screen p-2 sm:p-4 md:p-6">
      <div className="mx-auto max-w-6xl">
        <FormNotion />
      </div>
      <Toaster />
    </div>
  )
}


