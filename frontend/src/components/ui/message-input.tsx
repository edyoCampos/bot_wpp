"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Paperclip, Send, Image, Smile } from "lucide-react"

interface MessageInputProps extends React.HTMLAttributes<HTMLDivElement> {
  onSend?: (message: string) => void
  placeholder?: string
  showAttachment?: boolean
  showImage?: boolean
  showEmoji?: boolean
  disabled?: boolean
}

export function MessageInput({
  onSend,
  placeholder = "Type a message...",
  showAttachment = true,
  showImage = false,
  showEmoji = false,
  disabled = false,
  className,
  ...props
}: MessageInputProps) {
  const [message, setMessage] = React.useState("")

  const handleSend = () => {
    if (message.trim() && onSend) {
      onSend(message)
      setMessage("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div
      className={cn(
        "flex items-end gap-2 p-4 border-t bg-background",
        className
      )}
      {...props}
    >
      <div className="flex gap-1">
        {showAttachment && (
          <Button
            variant="ghost"
            size="icon-sm"
            disabled={disabled}
            aria-label="Attach file"
          >
            <Paperclip className="size-4" />
          </Button>
        )}
        {showImage && (
          <Button
            variant="ghost"
            size="icon-sm"
            disabled={disabled}
            aria-label="Attach image"
          >
            <Image className="size-4" />
          </Button>
        )}
        {showEmoji && (
          <Button
            variant="ghost"
            size="icon-sm"
            disabled={disabled}
            aria-label="Add emoji"
          >
            <Smile className="size-4" />
          </Button>
        )}
      </div>

      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="min-h-[44px] max-h-32 resize-none"
        rows={1}
      />

      <Button
        onClick={handleSend}
        disabled={disabled || !message.trim()}
        size="icon"
        aria-label="Send message"
      >
        <Send className="size-4" />
      </Button>
    </div>
  )
}
