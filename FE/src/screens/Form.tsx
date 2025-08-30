// "use client"
// import {
//   useState
// } from "react"
// import {
//   toast
// } from "@/hooks/use-toast"
// import {
//   useForm
// } from "react-hook-form"
// import {
//   zodResolver
// } from "@hookform/resolvers/zod"
// import {
//   z
// } from "zod"
// import {
//   cn
// } from "@/lib/utils"
// import {
//   Button
// } from "@/components/ui/button"
// import {
//   Form as FormRoot,
//   FormControl,
//   FormDescription,
//   FormField,
//   FormItem,
//   FormLabel,
//   FormMessage,
// } from "@/components/ui/form"
// import {
//   Input
// } from "@/components/ui/input"
// import {
//   Label
// } from "@/components/ui/label"
// import { buildApiUrl, API_CONFIG } from "@/config/api"

// const formSchema = z.object({
//   featureName: z.string().min(1),
//   description: z.string().min(1)
// });

// export function Form() {
//   const [isLoading, setIsLoading] = useState(false)
//   const [analysisResult, setAnalysisResult] = useState<any>(null)

//   const form = useForm<z.infer<typeof formSchema>>({
//     resolver: zodResolver(formSchema)
//   })

//   async function onSubmit(values: z.infer<typeof formSchema>) {
//     try {
//       setIsLoading(true)
//       setAnalysisResult(null)
      
//       console.log("Submitting form:", values);
//       console.log("API Config:", API_CONFIG);
//       console.log("API URL:", buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE));
      
//       // API call to compliance analysis backend (Docker)
//       console.log("About to make fetch request to:", buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE));
      
//       const requestBody = {
//         featureName: values.featureName,
//         description: values.description
//       };
      
//       console.log("Request body:", requestBody);
      
//       const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(requestBody),
//       })

      

      
//       if (!response.ok) {
//         throw new Error(`API request failed: ${response.status}`)
//       }

//       const result = await response.json()

//       if(result.analysis_results.length > 0){
//         console.log("Analysis results:", result.analysis_results[0]);
//       }
//       else{
//         console.log("Not working bro");
//       }

      
      
//       // Extract the first analysis result from the BE/app.py response format
//       if (result.status === 'success' && result.analysis_results && result.analysis_results.length > 0) {
//         setAnalysisResult(result.analysis_results[0])
//       } else {
//         throw new Error('No analysis results received')
//       }
      
//       toast({
//         title: "Analysis Complete!",
//         description: `Compliance analysis completed for "${values.featureName}"`,
//       });
      
//     } catch (error) {
//       console.error("Form submission error", error);
//       toast({
//         title: "Error",
//         description: error instanceof Error ? error.message : "Failed to submit the form. Please try again.",
//         variant: "destructive",
//       });
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   return (
//     <FormRoot {...form}>
//       <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 max-w-3xl mx-auto py-10">
        
//         <div className="grid grid-cols-12 gap-4">
          
//           <div className="col-span-6">
//             <FormField
//               control={form.control}
//               name="featureName"
//               render={({ field }) => (
//                 <FormItem>
//                   <FormLabel>Feature Name</FormLabel>
//                   <FormControl>
//                     <Input 
//                       placeholder="e.g., User Profile with Age Verification"
//                       type="text"
//                       {...field} 
//                     />
//                   </FormControl>
//                   <FormMessage />
//                 </FormItem>
//               )}
//             />
//           </div>
          

          
//         </div>

//         <FormField
//           control={form.control}
//           name="description"
//           render={({ field }) => (
//             <FormItem>
//               <FormLabel>Description</FormLabel>
//               <FormControl>
//                 <Input 
//                   placeholder="Describe the feature and its functionality..."
//                   type="text"
//                   {...field} 
//                 />
//               </FormControl>
//               <FormMessage />
//             </FormItem>
//           )}
//         />



//         <Button type="submit" disabled={isLoading}>
//           {isLoading ? "Analyzing..." : "Analyze Compliance"}
//         </Button>
//       </form>

//       {/* Analysis Results */}
//       {analysisResult && (
//         <div className="mt-8 p-6 bg-slate-50 rounded-lg border">
//           <h2 className="text-2xl font-bold mb-4">Compliance Analysis Results</h2>
          
//           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//             <div>
//               <h3 className="text-lg font-semibold mb-2">Feature Details</h3>
//               <div className="space-y-2">
//                 <p><strong>Name:</strong> {analysisResult.feature_name}</p>
//                 <p><strong>Risk Level:</strong> 
//                   <span className={`ml-2 px-2 py-1 rounded text-sm font-medium ${
//                     analysisResult.risk_level === 'high' ? 'bg-red-100 text-red-800' :
//                     analysisResult.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
//                     analysisResult.risk_level === 'low' ? 'bg-green-100 text-green-800' :
//                     'bg-gray-100 text-gray-800'
//                   }`}>
//                     {analysisResult.risk_level?.toUpperCase() || 'Unknown'}
//                   </span>
//                 </p>
//                 <p><strong>Confidence:</strong> {Math.round((analysisResult.confidence || 0) * 100)}%</p>
//                 <p><strong>Compliance Required:</strong> {analysisResult.needs_compliance_logic ? 'Yes' : 'No'}</p>
//               </div>
//             </div>

//             <div>
//               <h3 className="text-lg font-semibold mb-2">Action Required</h3>
//               <p className="text-sm text-gray-700">{analysisResult.action_required || 'No specific action required'}</p>
//             </div>
//           </div>

//           {analysisResult.applicable_regulations && analysisResult.applicable_regulations.length > 0 && (
//             <div className="mt-6">
//               <h3 className="text-lg font-semibold mb-2">Applicable Regulations</h3>
//               <div className="space-y-2">
//                 {analysisResult.applicable_regulations.map((reg: any, index: number) => (
//                   <div key={index} className="flex items-center gap-2">
//                     <span className={`w-3 h-3 rounded-full ${
//                       reg.applies ? 'bg-green-500' : 'bg-gray-300'
//                     }`}></span>
//                     <span className="font-medium">{reg.name}</span>
//                     <span className="text-sm text-gray-600">- {reg.reason}</span>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           )}

//           {analysisResult.implementation_notes && analysisResult.implementation_notes.length > 0 && (
//             <div className="mt-6">
//               <h3 className="text-lg font-semibold mb-2">Implementation Notes</h3>
//               <ul className="list-disc list-inside space-y-1">
//                 {analysisResult.implementation_notes.map((note: string, index: number) => (
//                   <li key={index} className="text-sm text-gray-700">{note}</li>
//                 ))}
//               </ul>
//             </div>
//           )}

//           <div className="mt-6 text-xs text-gray-500">
//             Analysis completed at: {(() => {
//               try {
//                 const timestamp = analysisResult.timestamp;
//                 if (timestamp) {
//                   return new Date(timestamp).toLocaleString();
//                 }
//                 return new Date().toLocaleString();
//               } catch (error) {
//                 return new Date().toLocaleString();
//               }
//             })()}
//           </div>
//         </div>
//       )}
//     </FormRoot>
//   )
// }



"use client"
import { useState } from "react"
import { toast } from "@/hooks/use-toast"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Form as FormRoot,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
// import { Label } from "@/components/ui/label" // (unused)
import {Dropzone} from "@/components/ui/shadcn-io/dropzone"   // 👈 add this
import { buildApiUrl, API_CONFIG } from "@/config/api"

// ---- schema: add attachments (max 5 files, ≤10MB each) ----
const MAX_FILES = 5;
const MAX_MB = 10;

const fileSchema = z
  .instanceof(File)
  .refine(f => f.size <= MAX_MB * 1024 * 1024, `Each file must be ≤ ${MAX_MB}MB`);

const formSchema = z.object({
  featureName: z.string().min(1, "Feature name is required"),
  description: z.string().min(1, "Description is required"),
  attachments: z.array(fileSchema).max(MAX_FILES, `Max ${MAX_FILES} files`).optional(),
});

export function Form() {
  const [isLoading, setIsLoading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      featureName: "",
      description: "",
      attachments: [],
    },
  })

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      setIsLoading(true)
      setAnalysisResult(null)

      const hasFiles = Array.isArray(values.attachments) && values.attachments.length > 0
      let response: Response

      if (hasFiles) {
        // ---- multipart flow (featureName + description + files) ----
        const fd = new FormData()
        fd.append("featureName", values.featureName)
        fd.append("description", values.description)
        values.attachments!.forEach((file) => fd.append("files", file)) // adjust "files" to your BE field name

        response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), {
          method: "POST",
          body: fd, // 👈 no Content-Type header; browser sets boundary
        })
      } else {
        // ---- original JSON flow ----
        const requestBody = {
          featureName: values.featureName,
          description: values.description,
        }

        response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        })
      }

      if (!response.ok) throw new Error(`API request failed: ${response.status}`)
      const result = await response.json()

      if (result.status === "success" && result.analysis_results?.length > 0) {
        setAnalysisResult(result.analysis_results[0])
      } else {
        throw new Error("No analysis results received")
      }

      toast({
        title: "Analysis Complete!",
        description: `Compliance analysis completed for "${values.featureName}"`,
      })
    } catch (error) {
      console.error("Form submission error", error)
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to submit the form. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const attachments = form.watch("attachments") ?? []

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
                      placeholder="e.g., User Profile with Age Verification"
                      type="text"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Input
                  placeholder="Describe the feature and its functionality..."
                  type="text"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* ---- NEW: Attachments (Dropzone) ---- */}
        <FormField
          control={form.control}
          name="attachments"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Attachments (optional)</FormLabel>
              <FormDescription>PDFs, images, CSVs. Max {MAX_FILES} files, {MAX_MB}MB each.</FormDescription>
              <FormControl>
                <div>
                  <Dropzone
                    // If your Dropzone uses different props, switch here:
                    // onDrop={(accepted: File[]) => form.setValue("attachments", accepted, { shouldValidate: true })}
                    // files={attachments}
                    onFilesSelected={(accepted: File[]) =>
                      form.setValue("attachments", accepted, { shouldValidate: true })
                    }
                    value={attachments}
                    maxFiles={MAX_FILES}
                    accept={{
                      "image/*": [],
                      "application/pdf": [],
                      "text/csv": [],
                    }}
                  />
                  {/* Small preview list */}
                  {!!attachments.length && (
                    <ul className="mt-3 text-sm text-gray-700 space-y-1">
                      {attachments.map((f, i) => (
                        <li key={i} className="flex items-center justify-between">
                          <span className="truncate">{f.name}</span>
                          <span className="ml-2 text-xs text-gray-500">
                            {(f.size / (1024 * 1024)).toFixed(2)} MB
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Analyzing..." : "Analyze Compliance"}
        </Button>
      </form>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="mt-8 p-6 bg-slate-50 rounded-lg border">
          <h2 className="text-2xl font-bold mb-4">Compliance Analysis Results</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">Feature Details</h3>
              <div className="space-y-2">
                <p><strong>Name:</strong> {analysisResult.feature_name}</p>
                <p><strong>Risk Level:</strong>
                  <span className={`ml-2 px-2 py-1 rounded text-sm font-medium ${
                    analysisResult.risk_level === 'high' ? 'bg-red-100 text-red-800' :
                    analysisResult.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    analysisResult.risk_level === 'low' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {analysisResult.risk_level?.toUpperCase() || 'Unknown'}
                  </span>
                </p>
                <p><strong>Confidence:</strong> {Math.round((analysisResult.confidence || 0) * 100)}%</p>
                <p><strong>Compliance Required:</strong> {analysisResult.needs_compliance_logic ? 'Yes' : 'No'}</p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Action Required</h3>
              <p className="text-sm text-gray-700">{analysisResult.action_required || 'No specific action required'}</p>
            </div>
          </div>

          {analysisResult.applicable_regulations?.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">Applicable Regulations</h3>
              <div className="space-y-2">
                {analysisResult.applicable_regulations.map((reg: any, index: number) => (
                  <div key={index} className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${reg.applies ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span className="font-medium">{reg.name}</span>
                    <span className="text-sm text-gray-600">- {reg.reason}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {analysisResult.implementation_notes?.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">Implementation Notes</h3>
              <ul className="list-disc list-inside space-y-1">
                {analysisResult.implementation_notes.map((note: string, index: number) => (
                  <li key={index} className="text-sm text-gray-700">{note}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-6 text-xs text-gray-500">
            Analysis completed at: {new Date(analysisResult.timestamp || Date.now()).toLocaleString("en-SG", { timeZone: "Asia/Singapore" })}
          </div>
        </div>
      )}
    </FormRoot>
  )
}
