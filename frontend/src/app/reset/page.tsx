import { Suspense } from "react"
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { ResetPasswordForm } from "./ResetPasswordForm";

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background" data-testid="reset-page">
      <Card className="w-full max-w-md shadow-lg border rounded-2xl bg-card">
        <CardHeader>
          <h1 className="text-center text-2xl font-bold font-serif mb-2" data-testid="reset-title">Redefinir senha</h1>
        </CardHeader>
        <CardContent className="space-y-6">
          <Suspense fallback={<div className="flex justify-center p-4">Loading...</div>}>
            <ResetPasswordForm />
          </Suspense>
        </CardContent>
      </Card>
    </div>
  );
}
