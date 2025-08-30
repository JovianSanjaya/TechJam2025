"use client"
import React, { useMemo, useState, useEffect, useRef } from "react"
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
import { Dropzone, DropzoneContent, DropzoneEmptyState } from "@/components/ui/shadcn-io/dropzone"
import { Badge } from "@/components/ui/badge"
import { TooltipProvider } from "@/components/ui/tooltip"
import { buildApiUrl, API_CONFIG } from "@/config/api"
import { Loader2, ShieldAlert, CheckCircle2, Info, UploadCloud, FileText, Trash2, RefreshCw, Clipboard, Download, ChevronDown } from "lucide-react"
import { motion, useScroll, useTransform, useInView } from "framer-motion"
import Papa from "papaparse";

// -------------------- schema & types --------------------
const MAX_FILES = 5
const MAX_MB = 10

const fileSchema = z
  .instanceof(File)
  .refine((f) => f.size <= MAX_MB * 1024 * 1024, `Each file must be ≤ ${MAX_MB}MB`)

const baseSchema = z.object({
  featureName: z.string().optional().default(""),
  description: z.string().optional().default(""),
  attachments: z.array(fileSchema).max(MAX_FILES, `Max ${MAX_FILES} files`).optional(),
})

const formSchema = baseSchema.superRefine((data, ctx) => {
  const hasFiles = (data.attachments?.length ?? 0) > 0
  const hasText = !!data.featureName?.trim() && !!data.description?.trim()

  if (hasFiles && hasText) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["attachments"], message: "Submit either a CSV upload OR the text fields, not both." })
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["featureName"], message: "Clear the text fields when uploading CSV." })
  }
  if (!hasFiles && !hasText) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["featureName"], message: "Provide Feature name + Description or upload a CSV." })
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["description"], message: "Provide Feature name + Description or upload a CSV." })
  }
})

type Regulation = { name: string; applies: boolean; reason?: string }
export type AnalysisResult = {
  id?: string
  feature_name?: string
  risk_level?: "low" | "medium" | "high" | string
  confidence?: number
  needs_compliance_logic?: boolean
  action_required?: string
  applicable_regulations?: Regulation[]
  implementation_notes?: string[]
  timestamp?: string | number
}

// -------------------- helpers --------------------
function riskBadgeClasses(level?: string) {
  switch ((level || "").toLowerCase()) {
    case "high": return "bg-red-50 text-red-700 border border-red-200"
    case "medium": return "bg-yellow-50 text-yellow-700 border border-yellow-200"
    case "low": return "bg-green-50 text-green-700 border border-green-200"
    default: return "bg-gray-50 text-gray-700 border border-gray-200"
  }
}
function formatMB(bytes: number) {
  return (bytes / (1024 * 1024)).toFixed(2)
}
const LOGO_SRC: string = (import.meta as any)?.env?.VITE_LOGO_SRC ?? "/CanOrNotLogo.png"

// Normalize various header spellings
const H = {
  feature: ["feature_name", "feature name", "name", "feature"],
  desc: ["description", "desc", "details", "feature_description", "feature description"],
  id: ["id", "ID"],
}
const norm = (s: string) => s.trim().toLowerCase().replace(/[\s_-]+/g, "")

function pick(row: Record<string, any>, candidates: string[]) {
  const keys = Object.keys(row)
  const byNorm: Record<string, string> = {}
  for (const k of keys) byNorm[norm(k)] = k

  for (const c of candidates) {
    const n = norm(c)
    if (row[c] != null) return String(row[c])
    if (row[c.toLowerCase()] != null) return String(row[c.toLowerCase()])
    if (byNorm[n] && row[byNorm[n]] != null) return String(row[byNorm[n]])
  }
  return ""
}

// Parse CSV files → unified items array
async function normalizeUploadedCsvFiles(files: File[]) {
  const all: Array<{ feature_name: string; description: string; id?: string }> = []

  for (const f of files) {
    const text = await f.text()
    const { data, errors, meta } = Papa.parse<Record<string, any>>(text, {
      header: true,
      skipEmptyLines: "greedy",
      transformHeader: (h: any) => h.trim(),
    })

    if (errors?.length) {
      const msgs = errors.slice(0, 3).map((e: any) => `Row ${e.row}: ${e.message}`).join("; ")
      throw new Error(`CSV parse error in "${f.name}": ${msgs || "Unknown parse error"}`)
    }
    if (!meta?.fields || meta.fields.length === 0) {
      throw new Error(`"${f.name}" has no header row. Include headers like: feature_name, description, id`)
    }

    for (const row of data) {
      const feature_name = pick(row, H.feature)
      const description = pick(row, H.desc)
      const id = pick(row, H.id) || undefined
      if (feature_name && description) all.push({ feature_name, description, id })
    }
  }

  if (all.length === 0) {
    throw new Error("No valid rows with { feature_name, description } found in uploaded CSV.")
  }
  return all
}

// -------------------- typing animation component --------------------
function TypingAnimation({ text, delay = 0, speed = 50 }: { text: string; delay?: number; speed?: number }) {
  const [displayText, setDisplayText] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (currentIndex < text.length) {
        setDisplayText(prev => prev + text[currentIndex])
        setCurrentIndex(currentIndex + 1)
      }
    }, currentIndex === 0 ? delay : speed)

    return () => clearTimeout(timeout)
  }, [currentIndex, text, delay, speed])

  return (
    <span>
      {displayText}
      {currentIndex < text.length && (
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity, repeatType: "reverse" }}
          className="inline-block"
        >
          |
        </motion.span>
      )}
    </span>
  )
}

// -------------------- main component --------------------
function FormNotion() {
  const [isLoading, setIsLoading] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([])
  const [logoFailed, setLogoFailed] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const formRef = useRef<HTMLDivElement>(null)
  const heroRef = useRef<HTMLDivElement>(null)

  const { scrollYProgress } = useScroll()
  const y = useTransform(scrollYProgress, [0, 1], [0, -100])
  const opacity = useTransform(scrollYProgress, [0, 0.3], [1, 0])

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { featureName: "", description: "", attachments: [] },
    mode: "onBlur",
  })

  const attachments = form.watch("attachments") ?? []
  const totalSizeMB = useMemo(() => formatMB(attachments.reduce((s, f) => s + f.size, 0)), [attachments])

  // Show form after 3 seconds or when user scrolls
  useEffect(() => {
    const timer = setTimeout(() => setShowForm(true), 3000)
    
    const handleScroll = () => {
      if (window.scrollY > 100) {
        setShowForm(true)
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => {
      clearTimeout(timer)
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  const scrollToForm = () => {
    setShowForm(true)
    setTimeout(() => {
      formRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      setIsLoading(true)
      setAnalysisResults([])

      const hasFiles = (values.attachments?.length ?? 0) > 0
      let items: Array<{ feature_name: string; description: string; id?: string }>

      if (hasFiles) {
        items = await normalizeUploadedCsvFiles(values.attachments as File[])
      } else {
        items = [{
          feature_name: (values.featureName ?? "").trim(),
          description: (values.description ?? "").trim(),
        }]
      }

      const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.ANALYZE), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items }),
      })

      if (!response.ok) throw new Error(`API request failed: ${response.status}`)
      const result = await response.json()

      if (result.status === "success" && Array.isArray(result.analysis_results) && result.analysis_results.length > 0) {
        setAnalysisResults(result.analysis_results as AnalysisResult[])
      } else if (result.status === "success" && result.analysis_results) {
        setAnalysisResults([result.analysis_results as AnalysisResult])
      } else {
        throw new Error("No analysis results received")
      }

      toast({
        title: "Analysis complete",
        description: hasFiles
          ? `Processed ${items.length} item(s) from uploaded CSV.`
          : `Compliance analysis completed for "${items[0].feature_name}".`,
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
    setAnalysisResults([])
  }

  async function copyJson(payload: unknown) {
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2))
      toast({ title: "Copied", description: "JSON copied to clipboard." })
    } catch {
      toast({ title: "Copy failed", description: "Could not copy to clipboard.", variant: "destructive" })
    }
  }

  function downloadCsv(results: AnalysisResult[]) {
    try {
      // Prepare CSV data
      const csvData = results.map((result, index) => ({
        'Analysis_ID': index + 1,
        'Feature_ID': result.id || '',
        'Feature_Name': result.feature_name || '',
        'Risk_Level': result.risk_level || '',
        'Confidence': result.confidence ? Math.round(result.confidence * 100) + '%' : '',
        'Compliance_Required': result.needs_compliance_logic ? 'Yes' : 'No',
        'Action_Required': result.action_required || '',
        'Applicable_Regulations': result.applicable_regulations?.map(reg => `${reg.name}${reg.applies ? ' (applies)' : ' (not applicable)'}${reg.reason ? ` - ${reg.reason}` : ''}`).join('; ') || '',
        'Implementation_Notes': result.implementation_notes?.join('; ') || '',
        'Timestamp': new Date(result.timestamp || Date.now()).toISOString()
      }))

      // Convert to CSV using Papa Parse
      const csv = Papa.unparse(csvData)
      
      // Create and download file
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `compliance_analysis_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }

      toast({ 
        title: "Downloaded", 
        description: `CSV file with ${results.length} analysis result(s) downloaded successfully.` 
      })
    } catch (error) {
      console.error('CSV download error:', error)
      toast({ 
        title: "Download failed", 
        description: "Could not download CSV file.", 
        variant: "destructive" 
      })
    }
  }

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
        
        {/* Hero Section with Typing Animation */}
        <motion.div 
          ref={heroRef}
          className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden"
          style={{ y, opacity }}
        >
          {/* Animated Background Elements */}
          <motion.div
            className="absolute inset-0 opacity-5"
            animate={{
              backgroundPosition: ["0% 0%", "100% 100%"],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              repeatType: "reverse",
            }}
            style={{
              backgroundImage: "radial-gradient(circle, #3b82f6 1px, transparent 1px)",
              backgroundSize: "50px 50px",
            }}
          />

          {/* Logo */}
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-8"
          >
            {!logoFailed ? (
              <img 
                src={LOGO_SRC} 
                alt="Logo" 
                className="h-16 w-auto" 
                onError={() => setLogoFailed(true)} 
              />
            ) : (
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 text-white grid place-items-center font-bold text-2xl shadow-xl">
                CA
              </div>
            )}
          </motion.div>

          {/* Main Title with Typing Animation */}
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="text-center max-w-4xl mx-auto px-6"
          >
            <h1 className="text-6xl md:text-7xl font-bold mb-6">
              <span className="text-slate-800">Can</span>
              <span className="text-slate-600">Or</span>
              <span className="text-orange-500">Not</span>
            </h1>
            
            <div className="text-2xl md:text-3xl text-gray-600 font-light mb-8 h-20 flex items-center justify-center">
              <TypingAnimation 
                text="Automated compliance analysis for your features"
                delay={1500}
                speed={80}
              />
            </div>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 5, duration: 1 }}
              className="text-lg text-gray-500 mb-12 max-w-2xl mx-auto leading-relaxed"
            >
              Submit your features for geo-regulatory assessment and get detailed compliance insights powered by AI
            </motion.p>

            {/* CTA Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 6, duration: 0.8 }}
            >
              <Button
                onClick={scrollToForm}
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-lg rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 group"
              >
                Start Analysis
                <motion.div
                  animate={{ y: [0, 5, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="ml-2"
                >
                  <ChevronDown className="h-5 w-5" />
                </motion.div>
              </Button>
            </motion.div>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 7, duration: 1 }}
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="text-gray-400"
            >
              <ChevronDown className="h-6 w-6" />
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Form Section - Appears after animation or scroll */}
        {showForm && (
          <motion.div
            ref={formRef}
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="relative z-10"
          >
            {/* Sticky Header */}
            <div className="border-b border-gray-200/70 bg-white/90 backdrop-blur-md sticky top-0 z-20">
              <div className="max-w-4xl mx-auto px-6 py-4">
                <div className="flex items-center gap-3">
                  {!logoFailed ? (
                    <img src={LOGO_SRC} alt="Logo" className="h-7 w-auto" onError={() => setLogoFailed(true)} />
                  ) : (
                    <div className="h-7 w-7 rounded-lg bg-blue-50 text-blue-600 grid place-items-center font-semibold text-sm">CA</div>
                  )}
                  <h1 className="text-xl font-semibold text-gray-900">
                    <span className="text-slate-700">Can</span><span className="text-slate-500">Or</span><span className="text-orange-500">Not</span> <span className="text-gray-400 font-normal text-sm">v1.0</span>
                  </h1>
                </div>
              </div>
            </div>

            {/* Main Form Content */}
            <div className="max-w-3xl mx-auto px-6 py-12">
              {/* Page title */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                viewport={{ once: true }}
                className="mb-12"
              >
                <h1 className="text-4xl font-bold text-gray-900 mb-3">Compliance Analysis</h1>
                <p className="text-gray-600 text-lg leading-relaxed">Submit a feature for automated geo-regulatory assessment and get detailed compliance insights.</p>
              </motion.div>

              {/* Form container - Notion style with animation */}
              <motion.div
                initial={{ opacity: 0, y: 50, scale: 0.95 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                viewport={{ once: true }}
                className="bg-white border border-gray-200/70 rounded-xl shadow-sm hover:shadow-md transition-all duration-300"
              >
                <FormRoot {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="p-8 space-y-8">
                    
                    {/* Input method selection */}
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.6 }}
                      viewport={{ once: true }}
                      className="space-y-3"
                    >
                      <h2 className="text-xl font-semibold text-gray-900">Choose input method</h2>
                      <p className="text-gray-600">Use either manual input or CSV upload to analyze your features</p>
                    </motion.div>

                    {/* Manual input section */}
                    <motion.div
                      initial={{ opacity: 0, x: -50 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.6, delay: 0.1 }}
                      viewport={{ once: true }}
                      className="space-y-6 p-6 bg-blue-50/30 rounded-xl border border-blue-100/50"
                    >
            <FormRoot {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="p-8 space-y-8">
                
                {/* Input method selection */}
                <div className="space-y-3">
                  <h2 className="text-xl font-semibold text-gray-900">Choose input method</h2>
                  <p className="text-gray-600">Use either manual input or CSV upload to analyze your features</p>
                </div>

                {/* Manual input section */}
                <div className="space-y-6 p-6 bg-blue-50/30 rounded-xl border border-blue-100/50">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <h3 className="font-semibold text-gray-900">Manual Input</h3>
                  </div>
                  
                  <FormField
                    control={form.control}
                    name="featureName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium text-gray-700">Feature name</FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="e.g., Curfew login blocker" 
                            className="border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white shadow-sm h-11" 
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="description"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium text-gray-700">Description</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Describe the feature, who it affects, data flows, age-gating, regional behavior..."
                            className="min-h-[120px] border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white resize-none shadow-sm"
                            {...field}
                          />
                        </FormControl>
                        <FormDescription className="text-sm text-gray-500">
                          If you use these fields, leave the CSV upload empty.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                {/* Divider */}
                <div className="flex items-center gap-4">
                  <div className="flex-1 h-px bg-gray-200"></div>
                  <span className="text-sm text-gray-500 font-medium px-3 py-1 bg-gray-100 rounded-full">OR</span>
                  <div className="flex-1 h-px bg-gray-200"></div>
                </div>

                {/* CSV upload section */}
                <div className="space-y-6 p-6 bg-orange-50/30 rounded-xl border border-orange-100/50">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                    <h3 className="font-semibold text-gray-900">CSV Upload</h3>
                  </div>

                  <FormField
                    control={form.control}
                    name="attachments"
                    render={() => (
                      <FormItem>
                        <FormLabel className="text-sm font-medium text-gray-700">
                          Upload CSV files
                          <span className="text-gray-400 font-normal ml-2">(optional)</span>
                        </FormLabel>
                        <FormDescription className="text-sm text-gray-500 mb-4">
                          Flexible headers accepted (e.g., feature name, desc). Max {MAX_FILES} files • ≤ {MAX_MB}MB each • Total {totalSizeMB} MB
                        </FormDescription>
                        <FormControl>
                          <div>
                            <Dropzone
                              onDrop={(accepted: File[], fileRejections) => {
                                console.log("Files selected:", accepted);
                                console.log("File rejections:", fileRejections);
                                
                                if (fileRejections.length > 0) {
                                  fileRejections.forEach((rejection) => {
                                    console.error("File rejected:", rejection.file.name, rejection.errors);
                                    toast({
                                      title: "File rejected",
                                      description: `${rejection.file.name}: ${rejection.errors.map(e => e.message).join(", ")}`,
                                      variant: "destructive",
                                    });
                                  });
                                }
                                
                                if (accepted.length > 0) {
                                  form.setValue("attachments", accepted, { shouldValidate: true });
                                  toast({
                                    title: "Files uploaded",
                                    description: `${accepted.length} file(s) selected successfully`,
                                  });
                                }
                              }}
                              onError={(error) => {
                                console.error("Dropzone error:", error);
                                toast({
                                  title: "Upload error",
                                  description: error.message,
                                  variant: "destructive",
                                });
                              }}
                              src={attachments}
                              maxFiles={MAX_FILES}
                              maxSize={MAX_MB * 1024 * 1024}
                              accept={{ "text/csv": [".csv"], "application/vnd.ms-excel": [".csv"] }}
                              className="border-2 border-dashed border-gray-300 hover:border-gray-400 bg-white rounded-xl p-8 transition-colors group"
                            >
                              <DropzoneEmptyState />
                              <DropzoneContent />
                            </Dropzone>

                            {!!attachments.length && (
                              <div className="mt-4 space-y-3">
                                {attachments.map((f, i) => (
                                  <div key={i} className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
                                    <div className="flex items-center gap-3">
                                      <div className="p-2 bg-gray-50 rounded-lg">
                                        <FileText className="h-4 w-4 text-gray-600" />
                                      </div>
                                      <div>
                                        <span className="text-sm font-medium text-gray-900 block">{f.name}</span>
                                        <span className="text-xs text-gray-500">{formatMB(f.size)} MB</span>
                                      </div>
                                    </div>
                                    <Button 
                                      variant="ghost" 
                                      size="sm" 
                                      type="button" 
                                      onClick={() => handleRemoveFile(i)}
                                      className="text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg"
                                    >
                                      <Trash2 className="h-4 w-4" />
                                    </Button>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                {/* Action buttons */}
                <div className="flex items-center justify-between pt-6 border-t border-gray-100">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                  </div>

                  <div className="flex items-center gap-3">
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={handleClear} 
                      disabled={isLoading}
                      className="border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg h-10"
                    >
                      <RefreshCw className={cn("mr-2 h-4 w-4")} />
                      Reset
                    </Button>
                    <Button 
                      type="submit" 
                      disabled={isLoading}
                      className="bg-blue-600 hover:bg-blue-700 text-white border-0 shadow-sm rounded-lg h-10"
                    >
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
                </div>
              </form>
            </FormRoot>
          </div>

          {/* Results - Notion style */}
          {analysisResults.length > 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }} 
              animate={{ opacity: 1, y: 0 }} 
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="mt-12 space-y-6"
            >
              <div className="mb-8 flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Results</h2>
                  <p className="text-gray-600">Detailed compliance analysis for your features</p>
                </div>
                <Button
                  onClick={() => downloadCsv(analysisResults)}
                  variant="outline"
                  className="border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download All as CSV
                </Button>
              </div>

              {analysisResults.map((analysisResult, idx) => (
                <div key={idx} className="bg-white border border-gray-200/70 rounded-xl shadow-sm hover:shadow-md transition-all duration-300">
                  <div className="p-8">
                    <div className="flex items-start justify-between mb-6">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          Analysis #{idx + 1}
                          {analysisResult.id && <span className="text-gray-500 font-normal ml-2">• ID: {analysisResult.id}</span>}
                        </h3>
                        <p className="text-gray-600">{analysisResult.feature_name || "—"}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge className={cn("px-3 py-1 text-xs font-medium", riskBadgeClasses(analysisResult.risk_level))}>
                          {analysisResult.risk_level?.toUpperCase() || "UNKNOWN"} RISK
                        </Badge>
                        <Badge variant="secondary" className="px-3 py-1 text-xs bg-gray-100 text-gray-700">
                          {Math.round((analysisResult.confidence || 0) * 100)}% confidence
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
                      <div className="space-y-4">
                        <div>
                          <div className="text-sm font-medium text-gray-700 mb-1">Compliance required</div>
                          <div className="flex items-center gap-2">
                            {analysisResult.needs_compliance_logic ? (
                              <>
                                <CheckCircle2 className="h-4 w-4 text-green-600" />
                                <span className="text-sm text-green-700 font-medium">Yes</span>
                              </>
                            ) : (
                              <span className="text-sm text-gray-600">No</span>
                            )}
                          </div>
                        </div>
                      </div>

                      <div>
                        <div className="text-sm font-medium text-gray-700 mb-2">Action required</div>
                        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                          <p className="text-sm text-gray-700 leading-relaxed">
                            {analysisResult.action_required || "No specific action required."}
                          </p>
                        </div>
                      </div>
                    </div>

                    {!!analysisResult.applicable_regulations?.length && (
                      <div className="mb-6">
                        <div className="text-sm font-medium text-gray-700 mb-3">Applicable regulations</div>
                        <div className="flex flex-wrap gap-2">
                          {analysisResult.applicable_regulations.map((reg, i) => (
                            <Badge key={i} variant={reg.applies ? "default" : "secondary"} className="text-xs bg-blue-50 text-blue-700 border border-blue-200">
                              <span className={cn("inline-block h-2 w-2 rounded-full mr-2", reg.applies ? "bg-green-500" : "bg-gray-300")} />
                              {reg.name}
                              {reg.reason && <span className="ml-1 opacity-75">— {reg.reason}</span>}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {!!analysisResult.implementation_notes?.length && (
                      <div className="mb-6">
                        <div className="text-sm font-medium text-gray-700 mb-3">Implementation notes</div>
                        <ul className="space-y-2">
                          {analysisResult.implementation_notes.map((note, i) => (
                            <li key={i} className="flex items-start gap-3">
                              <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                              <span className="text-sm text-gray-700">{note}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-6 border-t border-gray-100">
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <Info className="h-3.5 w-3.5" />
                        {new Date(analysisResult.timestamp || Date.now()).toLocaleString("en-SG", { timeZone: "Asia/Singapore" })}
                      </div>
                      <div className="flex items-center gap-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          type="button" 
                          onClick={() => downloadCsv([analysisResult])}
                          className="text-xs border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg"
                        >
                          <Download className="mr-1.5 h-3.5 w-3.5" />
                          CSV
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline" 
                          type="button" 
                          onClick={() => copyJson(analysisResult)}
                          className="text-xs border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg"
                        >
                          <Clipboard className="mr-1.5 h-3.5 w-3.5" />
                          JSON
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </TooltipProvider>
  )
}

export default FormNotion
export { FormNotion }
