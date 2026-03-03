import { ModeToggle } from "@/components/mode-toggle"

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="flex min-h-screen items-center justify-center bg-background relative">
            <div className="absolute top-6 right-6">
                <ModeToggle />
            </div>
            {children}
        </div>
    )
}
