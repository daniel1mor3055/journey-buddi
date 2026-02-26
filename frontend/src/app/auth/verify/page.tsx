"use client";

import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Compass, Loader2, AlertCircle } from "lucide-react";
import { useAuthStore } from "@/stores/auth-store";

function VerifyContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const verifyToken = useAuthStore((s) => s.verifyToken);
  const [verifyFailed, setVerifyFailed] = useState(false);
  const attemptedRef = useRef(false);

  const token = searchParams.get("token");

  const verify = useCallback(async (t: string) => {
    try {
      await verifyToken(t);
      router.replace("/dashboard");
    } catch {
      setVerifyFailed(true);
    }
  }, [verifyToken, router]);

  useEffect(() => {
    if (attemptedRef.current || !token) return;
    attemptedRef.current = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- async verification callback
    verify(token);
  }, [token, verify]);

  const hasError = !token || verifyFailed;
  const errorMessage = !token
    ? "No verification token found"
    : "Invalid or expired link. Please request a new one.";

  return (
    <div
      className="bg-cloud rounded-2xl p-8 w-full max-w-sm text-center"
      style={{ boxShadow: "0 4px 24px rgba(44,62,80,0.08)" }}
    >
      <div className="flex items-center justify-center gap-2 mb-6">
        <div className="w-10 h-10 rounded-full bg-forest flex items-center justify-center">
          <Compass className="text-white" size={22} />
        </div>
        <span className="text-bark text-xl font-bold">Journey Buddi</span>
      </div>

      {hasError ? (
        <>
          <div className="w-16 h-16 rounded-full bg-poor/10 flex items-center justify-center mx-auto mb-4">
            <AlertCircle size={28} className="text-poor" />
          </div>
          <h2 className="text-bark mb-2 text-lg font-semibold">
            Verification Failed
          </h2>
          <p className="text-stone text-sm mb-4">{errorMessage}</p>
          <a
            href="/auth"
            className="text-teal text-sm font-medium hover:underline"
          >
            Try again →
          </a>
        </>
      ) : (
        <>
          <Loader2
            size={32}
            className="animate-spin text-teal mx-auto mb-4"
          />
          <h2 className="text-bark mb-2 text-lg font-semibold">
            Verifying...
          </h2>
          <p className="text-stone text-sm">
            Signing you in to Journey Buddi
          </p>
        </>
      )}
    </div>
  );
}

export default function VerifyPage() {
  return (
    <div className="min-h-screen bg-mist flex items-center justify-center px-4">
      <Suspense
        fallback={
          <div className="text-center">
            <Loader2 size={32} className="animate-spin text-teal mx-auto mb-4" />
            <p className="text-stone text-sm">Loading...</p>
          </div>
        }
      >
        <VerifyContent />
      </Suspense>
    </div>
  );
}
