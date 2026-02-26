"use client";

import { useState } from "react";
import Link from "next/link";
import { Compass, Mail, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { useAuthStore } from "@/stores/auth-store";

export default function AuthPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const sendMagicLink = useAuthStore((s) => s.sendMagicLink);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email) return;

    setLoading(true);
    setError("");

    try {
      await sendMagicLink(email);
      setSent(true);
    } catch {
      setError("Failed to send magic link. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-mist relative flex items-center justify-center px-4">
      <motion.div
        className="relative z-10 w-full max-w-sm"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div
          className="bg-cloud rounded-2xl p-6"
          style={{ boxShadow: "0 4px 24px rgba(44,62,80,0.08)" }}
        >
          <div className="flex items-center justify-center gap-2 mb-6">
            <div className="w-10 h-10 rounded-full bg-forest flex items-center justify-center">
              <Compass className="text-white" size={22} />
            </div>
            <span className="text-bark text-xl font-bold">Journey Buddi</span>
          </div>

          {!sent ? (
            <>
              <h2 className="text-center text-bark mb-2 text-xl font-semibold">
                Sign in to continue
              </h2>
              <p className="text-center text-stone mb-6 text-sm">
                We&apos;ll send you a magic link — no password needed
              </p>

              <form onSubmit={handleSubmit}>
                <div className="relative mb-4">
                  <Mail
                    size={18}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-driftwood"
                  />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="w-full bg-sand rounded-xl pl-10 pr-4 py-3 text-bark placeholder:text-driftwood outline-none focus:ring-2 focus:ring-teal/30 text-[0.9375rem]"
                    required
                  />
                </div>

                {error && (
                  <p className="text-poor text-sm mb-3 text-center">{error}</p>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-teal text-white rounded-xl py-3 flex items-center justify-center gap-2 transition-all hover:shadow-md active:scale-[0.98] font-semibold disabled:opacity-60"
                >
                  {loading ? "Sending..." : "Send Magic Link"}
                  {!loading && <ArrowRight size={18} />}
                </button>
              </form>

              <p className="text-center text-driftwood mt-4 text-xs">
                By continuing, you agree to our Terms & Privacy Policy
              </p>
            </>
          ) : (
            <div className="text-center py-4">
              <div className="w-16 h-16 rounded-full bg-[#D4EDDA] flex items-center justify-center mx-auto mb-4">
                <Mail size={28} className="text-[#155724]" />
              </div>
              <h2 className="text-bark mb-2 text-xl font-semibold">
                Check your email
              </h2>
              <p className="text-stone mb-4 text-sm">
                We&apos;ve sent a magic link to{" "}
                <span className="text-bark font-medium">{email}</span>
              </p>
              <p className="text-driftwood text-xs">
                The link expires in 15 minutes
              </p>
            </div>
          )}
        </div>

        <Link
          href="/"
          className="block mx-auto mt-4 text-stone text-[0.8125rem] text-center"
        >
          ← Back to home
        </Link>
      </motion.div>
    </div>
  );
}
