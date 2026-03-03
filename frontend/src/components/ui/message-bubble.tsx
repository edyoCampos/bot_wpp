"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

interface MessageBubbleProps extends React.HTMLAttributes<HTMLDivElement> {
  sender?: "user" | "other"
  message: string
  timestamp?: string
  senderName?: string
  senderInitials?: string
  unread?: boolean
}

export function MessageBubble({
  sender = "other",
  message,
  timestamp,
  senderName,
  senderInitials = "JD",
  unread = false,
  className,
  ...props
}: MessageBubbleProps) {
  const isUser = sender === "user"

  return (
    <div
      className={cn(
        "flex gap-3 items-start",
        isUser && "flex-row-reverse",
        className
      )}
      {...props}
    >
      {!isUser && (
        <Avatar className="size-8 shrink-0">
          <AvatarFallback className="text-xs">{senderInitials}</AvatarFallback>
        </Avatar>
      )}

      <div className={cn("flex flex-col gap-1 max-w-[70%]", isUser && "items-end")}>
        {!isUser && senderName && (
          <span className="text-xs font-medium text-muted-foreground px-1">
            {senderName}
          </span>
        )}

        <div
          className={cn(
            "px-4 py-2 rounded-2xl",
            isUser
              ? "bg-primary text-primary-foreground rounded-br-sm"
              : "bg-muted text-foreground rounded-bl-sm",
            unread && !isUser && "ring-2 ring-primary/50"
          )}
        >
          <p className="text-sm leading-relaxed">{message}</p>
        </div>

        {timestamp && (
          <span className="text-xs text-muted-foreground px-1">
            {timestamp}
          </span>
        )}
      </div>
    </div>
  )
}
