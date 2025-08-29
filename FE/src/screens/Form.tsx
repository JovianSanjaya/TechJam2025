"use client"
import {
  useState
} from "react"
import {
  toast
} from "@/hooks/use-toast"
import {
  useForm
} from "react-hook-form"
import {
  zodResolver
} from "@hookform/resolvers/zod"
import {
  z
} from "zod"
import {
  cn
} from "@/lib/utils"
import {
  Button
} from "@/components/ui/button"
import {
  Form as FormRoot,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Input
} from "@/components/ui/input"

const formSchema = z.object({
  featureName: z.string().min(1),
  description: z.string().min(1)
});

export function Form() {

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      console.log(values);
      toast({
        title: "Form Submitted",
        description: (
          <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
            <code className="text-white">{JSON.stringify(values, null, 2)}</code>
          </pre>
        ),
      });
    } catch (error) {
      console.error("Form submission error", error);
      toast({
        title: "Error",
        description: "Failed to submit the form. Please try again.",
        variant: "destructive",
      });
    }
  }

  return (
    <FormRoot {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 max-w-3xl mx-auto py-10">
        
        <div className="grid grid-cols-12 gap-4">
          
          <div className="col-span-6">
            
        <FormField
          control={form.control}
          name="featureName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Feature Name</FormLabel>
              <FormControl>
                <Input 
                placeholder="Feature Name"
                
                type="text"
                {...field} />
              </FormControl>
              
              <FormMessage />
            </FormItem>
          )}
        />
          </div>
          
          <div className="col-span-6">
            
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Input 
                placeholder="Description"
                
                type="text"
                {...field} />
              </FormControl>
              
              <FormMessage />
            </FormItem>
          )}
        />
          </div>
          
        </div>
        <Button type="submit">Submit</Button>
      </form>
    </FormRoot>
  )
}
