"use client"

import { useState, useEffect } from "react"
import BackendStatus from "./BackendStatus"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, CheckCircle2, Info, AlertTriangle } from "lucide-react"

export default function StyleguidePage() {
  const [isDark, setIsDark] = useState(false)
  const [mounted, setMounted] = useState(false)

  // Avoid hydration errors by only rendering theme-dependent content after mount
  useEffect(() => {
    setMounted(true)
    // Check if dark mode is already enabled
    setIsDark(document.documentElement.classList.contains("dark"))
  }, [])

  const toggleDarkMode = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle("dark")
  }

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <div className="p-8 max-w-7xl mx-auto">
        <div className="h-screen flex items-center justify-center">
          <div className="animate-pulse text-muted-foreground">Loading...</div>
        </div>
      </div>
    )
  }

  const colorPalette = [
    { name: "Background", var: "--background", description: "Page background" },
    { name: "Foreground", var: "--foreground", description: "Main text color" },
    { name: "Card", var: "--card", description: "Card background" },
    { name: "Card Foreground", var: "--card-foreground", description: "Card text" },
    { name: "Primary", var: "--primary", description: "Brand blue" },
    { name: "Primary Foreground", var: "--primary-foreground", description: "Text on primary" },
    { name: "Secondary", var: "--secondary", description: "Light grey background" },
    { name: "Secondary Foreground", var: "--secondary-foreground", description: "Text on secondary" },
    { name: "Muted", var: "--muted", description: "Muted background" },
    { name: "Muted Foreground", var: "--muted-foreground", description: "Muted text" },
    { name: "Destructive", var: "--destructive", description: "Error/danger color" },
    { name: "Destructive Foreground", var: "--destructive-foreground", description: "Text on destructive" },
    { name: "Border", var: "--border", description: "Default border color" },
    { name: "Input", var: "--input", description: "Input border color" },
    { name: "Ring", var: "--ring", description: "Focus ring color" },
  ]

  const semanticColors = [
    { name: "Success", var: "--success", fg: "--success-foreground", description: "Success states" },
    { name: "Warning", var: "--warning", fg: "--warning-foreground", description: "Warning states" },
    { name: "Info", var: "--info", fg: "--info-foreground", description: "Info states" },
  ]

  const chartColors = [
    { name: "Chart 1", var: "--chart-1" },
    { name: "Chart 2", var: "--chart-2" },
    { name: "Chart 3", var: "--chart-3" },
    { name: "Chart 4", var: "--chart-4" },
    { name: "Chart 5", var: "--chart-5" },
  ]

  const radiiSizes = [
    { name: "Small", class: "rounded-sm", var: "--radius-sm" },
    { name: "Medium", class: "rounded-md", var: "--radius-md" },
    { name: "Large", class: "rounded-lg", var: "--radius-lg" },
    { name: "Extra Large", class: "rounded-xl", var: "--radius-xl" },
    { name: "2XL", class: "rounded-2xl", var: "--radius-2xl" },
    { name: "3XL", class: "rounded-3xl", var: "--radius-3xl" },
  ]

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-12">
      {/* Backend status */}
      <div className="mb-4">
        <BackendStatus />
      </div>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">Design Tokens</h1>
          <p className="text-muted-foreground">
            Complete design system for Go
          </p>
        </div>
        <Button onClick={toggleDarkMode} variant="outline" data-testid="styleguide-theme-toggle">
          {isDark ? "☀️ Light Mode" : "🌙 Dark Mode"}
        </Button>
      </div>

      {/* Color Palette */}
      <section>
        <h2 className="text-3xl font-bold mb-6">Color Palette</h2>

        <div className="space-y-8">
          <div>
            <h3 className="text-xl font-semibold mb-4">Base Colors</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {colorPalette.map((color) => (
                <Card key={color.var}>
                  <CardContent className="p-4">
                    <div
                      className="w-full h-24 rounded-lg mb-3 border"
                      style={{ background: `var(${color.var})` }}
                    />
                    <p className="font-medium">{color.name}</p>
                    <p className="text-xs text-muted-foreground font-mono">{color.var}</p>
                    <p className="text-sm text-muted-foreground mt-1">{color.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold mb-4">Semantic Colors</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {semanticColors.map((color) => (
                <Card key={color.var}>
                  <CardContent className="p-4">
                    <div
                      className="w-full h-24 rounded-lg mb-3 border flex items-center justify-center text-lg font-semibold"
                      style={{
                        background: `var(${color.var})`,
                        color: `var(${color.fg})`
                      }}
                    >
                      {color.name}
                    </div>
                    <p className="font-medium">{color.name}</p>
                    <p className="text-xs text-muted-foreground font-mono">{color.var}</p>
                    <p className="text-sm text-muted-foreground mt-1">{color.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold mb-4">Chart Colors</h3>
            <div className="grid grid-cols-5 gap-4">
              {chartColors.map((color) => (
                <Card key={color.var}>
                  <CardContent className="p-4">
                    <div
                      className="w-full h-20 rounded-lg mb-2 border"
                      style={{ background: `var(${color.var})` }}
                    />
                    <p className="font-medium text-sm">{color.name}</p>
                    <p className="text-xs text-muted-foreground font-mono">{color.var}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Typography */}
      <section>
        <h2 className="text-3xl font-bold mb-6">Typography</h2>
        <Card>
          <CardContent className="p-6 space-y-6">
            <div>
              <p className="text-sm text-muted-foreground mb-2">Font Family: Lora (Headings)</p>
              <h1 className="text-5xl font-bold mb-2">The quick brown fox</h1>
              <p className="text-muted-foreground font-mono text-xs">font-family: var(--font-lora)</p>
            </div>

            <div>
              <p className="text-sm text-muted-foreground mb-2">Font Family: Geist (Body)</p>
              <p className="text-lg">The quick brown fox jumps over the lazy dog</p>
              <p className="text-muted-foreground font-mono text-xs">font-family: var(--font-geist)</p>
            </div>

            <div className="space-y-3 pt-4 border-t">
              <h1 className="text-5xl">Heading 1</h1>
              <h2 className="text-4xl">Heading 2</h2>
              <h3 className="text-3xl">Heading 3</h3>
              <h4 className="text-2xl">Heading 4</h4>
              <h5 className="text-xl">Heading 5</h5>
              <h6 className="text-lg">Heading 6</h6>
              <p className="text-base">Body text - Regular paragraph</p>
              <p className="text-sm">Small text - Secondary information</p>
              <p className="text-xs">Extra small text - Captions</p>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Border Radius */}
      <section>
        <h2 className="text-3xl font-bold mb-6">Border Radius</h2>
        <Card>
          <CardContent className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              {radiiSizes.map((radius) => (
                <div key={radius.var} className="text-center">
                  <div
                    className={`w-24 h-24 mx-auto mb-3 bg-primary ${radius.class}`}
                  />
                  <p className="font-medium">{radius.name}</p>
                  <p className="text-xs text-muted-foreground font-mono">{radius.class}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Shadows */}
      <section>
        <h2 className="text-3xl font-bold mb-6">Shadows</h2>
        <Card>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-3 bg-card border rounded-lg shadow-sm" />
                <p className="font-medium">Small</p>
                <p className="text-xs text-muted-foreground">shadow-sm</p>
              </div>
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-3 bg-card border rounded-lg shadow-md" />
                <p className="font-medium">Medium</p>
                <p className="text-xs text-muted-foreground">shadow-md</p>
              </div>
              <div className="text-center">
                <div className="w-32 h-32 mx-auto mb-3 bg-card border rounded-lg shadow-lg" />
                <p className="font-medium">Large</p>
                <p className="text-xs text-muted-foreground">shadow-lg</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Components Preview */}
      <section>
        <h2 className="text-3xl font-bold mb-6">Component Examples</h2>

        <div className="space-y-6">
          {/* Buttons */}
          <Card>
            <CardHeader>
              <CardTitle>Buttons</CardTitle>
              <CardDescription>Button component with different variants</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-4">
              <Button>Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="link">Link</Button>
              <Button disabled>Disabled</Button>
            </CardContent>
          </Card>

          {/* Badges */}
          <Card>
            <CardHeader>
              <CardTitle>Badges</CardTitle>
              <CardDescription>Badge component with different variants</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-4">
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="destructive">Destructive</Badge>
              <Badge className="bg-success text-success-foreground">Success</Badge>
              <Badge className="bg-warning text-warning-foreground">Warning</Badge>
              <Badge className="bg-info text-info-foreground">Info</Badge>
            </CardContent>
          </Card>

          {/* Alerts */}
          <Card>
            <CardHeader>
              <CardTitle>Alerts</CardTitle>
              <CardDescription>Alert component with semantic meanings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>Information</AlertTitle>
                <AlertDescription>
                  This is an informational alert message.
                </AlertDescription>
              </Alert>

              <Alert className="border-success/50 text-success">
                <CheckCircle2 className="h-4 w-4" />
                <AlertTitle>Success</AlertTitle>
                <AlertDescription>
                  Your changes have been saved successfully.
                </AlertDescription>
              </Alert>

              <Alert className="border-warning/50 text-warning">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Warning</AlertTitle>
                <AlertDescription>
                  Please review the information before proceeding.
                </AlertDescription>
              </Alert>

              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>
                  An error occurred while processing your request.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          {/* Cards */}
          <Card>
            <CardHeader>
              <CardTitle>Cards</CardTitle>
              <CardDescription>Card component for grouping content</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Card Title</CardTitle>
                    <CardDescription>Card description goes here</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">This is the card content area.</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Another Card</CardTitle>
                    <CardDescription>With some content</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">Cards can contain any content.</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle>Third Card</CardTitle>
                    <CardDescription>Example card</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm">Consistent styling across all cards.</p>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}
