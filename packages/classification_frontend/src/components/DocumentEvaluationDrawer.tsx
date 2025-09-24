"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { Label } from "@/components/ui/label"
import type { ReactNode } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from "@/components/ui/drawer"
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Document as PdfDocument, Page, pdfjs } from "react-pdf"
import { FieldDisplay } from "@/components/fieldDisplayer"
import "react-pdf/dist/Page/TextLayer.css"
import "react-pdf/dist/Page/AnnotationLayer.css"

pdfjs.GlobalWorkerOptions.workerSrc = "https://unpkg.com/pdfjs-dist@5.3.93/build/pdf.worker.min.mjs"

interface Document {
  evaluations: Record<string, unknown>
  url: string // do not change prop; internally we can accept a Blob via type coercion
}

interface DocumentEvaluationDrawerProps {
  isOpen: boolean
  onClose: () => void
  documents: Document[]
  applicationId: string
}

export function DocumentEvaluationDrawer({ isOpen, onClose, documents, applicationId }: DocumentEvaluationDrawerProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [numPages, setNumPages] = useState<number>(0)
  const [scale, setScale] = useState(0.75)

  const renderEvaluationValue = (value: unknown): ReactNode => {
    if (value == null) return "—"
    if (Array.isArray(value)) {
      if (value.length === 0) return "—"
      // If array of objects with consistent keys, render list
      if (typeof value[0] === "object" && value[0] !== null) {
        return (
          <div className="space-y-2">
            {(value as Array<Record<string, unknown>>).map((item, idx) => {
              const name = (item as any).name ?? Object.keys(item)[0]
              const amount = (item as any).amount ?? (name ? (item as any)[name] : undefined)
              return (
                <div key={idx} className="flex items-center justify-between rounded-md border px-3 py-2 text-sm">
                  <span className="text-muted-foreground">{String(name)}</span>
                  {amount !== undefined ? <span className="font-medium">{String(amount)}</span> : null}
                </div>
              )
            })}
          </div>
        )
      }
      // Primitive array
      return (
        <ul className="list-disc pl-5 space-y-1 text-sm">
          {(value as Array<unknown>).map((v, i) => (
            <li key={i}>{String(v)}</li>
          ))}
        </ul>
      )
    }
    if (typeof value === "object") {
      const entries = Object.entries(value as Record<string, unknown>)
      return (
        <div className="space-y-2">
          {entries.map(([k, v]) => (
            <div key={k} className="flex items-center justify-between rounded-md border px-3 py-2 text-sm">
              <span className="text-muted-foreground capitalize">{k.replace(/_/g, " ")}</span>
              <span className="font-medium">{String(v)}</span>
            </div>
          ))}
        </div>
      )
    }
    return String(value)
  }

  const objectUrlRef = useRef<string | null>(null)
  const fileUrl = useMemo(() => {
    const doc = documents?.[currentIndex] as any
    if (!doc) return null
    const base = process.env.NEXT_PUBLIC_FILE_BASE_URL
    const maybe = base ? `${base}/${doc.url}` : doc.url
    if (typeof maybe === "string") {
      return maybe
    }
    if (maybe instanceof Blob) {
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current)
      objectUrlRef.current = URL.createObjectURL(maybe)
      return objectUrlRef.current
    }
    return null
  }, [documents, currentIndex])

  const formatFileLabel = (filePathOrName: string): string => {
    const baseName = filePathOrName.split("/").pop() || filePathOrName
    const withoutExt = baseName.replace(/\.[^/.]+$/, "")
    const noUnderscores = withoutExt.replace(/_/g, " ")
    const removedLeadingNumbers = noUnderscores.replace(/^[\s\-]*\d+[\s\-]*/, "")
    const removedTrailingNumbers = removedLeadingNumbers.replace(/[\s\-]*\d+$/g, "")
    return removedTrailingNumbers.replace(/\s{2,}/g, " ").trim()
  }

  useEffect(() => {
    return () => {
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current)
    }
  }, [])

  const handleLoadSuccess = (info: { numPages: number }) => {
    setNumPages(info.numPages)
  }

  return (
    <Drawer open={isOpen} onOpenChange={onClose} direction="bottom">
      <DrawerContent className="max-h-[90vh]">
        <DrawerHeader>
          <DrawerTitle className="text-balance text-xl font-semibold">Evaluate documents</DrawerTitle>
          <p className="text-sm text-muted-foreground">{applicationId}</p>
        </DrawerHeader>

        {/* Main content */}
        <div className="flex-1 overflow-auto px-6 pb-6">
          <div className="grid gap-6 md:grid-cols-12">
            {/* LEFT: PDF preview + selector */}
            <section className="md:col-span-7 lg:col-span-6">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="font-medium truncate" >
                  Document preview
                </h3>
                <div className="flex items-center gap-2">
                  <div className="w-56">
                    <Label htmlFor="documentSelect" className="sr-only">
                      Select document
                    </Label>
                    <Select value={String(currentIndex)} onValueChange={(v) => setCurrentIndex(Number(v))}>
                      <SelectTrigger
                        id="documentSelect"
                        className="h-8 px-2 rounded-md border border-transparent bg-transparent hover:bg-accent/40 focus:ring-0 focus:ring-offset-0 data-[state=open]:bg-accent/50"
                        aria-label="Select document"
                      >
                        <SelectValue placeholder="Select document" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          {documents.map((doc, idx) => (
                            <SelectItem key={idx} value={String(idx)} title={doc.url}>
                              {formatFileLabel(doc.url)}
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="hidden md:flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => setScale((s) => Math.max(0.5, parseFloat((s - 0.1).toFixed(2))))}
                      aria-label="Zoom out"
                      className="inline-flex h-8 w-8 items-center justify-center rounded-md border text-sm"
                    >
                      −
                    </button>
                    <span className="mx-1 text-xs text-muted-foreground w-10 text-center">{Math.round(scale * 100)}%</span>
                    <button
                      type="button"
                      onClick={() => setScale((s) => Math.min(2, parseFloat((s + 0.1).toFixed(2))))}
                      aria-label="Zoom in"
                      className="inline-flex h-8 w-8 items-center justify-center rounded-md border text-sm"
                    >
                      +
                    </button>
                  </div>
                </div>
              </div>

              <div className="rounded-lg border bg-card">
                <div className="h-[600px] overflow-auto">
                  {fileUrl ? (
                    <div className="flex justify-center p-3">
                      <PdfDocument
                        file={fileUrl}
                        onLoadSuccess={handleLoadSuccess}
                        loading={<div className="text-sm text-muted-foreground">Loading PDF…</div>}
                      >
                        {Array.from({ length: numPages || 1 }, (_, idx) => (
                          <div key={idx} className="mb-4 last:mb-0">
                            <Page pageNumber={idx + 1} scale={scale} renderTextLayer renderAnnotationLayer />
                          </div>
                        ))}
                      </PdfDocument>
                    </div>
                  ) : (
                    <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                      No document selected
                    </div>
                  )}
                </div>
                <div className="flex items-center justify-center gap-2 border-t p-2 text-xs text-muted-foreground">
                  <span>Pages: {numPages || 0}</span>
                </div>
              </div>
            </section>

            {/* RIGHT: Dynamic evaluation fields for current document */}
            <section className="md:col-span-5 lg:col-span-6">
              <div className="grid gap-6">
                <div>
                  <h4 className="mb-3 text-sm font-medium text-muted-foreground">Extracted fields</h4>
                  <ScrollArea className="h-[600px] rounded-lg border">
                    <div className="p-4">
                      <div className="grid gap-4 md:grid-cols-2">
                        {Object.entries(documents?.[currentIndex]?.evaluations ?? {}).map(([key, value]) => (
                          <div key={key} className="space-y-2">
                            <Label className="text-sm font-medium capitalize">{key.replace(/_/g, " ")}</Label>
                            <FieldDisplay value={renderEvaluationValue(value)} lines={3} />
                          </div>
                        ))}
                      </div>
                    </div>
                  </ScrollArea>
                </div>
              </div>
            </section>
          </div>
        </div>


      </DrawerContent>
    </Drawer>
  )
}
