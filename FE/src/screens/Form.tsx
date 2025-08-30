

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
import { Dropzone, DropzoneContent, DropzoneEmptyState } from "@/components/ui/shadcn-io/dropzone"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { buildApiUrl, API_CONFIG } from "@/config/api"
import { Loader2, ShieldAlert, CheckCircle2, Info, UploadCloud, FileText, Trash2, RefreshCw, Clipboard } from "lucide-react"
import { motion } from "framer-motion"
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
    case "high": return "bg-red-100 text-red-800 border border-red-200"
    case "medium": return "bg-yellow-100 text-yellow-800 border border-yellow-200"
    case "low": return "bg-green-100 text-green-800 border border-green-200"
    default: return "bg-gray-100 text-gray-800 border border-gray-200"
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
  // Try exact, lower, normalized, etc.
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
      transformHeader: (h) => h.trim(),
    })

    if (errors?.length) {
      // keep first few to help debugging
      const msgs = errors.slice(0, 3).map(e => `Row ${e.row}: ${e.message}`).join("; ")
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

// -------------------- main component --------------------
function Form() {
  const [isLoading, setIsLoading] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([])
  const [logoFailed, setLogoFailed] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { featureName: "", description: "", attachments: [] },
    mode: "onBlur",
  })

  const attachments = form.watch("attachments") ?? []
  const totalSizeMB = useMemo(() => formatMB(attachments.reduce((s, f) => s + f.size, 0)), [attachments])

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      setIsLoading(true)
      setAnalysisResults([])

      const hasFiles = (values.attachments?.length ?? 0) > 0
      let items: Array<{ feature_name: string; description: string; id?: string }>

      if (hasFiles) {
        // CSV → JSON items[]
        items = await normalizeUploadedCsvFiles(values.attachments as File[])
      } else {
        // Single entry via text fields
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
        // in case backend returns single object
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

  return (
    <TooltipProvider>
      <div className="mx-auto max-w-4xl py-6 md:py-10">
        {/* Page heading */}
        <div className="mb-6 md:mb-8">
          <div className="flex items-center gap-3">
            {!logoFailed ? (
              <img src={LOGO_SRC} alt="Logo" className="h-8 w-auto" onError={() => setLogoFailed(true)} />
            ) : (
              <div className="h-8 w-8 rounded-md bg-primary/10 text-primary grid place-items-center font-semibold select-none">CA</div>
            )}
            <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">
              <span className="text-slate-700">Can</span><span className="text-slate-500">Or</span><span className="text-orange-500">Not</span> <span className="text-muted-foreground font-normal">v1.0</span>
            </h1>
          </div>
          <p className="text-muted-foreground mt-1">
            Submit a feature for automated geo-regulatory assessment.
          </p>
        </div>

        {/* Form card */}
        <div className="rounded-2xl">
          <Card className="rounded-2xl border-border/60 shadow-sm bg-background">
            <CardHeader className="pb-3">
              <CardTitle className="text-xl">Feature details</CardTitle>
              <CardDescription>
                Use <span className="font-medium">either</span> the text fields <span className="italic">or</span> upload a CSV with headers:
                <code className="ml-1">feature_name, description, id (optional)</code>.
              </CardDescription>
            </CardHeader>
            <Separator />

            <FormRoot {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <CardContent className="pt-6 space-y-6">
                  {/* Text mode */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <FormField
                      control={form.control}
                      name="featureName"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Feature name (single)</FormLabel>
                          <FormControl>
                            <Input placeholder="e.g., Curfew login blocker" type="text" {...field} />
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
                        <FormLabel>Description (single)</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Describe the feature, who it affects, data flows, age-gating, regional behavior..."
                            className="min-h-[110px]"
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>If you use these fields, leave the CSV upload empty.</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* CSV file mode */}
                  <FormField
                    control={form.control}
                    name="attachments"
                    render={() => (
                      <FormItem>
                        <div className="flex items-center justify-between">
                          <FormLabel>CSV Upload <span className="text-muted-foreground font-normal">(optional)</span></FormLabel>
                          <span className="text-xs text-muted-foreground">
                            Max {MAX_FILES} files • ≤ {MAX_MB}MB each • Total {totalSizeMB} MB
                          </span>
                        </div>
                        <FormDescription>
                          
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
                            >
                              <DropzoneEmptyState />
                              <DropzoneContent />
                            </Dropzone>

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
                   
                  </div>

                  <div className="flex items-center gap-2">
                    <Button type="button" variant="outline" onClick={handleClear} disabled={isLoading}>
                      <RefreshCw className={cn("mr-2 h-4 w-4")} />
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
        {analysisResults.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}>
            <div className="rounded-2xl">
              {analysisResults.map((analysisResult, idx) => (
                <Card key={idx} className="mt-8 rounded-2xl border-border/60 shadow-sm bg-background">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-xl">Compliance analysis #{idx + 1}</CardTitle>
                        <CardDescription></CardDescription>
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
                        {analysisResult.id && (
                          <div className="text-sm">
                            <div className="text-muted-foreground">ID</div>
                            <div className="font-medium">{analysisResult.id}</div>
                          </div>
                        )}
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
                          {analysisResult.applicable_regulations.map((reg, i) => (
                            <Badge key={i} variant={reg.applies ? "default" : "secondary"} className="whitespace-normal text-left">
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
                        <Button size="sm" variant="outline" type="button" onClick={() => copyJson(analysisResult)}>
                          <Clipboard className="mr-2 h-3.5 w-3.5" /> Copy JSON
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </TooltipProvider>
  )
}

export default Form
export { Form }
