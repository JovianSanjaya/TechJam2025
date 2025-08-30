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

















// "use client"
// import { useState } from "react"
// import { toast } from "@/hooks/use-toast"
// import { useForm } from "react-hook-form"
// import { zodResolver } from "@hookform/resolvers/zod"
// import { z } from "zod"
// import { cn } from "@/lib/utils"
// import { Button } from "@/components/ui/button"
// import {
//   Form as FormRoot,
//   FormControl,
//   FormDescription,
//   FormField,
//   FormItem,
//   FormLabel,
//   FormMessage,
// } from "@/components/ui/form"
// import { Input } from "@/components/ui/input"
// // import { Label } from "@/components/ui/label" // (unused)
// import {Dropzone} from "@/components/ui/shadcn-io/dropzone"   // 👈 add this
// import { buildApiUrl, API_CONFIG } from "@/config/api"

// // ---- schema: add attachments (max 5 files, ≤10MB each) ----
// const MAX_FILES = 5;
// const MAX_MB = 10;

// const fileSchema = z
//   .instanceof(File)
//   .refine(f => f.size <= MAX_MB * 1024 * 1024, `Each file must be ≤ ${MAX_MB}MB`);

// const formSchema = z.object({
//   featureName: z.string().min(1, "Feature name is required"),
//   description: z.string().min(1, "Description is required"),
//   attachments: z.array(fileSchema).max(MAX_FILES, `Max ${MAX_FILES} files`).optional(),
// });

// export function Form() {
//   const [isLoading, setIsLoading] = useState(false)
//   const [analysisResult, setAnalysisResult] = useState<any>(null)

//   const form = useForm<z.infer<typeof formSchema>>({
//     resolver: zodResolver(formSchema),
//     defaultValues: {
//       featureName: "",
//       description: "",
//       attachments: [],
//     },
//   })

//   async function onSubmit(values: z.infer<typeof formSchema>) {
//     try {
//       setIsLoading(true)
//       setAnalysisResult(null)

//       const hasFiles = Array.isArray(values.attachments) && values.attachments.length > 0
//       let response: Response

//       if (hasFiles) {
//         // ---- multipart flow (featureName + description + files) ----
//         const fd = new FormData()
//         fd.append("featureName", values.featureName)
//         fd.append("description", values.description)
//         values.attachments!.forEach((file) => fd.append("files", file)) // adjust "files" to your BE field name

//         response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), {
//           method: "POST",
//           body: fd, // 👈 no Content-Type header; browser sets boundary
//         })
//       } else {
//         // ---- original JSON flow ----
//         const requestBody = {
//           featureName: values.featureName,
//           description: values.description,
//         }

//         response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify(requestBody),
//         })
//       }

//       if (!response.ok) throw new Error(`API request failed: ${response.status}`)
//       const result = await response.json()

//       if (result.status === "success" && result.analysis_results?.length > 0) {
//         setAnalysisResult(result.analysis_results[0])
//       } else {
//         throw new Error("No analysis results received")
//       }

//       toast({
//         title: "Analysis Complete!",
//         description: `Compliance analysis completed for "${values.featureName}"`,
//       })
//     } catch (error) {
//       console.error("Form submission error", error)
//       toast({
//         title: "Error",
//         description:
//           error instanceof Error ? error.message : "Failed to submit the form. Please try again.",
//         variant: "destructive",
//       })
//     } finally {
//       setIsLoading(false)
//     }
//   }

//   const attachments = form.watch("attachments") ?? []

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

//         {/* ---- NEW: Attachments (Dropzone) ---- */}
//         <FormField
//           control={form.control}
//           name="attachments"
//           render={({ field }) => (
//             <FormItem>
//               <FormLabel>Attachments (optional)</FormLabel>
//               <FormDescription>PDFs, images, CSVs. Max {MAX_FILES} files, {MAX_MB}MB each.</FormDescription>
//               <FormControl>
//                 <div>
//                   <Dropzone
//                     // If your Dropzone uses different props, switch here:
//                     // onDrop={(accepted: File[]) => form.setValue("attachments", accepted, { shouldValidate: true })}
//                     // files={attachments}
//                     onFilesSelected={(accepted: File[]) =>
//                       form.setValue("attachments", accepted, { shouldValidate: true })
//                     }
//                     value={attachments}
//                     maxFiles={MAX_FILES}
//                     accept={{
//                       "image/*": [],
//                       "application/pdf": [],
//                       "text/csv": [],
//                     }}
//                   />
//                   {/* Small preview list */}
//                   {!!attachments.length && (
//                     <ul className="mt-3 text-sm text-gray-700 space-y-1">
//                       {attachments.map((f, i) => (
//                         <li key={i} className="flex items-center justify-between">
//                           <span className="truncate">{f.name}</span>
//                           <span className="ml-2 text-xs text-gray-500">
//                             {(f.size / (1024 * 1024)).toFixed(2)} MB
//                           </span>
//                         </li>
//                       ))}
//                     </ul>
//                   )}
//                 </div>
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

//           {analysisResult.applicable_regulations?.length > 0 && (
//             <div className="mt-6">
//               <h3 className="text-lg font-semibold mb-2">Applicable Regulations</h3>
//               <div className="space-y-2">
//                 {analysisResult.applicable_regulations.map((reg: any, index: number) => (
//                   <div key={index} className="flex items-center gap-2">
//                     <span className={`w-3 h-3 rounded-full ${reg.applies ? 'bg-green-500' : 'bg-gray-300'}`} />
//                     <span className="font-medium">{reg.name}</span>
//                     <span className="text-sm text-gray-600">- {reg.reason}</span>
//                   </div>
//                 ))}
//               </div>
//             </div>
//           )}

//           {analysisResult.implementation_notes?.length > 0 && (
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
//             Analysis completed at: {new Date(analysisResult.timestamp || Date.now()).toLocaleString("en-SG", { timeZone: "Asia/Singapore" })}
//           </div>
//         </div>
//       )}
//     </FormRoot>
//   )
// }












"use client"
import React, { useMemo, useState } from "react"
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
import { Textarea } from "@/components/ui/textarea"
import { Dropzone } from "@/components/ui/shadcn-io/dropzone"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { buildApiUrl, API_CONFIG } from "@/config/api"
import { Loader2, ShieldAlert, CheckCircle2, Info, UploadCloud, FileText, Trash2, RefreshCw, Clipboard } from "lucide-react"
import { motion } from "framer-motion"

// -------------------- schema & types --------------------
const MAX_FILES = 5
const MAX_MB = 10

const fileSchema = z
  .instanceof(File)
  .refine((f) => f.size <= MAX_MB * 1024 * 1024, `Each file must be ≤ ${MAX_MB}MB`)

const formSchema = z.object({
  featureName: z.string().min(1, "Feature name is required"),
  description: z.string().min(1, "Description is required"),
  attachments: z.array(fileSchema).max(MAX_FILES, `Max ${MAX_FILES} files`).optional(),
})

// Response shape from your backend (adjust as needed)
type Regulation = { name: string; applies: boolean; reason?: string }
export type AnalysisResult = {
  feature_name?: string
  risk_level?: "low" | "medium" | "high" | string
  confidence?: number // 0..1
  needs_compliance_logic?: boolean
  action_required?: string
  applicable_regulations?: Regulation[]
  implementation_notes?: string[]
  timestamp?: string | number
}

// -------------------- helpers --------------------
function riskBadgeClasses(level?: string) {
  switch ((level || "").toLowerCase()) {
    case "high":
      return "bg-red-100 text-red-800 border border-red-200"
    case "medium":
      return "bg-yellow-100 text-yellow-800 border border-yellow-200"
    case "low":
      return "bg-green-100 text-green-800 border border-green-200"
    default:
      return "bg-gray-100 text-gray-800 border border-gray-200"
  }
}

function formatMB(bytes: number) {
  return (bytes / (1024 * 1024)).toFixed(2)
}

// -------------------- branding --------------------
const LOGO_SRC: string = (import.meta as any)?.env?.VITE_LOGO_SRC ?? "/logo.svg";

// -------------------- main component --------------------
function Form() {
  const [isLoading, setIsLoading] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [logoFailed, setLogoFailed] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { featureName: "", description: "", attachments: [] },
  })

  const attachments = form.watch("attachments") ?? []
  const totalSizeMB = useMemo(() => formatMB(attachments.reduce((s, f) => s + f.size, 0)), [attachments])

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      setIsLoading(true)
      setAnalysisResult(null)

      const hasFiles = Array.isArray(values.attachments) && values.attachments.length > 0
      let response: Response

      if (hasFiles) {
        const fd = new FormData()
        fd.append("featureName", values.featureName)
        fd.append("description", values.description)
        values.attachments!.forEach((file) => fd.append("files", file))

        response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), {
          method: "POST",
          body: fd, // browser sets Content-Type with boundary automatically
        })
      } else {
        const requestBody = { featureName: values.featureName, description: values.description }
        response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        })
      }

      if (!response.ok) throw new Error(`API request failed: ${response.status}`)
      const result = await response.json()

      if (result.status === "success" && result.analysis_results?.length > 0) {
        setAnalysisResult(result.analysis_results[0] as AnalysisResult)
      } else {
        throw new Error("No analysis results received")
      }

      toast({
        title: "Analysis complete",
        description: `Compliance analysis completed for "${values.featureName}"`,
      })
    } catch (error) {
      console.error("Form submission error", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to submit the form. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  function handleRemoveFile(index: number) {
    const arr = [...(attachments || [])]
    arr.splice(index, 1)
    form.setValue("attachments", arr, { shouldValidate: true })
  }

  function handleClear() {
    form.reset({ featureName: "", description: "", attachments: [] })
    setAnalysisResult(null)
  }

  async function copyJson() {
    if (!analysisResult) return
    try {
      await navigator.clipboard.writeText(JSON.stringify(analysisResult, null, 2))
      toast({ title: "Copied", description: "Analysis JSON copied to clipboard." })
    } catch {
      toast({ title: "Copy failed", description: "Could not copy to clipboard.", variant: "destructive" })
    }
  }

  return (
    <TooltipProvider>
      
      <div className="mx-auto max-w-4xl py-6 md:py-10">
        {/* Page heading */}
        <div className="mb-6 md:mb-8">
          <div className="flex items-center gap-3">
            {!logoFailed ? (
              <img src={"../public/CanOrNotLogo.png"} alt="Logo" className="h-8 w-auto" onError={() => setLogoFailed(true)} />
            ) : (
              <div className="h-8 w-8 rounded-md bg-primary/10 text-primary grid place-items-center font-semibold select-none">CA</div>
            )}
            <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Compliance Analyzer</h1>
          </div>
          <p className="text-muted-foreground mt-1">Submit a feature for automated geo‑regulatory assessment.</p>
        </div>

        {/* Form card */}
        <div className="rounded-2xl">
          <Card className="rounded-2xl border-border/60 shadow-sm bg-background">
            <CardHeader className="pb-3">
              <CardTitle className="text-xl">Feature details</CardTitle>
              <CardDescription>Provide a clear description and optionally attach artifacts (PRD, screenshots, CSVs).</CardDescription>
            </CardHeader>
            <Separator />

            <FormRoot {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <CardContent className="pt-6 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="featureName"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Feature name</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g., Age‑gated Direct Messages" type="text" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="md:col-span-1" />
                  </div>

                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Description</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Describe the feature, who it affects, data flows, age‑gating, regional behavior..."
                            className="min-h-[110px]"
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>Be specific about user cohorts (e.g., EU minors), data processed, and toggles.</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="attachments"
                    render={() => (
                      <FormItem>
                        <div className="flex items-center justify-between">
                          <FormLabel>Attachments <span className="text-muted-foreground font-normal">(optional)</span></FormLabel>
                          <span className="text-xs text-muted-foreground">Max {MAX_FILES} files • ≤ {MAX_MB}MB each • Total {totalSizeMB} MB</span>
                        </div>
                        <FormDescription>PDFs, images, CSVs.</FormDescription>
                        <FormControl>
                          <div>
                            <Dropzone
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

                            {!!attachments.length && (
                              <ul className="mt-3 space-y-2">
                                {attachments.map((f, i) => (
                                  <li key={i} className="flex items-center justify-between rounded-md border bg-card p-2 text-sm">
                                    <div className="flex min-w-0 items-center gap-2">
                                      <FileText className="h-4 w-4 shrink-0" />
                                      <span className="truncate" title={f.name}>{f.name}</span>
                                      <span className="text-xs text-muted-foreground whitespace-nowrap">{formatMB(f.size)} MB</span>
                                    </div>
                                    <Tooltip>
                                      <TooltipTrigger asChild>
                                        <Button variant="ghost" size="icon" type="button" onClick={() => handleRemoveFile(i)} aria-label={`Remove ${f.name}`}>
                                          <Trash2 className="h-4 w-4" />
                                        </Button>
                                      </TooltipTrigger>
                                      <TooltipContent>Remove</TooltipContent>
                                    </Tooltip>
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
                </CardContent>

                <Separator />

                <CardFooter className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 justify-between">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <UploadCloud className="h-4 w-4" />
                    Files are uploaded securely over HTTPS.
                  </div>

                  <div className="flex items-center gap-2">
                    <Button type="button" variant="outline" onClick={handleClear} disabled={isLoading}>
                      <RefreshCw className={cn("mr-2 h-4 w-4", { "animate-spin": isLoading })} />
                      Reset
                    </Button>
                    <Button type="submit" disabled={isLoading}>
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Analyzing…
                        </>
                      ) : (
                        <>
                          <ShieldAlert className="mr-2 h-4 w-4" />
                          Analyze compliance
                        </>
                      )}
                    </Button>
                  </div>
                </CardFooter>
              </form>
            </FormRoot>
          </Card>
        </div>

        {/* Results */}
        {analysisResult && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
            <div className="rounded-2xl">
              <Card className="mt-8 rounded-2xl border-border/60 shadow-sm bg-background">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl">Compliance analysis results</CardTitle>
                      <CardDescription>Model output summarized with confidence and actions.</CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={cn("px-2.5 py-1 text-xs", riskBadgeClasses(analysisResult.risk_level))}>
                        Risk: {analysisResult.risk_level?.toUpperCase() || "UNKNOWN"}
                      </Badge>
                      <Badge variant="secondary" className="px-2.5 py-1 text-xs">
                        Confidence: {Math.round((analysisResult.confidence || 0) * 100)}%
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <Separator />
                <CardContent className="pt-6 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                      <div className="text-sm">
                        <div className="text-muted-foreground">Feature</div>
                        <div className="font-medium">{analysisResult.feature_name || "—"}</div>
                      </div>
                      <div className="text-sm">
                        <div className="text-muted-foreground">Compliance required</div>
                        <div className="font-medium flex items-center gap-1">
                          {analysisResult.needs_compliance_logic ? (
                            <>
                              <CheckCircle2 className="h-4 w-4 text-green-600" /> Yes
                            </>
                          ) : (
                            <>No</>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="text-sm text-muted-foreground">Action required</div>
                      <p className="text-sm leading-6 bg-muted/40 border rounded-md p-3">
                        {analysisResult.action_required || "No specific action required."}
                      </p>
                    </div>
                  </div>

                  {!!analysisResult.applicable_regulations?.length && (
                    <div>
                      <div className="text-sm text-muted-foreground mb-2">Applicable regulations</div>
                      <div className="flex flex-wrap gap-2">
                        {analysisResult.applicable_regulations.map((reg, idx) => (
                          <Badge key={idx} variant={reg.applies ? "default" : "secondary"} className="whitespace-normal text-left">
                            <span className={cn("inline-block h-2 w-2 rounded-full mr-2", reg.applies ? "bg-green-500" : "bg-gray-300")} />
                            {reg.name}
                            {reg.reason ? <span className="ml-1 text-xs opacity-80">— {reg.reason}</span> : null}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {!!analysisResult.implementation_notes?.length && (
                    <div>
                      <div className="text-sm text-muted-foreground mb-2">Implementation notes</div>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {analysisResult.implementation_notes.map((note, i) => (
                          <li key={i}>{note}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Info className="h-3.5 w-3.5" />
                      Analysis completed at: {new Date(analysisResult.timestamp || Date.now()).toLocaleString("en-SG", { timeZone: "Asia/Singapore" })}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="outline" type="button" onClick={copyJson}>
                        <Clipboard className="mr-2 h-3.5 w-3.5" /> Copy JSON
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}
      </div>
    </TooltipProvider>
  )
}



export default Form
export { Form }
