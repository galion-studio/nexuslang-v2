#!/bin/bash
# ============================================
# Fix ALL Missing Files in Galion App
# ============================================

echo "🔧 FIXING ALL MISSING COMPONENTS"
echo "============================================"
echo ""

cd /nexuslang-v2/galion-app || exit 1

# Step 1: Install critters (the main missing module)
echo "Step 1: Installing critters and dependencies..."
npm install critters --save-dev
npm install @radix-ui/react-avatar --silent
echo "✓ Core dependencies installed"
echo ""

# Step 2: Create missing UI components
echo "Step 2: Creating missing UI components..."
mkdir -p components/ui

# Avatar component
cat > components/ui/avatar.tsx << 'EOF'
"use client"

import * as React from "react"
import * as AvatarPrimitive from "@radix-ui/react-avatar"
import { cn } from "@/lib/utils"

const Avatar = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full",
      className
    )}
    {...props}
  />
))
Avatar.displayName = AvatarPrimitive.Root.displayName

const AvatarImage = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Image>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Image>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Image
    ref={ref}
    className={cn("aspect-square h-full w-full", className)}
    {...props}
  />
))
AvatarImage.displayName = AvatarPrimitive.Image.displayName

const AvatarFallback = React.forwardRef<
  React.ElementRef<typeof AvatarPrimitive.Fallback>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Fallback>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Fallback
    ref={ref}
    className={cn(
      "flex h-full w-full items-center justify-center rounded-full bg-muted",
      className
    )}
    {...props}
  />
))
AvatarFallback.displayName = AvatarPrimitive.Fallback.displayName

export { Avatar, AvatarImage, AvatarFallback }
EOF

echo "✓ Avatar component created"

# Step 3: Create AI components
echo "Step 3: Creating AI components..."
mkdir -p components/ai

cat > components/ai/ImageGenerator.tsx << 'EOF'
"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'

export function ImageGenerator() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [imageUrl, setImageUrl] = useState<string | null>(null)

  const generateImage = async () => {
    setLoading(true)
    try {
      // Placeholder for image generation
      // Will integrate with actual API later
      console.log('Generating image with prompt:', prompt)
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      setImageUrl('https://via.placeholder.com/512')
    } catch (error) {
      console.error('Error generating image:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6">
      <h2 className="text-2xl font-bold mb-4">AI Image Generator</h2>
      <div className="space-y-4">
        <Input
          placeholder="Enter your image prompt..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <Button onClick={generateImage} disabled={loading}>
          {loading ? 'Generating...' : 'Generate Image'}
        </Button>
        {imageUrl && (
          <div className="mt-4">
            <img src={imageUrl} alt="Generated" className="rounded-lg" />
          </div>
        )}
      </div>
    </Card>
  )
}
EOF

echo "✓ ImageGenerator component created"

# Step 4: Create lib files
echo "Step 4: Creating lib files..."
mkdir -p lib

cat > lib/openrouter.ts << 'EOF'
// OpenRouter API Client
export class OpenRouterClient {
  private apiKey: string
  private baseUrl = 'https://openrouter.ai/api/v1'

  constructor(apiKey?: string) {
    this.apiKey = apiKey || process.env.OPENROUTER_API_KEY || ''
  }

  async generateText(prompt: string, model = 'openai/gpt-3.5-turbo') {
    // Placeholder for OpenRouter integration
    console.log('OpenRouter request:', { prompt, model })
    return { text: 'Response from AI', model }
  }
}

export const openrouter = new OpenRouterClient()
EOF

cat > lib/comfyui.ts << 'EOF'
// ComfyUI API Client
export class ComfyUIClient {
  private baseUrl: string

  constructor(baseUrl = process.env.COMFYUI_URL || 'http://localhost:8188') {
    this.baseUrl = baseUrl
  }

  async generateImage(prompt: string) {
    // Placeholder for ComfyUI integration
    console.log('ComfyUI request:', { prompt })
    return { imageUrl: 'https://via.placeholder.com/512', prompt }
  }

  async getModels() {
    // Placeholder
    return ['sd_xl_base_1.0', 'sd_v1-5']
  }
}

export const comfyui = new ComfyUIClient()
EOF

echo "✓ API client files created"
echo ""

# Step 5: Clear cache and rebuild
echo "Step 5: Clearing caches..."
rm -rf .next node_modules/.cache
echo "✓ Caches cleared"
echo ""

# Step 6: Restart
echo "Step 6: Restarting service..."
pm2 delete galion-app 2>/dev/null || true
pm2 start npm --name galion-app -- run dev -- -p 3000
pm2 save
echo ""

# Step 7: Wait and test
echo "Step 7: Waiting 10 seconds..."
sleep 10
echo ""

# Step 8: Test
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)

echo "============================================"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCESS! Galion App is working!"
    echo "   HTTP Status: $HTTP_CODE"
    echo ""
    echo "🌐 Access at: http://213.173.105.83:3000"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "⚠ Still 500 error."
    echo ""
    echo "Remaining errors (last 20 lines):"
    pm2 logs galion-app --lines 20 --nostream --err
else
    echo "Status: HTTP $HTTP_CODE"
fi
echo "============================================"
echo ""

pm2 status

