import { useState } from "react";
import { Link } from "@tanstack/react-router";
import {
  Calendar,
  CheckCircle2,
  ExternalLink,
  Lock,
  MessageCircle,
  Send,
  ShieldCheck,
  Sparkles,
  Star,
  X,
} from "lucide-react";
import { api, price, queryString, type Service } from "@/lib/local/api";
import { techAudio } from "@/lib/artisan-chat-engine";

interface ModernArtisanChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  service: Service;
}

export function ModernArtisanChatModal({
  isOpen,
  onClose,
  service,
}: ModernArtisanChatModalProps) {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const quickPrompts = [
    `Hi ${service.artisan_name || "there"}, are you available for an urgent job this week?`,
    `Could you provide an estimated quotation for ${service.title}?`,
    `Can we schedule an on-site inspection visit?`,
    `What materials should I prepare before you arrive?`,
  ];

  async function handleLaunchWhatsApp() {
    setError("");
    setBusy(true);
    techAudio.playClickBlip();
    try {
      const finalMsg = message.trim() || `Hi ${service.artisan_name || "there"}, I found your service "${service.title}" on Local Artisan and would like to inquire about availability.`;
      const result = await api<{ whatsapp_url: string }>(
        `/marketplace/listings/${service.id}/whatsapp?${queryString({ message: finalMsg })}`
      );
      const url = new URL(result.whatsapp_url);
      if (
        url.protocol !== "https:" ||
        !["wa.me", "api.whatsapp.com", "www.whatsapp.com", "web.whatsapp.com"].includes(
          url.hostname
        )
      ) {
        throw new Error("The contact link is not a valid WhatsApp address.");
      }
      techAudio.playSendBeep();
      window.open(url.href, "_blank", "noopener,noreferrer");
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Contact is currently unavailable.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="tech-modal-overlay" role="dialog" aria-modal="true" onClick={onClose}>
      <div
        className="tech-modal-card"
        onClick={(e) => e.stopPropagation()}
        aria-labelledby="tech-modal-title"
      >
        {/* Header */}
        <div className="tech-modal-header">
          <div className="flex items-center gap-2.5">
            <div className="size-9 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
              <MessageCircle className="size-5" />
            </div>
            <div>
              <h3 id="tech-modal-title" className="text-sm font-bold text-white flex items-center gap-1.5 m-0">
                Direct Artisan Gateway
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/30 text-emerald-300">
                  SECURE HUD
                </span>
              </h3>
              <p className="text-[11px] text-slate-400 m-0 flex items-center gap-1 font-mono">
                <Lock className="size-2.5 text-emerald-400" /> 256-bit WhatsApp Bridge
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="tech-chat-icon-btn"
            aria-label="Close modal"
          >
            <X className="size-4" />
          </button>
        </div>

        {/* Body */}
        <div className="tech-modal-body">
          {/* Artisan Identity HUD Banner */}
          <div className="tech-modal-artisan-banner">
            {service.artisan_photo_url ? (
              <img
                src={service.artisan_photo_url}
                alt={service.artisan_name || "Artisan"}
                className="tech-modal-avatar"
              />
            ) : (
              <div className="tech-modal-avatar bg-emerald-950 flex items-center justify-center text-emerald-400 font-bold text-lg">
                {(service.artisan_name || "A").slice(0, 2).toUpperCase()}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h4 className="text-sm font-bold text-white m-0 truncate">
                  {service.artisan_name || "Local Artisan"}
                </h4>
                {service.is_verified && (
                  <span className="inline-flex items-center gap-0.5 text-[11px] text-sky-400 font-medium">
                    <CheckCircle2 className="size-3.5 fill-sky-400 text-slate-900" />
                    Verified
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-300 font-semibold m-0 mt-0.5 truncate">
                {service.title}
              </p>
              <div className="flex flex-wrap items-center gap-2 mt-1.5 text-[11px] text-slate-400">
                <span className="font-mono text-emerald-400 font-bold">
                  {price(service)}
                </span>
                {service.average_rating && (
                  <span className="inline-flex items-center gap-1 text-amber-400 font-bold">
                    <Star className="size-3 fill-amber-400" />
                    {service.average_rating.toFixed(1)}
                  </span>
                )}
                {service.county_name && (
                  <span>
                    • {[service.county_name, service.sub_county_name].filter(Boolean).join(", ")}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Quick Prompts */}
          <div>
            <label className="text-xs font-semibold text-slate-300 mb-1.5 block flex items-center gap-1.5">
              <Sparkles className="size-3.5 text-cyan-400" />
              Quick Inquiries (Tap to insert)
            </label>
            <div className="tech-modal-prompt-chips">
              {quickPrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="tech-modal-prompt-chip"
                  onClick={() => {
                    techAudio.playClickBlip();
                    setMessage(prompt);
                  }}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Custom Message Field */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="modal-message-input" className="text-xs font-semibold text-slate-300">
                Custom Message to Artisan
              </label>
              <span className="text-[10px] font-mono text-slate-400">
                {message.length} / 500 chars
              </span>
            </div>
            <textarea
              id="modal-message-input"
              value={message}
              onChange={(e) => setMessage(e.target.value.slice(0, 500))}
              placeholder={`Write a message to ${service.artisan_name || "this artisan"} regarding your job details...`}
              className="tech-modal-textarea"
            />
          </div>

          {error && (
            <p className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/30 p-2.5 rounded-lg m-0 font-medium" role="alert">
              {error}
            </p>
          )}

          {/* Escrow Trust Guarantee */}
          <div className="flex items-center gap-2 p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-slate-300 text-xs">
            <ShieldCheck className="size-4 text-emerald-400 shrink-0" />
            <span>
              <strong>Local Artisan Escrow:</strong> Never make direct off-platform cash deposits. Payments are protected until task dispatch and completion.
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="tech-modal-footer">
          <Link
            to="/listing/$id"
            params={{ id: String(service.id) }}
            onClick={onClose}
            className="inline-flex items-center gap-1.5 text-xs text-slate-300 hover:text-white transition-colors"
          >
            <Calendar className="size-3.5 text-emerald-400" />
            <span>View Available Slots</span>
          </Link>

          <button
            type="button"
            disabled={busy}
            onClick={handleLaunchWhatsApp}
            className="tech-modal-launch-btn"
          >
            <Send className="size-4" />
            <span>{busy ? "Connecting..." : "Launch WhatsApp Chat"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
