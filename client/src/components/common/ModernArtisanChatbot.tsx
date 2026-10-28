import { useEffect, useRef, useState } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import {
  Bot,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  MapPin,
  MessageCircle,
  Minus,
  RotateCcw,
  Send,
  Sparkles,
  Star,
  Volume2,
  VolumeX,
  X,
  Zap,
} from "lucide-react";
import {
  techAudio,
  processArtisanMessage,
  INITIAL_SUGGESTIONS,
  type ChatMessage,
} from "@/lib/artisan-chat-engine";
import { api, price, type Service } from "@/lib/local/api";

const CHAT_STORAGE_KEY = "local_artisan_tech_chat_v2";
const TEASER_DISMISSED_KEY = "local_artisan_teaser_dismissed";

const DEFAULT_WELCOME_MESSAGE: ChatMessage = {
  id: "welcome-01",
  sender: "bot",
  text: `👋 **Welcome to Local Artisan — AI Concierge!**\n\nI am your intelligent assistant for discovering vetted Kenyan craftspeople, booking open availability slots, and securing quotes.\n\n• **Emergency response**: 24/7 plumbers, electricians & mobile mechanics.\n• **Protected payments**: Secure M-Pesa milestone escrow.\n• **Vetted credentials**: National ID & Certificate of Good Conduct verification.\n\nHow can I assist you today?`,
  timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  suggestions: INITIAL_SUGGESTIONS,
};

export function ModernArtisanChatbot() {
  const routerState = useRouterState();
  const currentPath = routerState.location.pathname;

  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [showTeaser, setShowTeaser] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    if (typeof window === "undefined") return [DEFAULT_WELCOME_MESSAGE];
    try {
      const stored = sessionStorage.getItem(CHAT_STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {
      // Fallback
    }
    return [DEFAULT_WELCOME_MESSAGE];
  });
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [contextService, setContextService] = useState<Service | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sync sound settings with synthesizer
  useEffect(() => {
    techAudio.enabled = soundEnabled;
  }, [soundEnabled]);

  // Save conversation to session storage
  useEffect(() => {
    try {
      sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
    } catch {
      // Storage quota or private mode
    }
  }, [messages]);

  // Show teaser balloon after slight delay if not opened or dismissed
  useEffect(() => {
    if (sessionStorage.getItem(TEASER_DISMISSED_KEY)) return;
    const timer = setTimeout(() => {
      setShowTeaser(true);
    }, 2800);
    return () => clearTimeout(timer);
  }, []);

  // Detect if user is on a specific listing page to provide contextual HUD assistance
  useEffect(() => {
    const listingMatch = currentPath.match(/^\/listing\/([^/]+)$/);
    if (listingMatch && listingMatch[1]) {
      const id = listingMatch[1];
      api<Service>(`/marketplace/listings/${id}`)
        .then((svc) => setContextService(svc))
        .catch(() => setContextService(null));
    } else {
      setContextService(null);
    }
  }, [currentPath]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (isOpen && !isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isTyping, isOpen, isMinimized]);

  function handleToggleOpen() {
    techAudio.playClickBlip();
    if (!isOpen) {
      setIsOpen(true);
      setIsMinimized(false);
      setShowTeaser(false);
      sessionStorage.setItem(TEASER_DISMISSED_KEY, "true");
    } else if (isMinimized) {
      setIsMinimized(false);
    } else {
      setIsOpen(false);
    }
  }

  function handleDismissTeaser(e: React.MouseEvent) {
    e.stopPropagation();
    techAudio.playClickBlip();
    setShowTeaser(false);
    sessionStorage.setItem(TEASER_DISMISSED_KEY, "true");
  }

  function handleResetChat() {
    techAudio.playClickBlip();
    setMessages([
      {
        ...DEFAULT_WELCOME_MESSAGE,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  }

  async function handleSendMessage(textToSend?: string) {
    const content = (textToSend || inputText).trim();
    if (!content || isTyping) return;

    techAudio.playSendBeep();
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: content,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setIsTyping(true);

    try {
      // Small realistic cognitive processing pause
      await new Promise((r) => setTimeout(r, 650));
      const botResponse = await processArtisanMessage(content, {
        service: contextService || undefined,
        artisanName: contextService?.artisan_name,
      });

      techAudio.playReceiveChime();
      const botMsg: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: botResponse.text,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        services: botResponse.services,
        suggestions: botResponse.suggestions,
        actionLink: botResponse.actionLink,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch {
      const errMsg: ChatMessage = {
        id: `bot-err-${Date.now()}`,
        sender: "bot",
        text: "I encountered a minor network glitch connecting to the marketplace index. You can continue searching or browse the full directory directly.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        suggestions: ["🔧 Plumbers", "⚡ Electricians", "📅 Book a slot"],
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setIsTyping(false);
    }
  }

  // Find latest suggestions
  const latestBotMessage = [...messages].reverse().find((m) => m.sender === "bot");
  const activeSuggestions = latestBotMessage?.suggestions || INITIAL_SUGGESTIONS;

  return (
    <>
      {/* Floating Launcher and Teaser HUD */}
      {!isOpen && (
        <div className="tech-chat-launcher-root">
          {showTeaser && (
            <div
              className="tech-chat-teaser"
              onClick={handleToggleOpen}
              role="status"
              aria-live="polite"
            >
              <div className="size-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
                <Sparkles className="size-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="tech-chat-teaser-badge">
                  <Zap className="size-2.5" /> AI Fundi Concierge
                </div>
                <p className="tech-chat-teaser-text">
                  Need a reliable Kenyan fundi or urgent pricing quote? Tap to chat ⚡
                </p>
              </div>
              <button
                className="tech-chat-teaser-close"
                onClick={handleDismissTeaser}
                aria-label="Dismiss message"
              >
                <X className="size-3.5" />
              </button>
            </div>
          )}

          <button
            type="button"
            className="tech-chat-trigger-btn"
            onClick={handleToggleOpen}
            aria-label="Open AI Artisan Concierge"
            title="Chat with AI Artisan Concierge"
          >
            <div className="tech-chat-radar-ring" />
            <Bot className="size-7" />
            <div className="tech-chat-online-pill">
              <span className="tech-chat-online-dot" />
              AI 24/7
            </div>
          </button>
        </div>
      )}

      {/* Main Glassmorphic Chat Window */}
      {isOpen && (
        <div
          className={`tech-chat-window ${isMinimized ? "!h-auto !max-h-[64px]" : ""}`}
          role="complementary"
          aria-label="AI Artisan Concierge"
        >
          {/* Tech Header */}
          <div className="tech-chat-header">
            <div className="tech-chat-header-title-box">
              <div className="tech-chat-avatar-frame">
                <Bot className="size-5" />
              </div>
              <div>
                <h2 className="tech-chat-title-heading">
                  FundiBot AI
                  <span className="tech-chat-badge-version">v2.4 HUD</span>
                </h2>
                <div className="tech-chat-status-subline">
                  <span className="tech-chat-online-dot" />
                  <span>ONLINE | 24ms | KENYA CLOUD</span>
                </div>
              </div>
            </div>

            <div className="tech-chat-header-actions">
              <button
                type="button"
                className="tech-chat-icon-btn"
                onClick={() => {
                  techAudio.playClickBlip();
                  setSoundEnabled((prev) => !prev);
                }}
                title={soundEnabled ? "Mute cyber audio" : "Enable cyber audio"}
                aria-label="Toggle audio effects"
              >
                {soundEnabled ? <Volume2 className="size-4 text-emerald-400" /> : <VolumeX className="size-4" />}
              </button>

              <button
                type="button"
                className="tech-chat-icon-btn"
                onClick={handleResetChat}
                title="Reset conversation"
                aria-label="Reset conversation"
              >
                <RotateCcw className="size-3.5" />
              </button>

              <button
                type="button"
                className="tech-chat-icon-btn"
                onClick={() => {
                  techAudio.playClickBlip();
                  setIsMinimized((prev) => !prev);
                }}
                title={isMinimized ? "Expand chat" : "Minimize chat"}
                aria-label="Minimize or expand"
              >
                <Minus className="size-4" />
              </button>

              <button
                type="button"
                className="tech-chat-icon-btn"
                onClick={() => {
                  techAudio.playClickBlip();
                  setIsOpen(false);
                }}
                title="Close chat"
                aria-label="Close chat"
              >
                <X className="size-4" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Contextual Page HUD Banner if viewing a listing */}
              {contextService && (
                <div className="tech-chat-context-banner">
                  <div className="tech-chat-context-text">
                    <Zap className="size-3 text-cyan-400 shrink-0" />
                    <span>
                      Viewing: <strong>{contextService.title}</strong> by {contextService.artisan_name || "Artisan"}
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleSendMessage(`What are the rates and availability for ${contextService.title}?`)}
                    className="text-[10px] font-mono text-cyan-300 underline hover:text-white shrink-0 ml-2"
                  >
                    Ask Rates
                  </button>
                </div>
              )}

              {/* Message Feed */}
              <div className="tech-chat-messages-container">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={msg.sender === "user" ? "tech-msg-user-row" : "tech-msg-bot-row"}
                  >
                    <div
                      className={msg.sender === "user" ? "tech-msg-user-bubble" : "tech-msg-bot-bubble"}
                    >
                      <div className="whitespace-pre-line">{msg.text}</div>

                      {/* Embedded Artisan Cards Carousel */}
                      {msg.services && msg.services.length > 0 && (
                        <div className="tech-chat-cards-carousel">
                          {msg.services.map((svc) => (
                            <div key={svc.id} className="tech-chat-artisan-card">
                              <div className="tech-card-glow-bar" />
                              <div className="tech-chat-card-header">
                                {svc.artisan_photo_url ? (
                                  <img
                                    src={svc.artisan_photo_url}
                                    alt={svc.artisan_name || "Artisan"}
                                    className="tech-chat-card-photo"
                                  />
                                ) : (
                                  <div className="tech-chat-card-photo bg-emerald-950 flex items-center justify-center text-emerald-400 font-bold">
                                    {(svc.artisan_name || "A").slice(0, 2).toUpperCase()}
                                  </div>
                                )}
                                <div className="tech-chat-card-info">
                                  <div className="tech-chat-card-name">
                                    {svc.artisan_name || "Local Artisan"}
                                    {svc.is_verified && (
                                      <span title="Verified Artisan" className="inline-flex">
                                        <CheckCircle2
                                          className="size-3.5 fill-sky-400 text-slate-900 tech-chat-card-badge-verified"
                                        />
                                      </span>
                                    )}
                                  </div>
                                  <p className="tech-chat-card-specialty">
                                    {svc.specialty || "Verified Professional"}
                                  </p>
                                </div>
                              </div>

                              <p className="tech-chat-card-title">{svc.title}</p>

                              <div className="tech-chat-card-meta-row">
                                <span className="tech-chat-card-price-pill">
                                  {price(svc)}
                                </span>
                                {svc.average_rating ? (
                                  <span className="tech-chat-card-rating">
                                    <Star className="size-3 fill-amber-400" />
                                    {svc.average_rating.toFixed(1)}
                                    {svc.review_count ? ` (${svc.review_count})` : ""}
                                  </span>
                                ) : (
                                  <span className="text-[10px] text-slate-400">New artisan</span>
                                )}
                                {(svc.county_name || svc.sub_county_name) && (
                                  <span className="inline-flex items-center gap-0.5 text-[10px] text-slate-400">
                                    <MapPin className="size-2.5" />
                                    {[svc.county_name, svc.sub_county_name].filter(Boolean).join(" · ")}
                                  </span>
                                )}
                              </div>

                              <div className="tech-chat-card-actions">
                                <Link
                                  to="/listing/$id"
                                  params={{ id: String(svc.id) }}
                                  className="tech-chat-btn-view"
                                  onClick={() => techAudio.playClickBlip()}
                                >
                                  <span>View Service</span>
                                  <ChevronRight className="size-3" />
                                </Link>

                                <button
                                  type="button"
                                  className="tech-chat-btn-whatsapp"
                                  onClick={async () => {
                                    techAudio.playClickBlip();
                                    try {
                                      const res = await api<{ whatsapp_url: string }>(
                                        `/marketplace/listings/${svc.id}/whatsapp`
                                      );
                                      if (res.whatsapp_url) {
                                        window.open(res.whatsapp_url, "_blank", "noopener,noreferrer");
                                      }
                                    } catch {
                                      // Fallback direct wa.me
                                      window.open("https://wa.me/254700000000", "_blank", "noopener,noreferrer");
                                    }
                                  }}
                                >
                                  <MessageCircle className="size-3.5" />
                                  <span>Direct WhatsApp</span>
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Action Link Button if provided */}
                      {msg.actionLink && (
                        <div className="mt-3">
                          <Link
                            to={msg.actionLink.url}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs font-semibold hover:bg-emerald-500/30 transition-colors"
                            onClick={() => techAudio.playClickBlip()}
                          >
                            <span>{msg.actionLink.label}</span>
                            <ExternalLink className="size-3" />
                          </Link>
                        </div>
                      )}

                      <div className="tech-msg-meta">
                        <span>{msg.timestamp}</span>
                        {msg.sender === "user" && <span>✓✓ 256-bit</span>}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Animated Typing Indicator */}
                {isTyping && (
                  <div className="tech-msg-bot-row">
                    <div className="tech-chat-typing-bubble">
                      <div className="tech-chat-typing-dots">
                        <span className="tech-chat-typing-dot" />
                        <span className="tech-chat-typing-dot" />
                        <span className="tech-chat-typing-dot" />
                      </div>
                      <span>Neural fundi matcher querying live index...</span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Quick Suggestion Chips Bar */}
              <div className="tech-chat-chips-bar" aria-label="Suggested prompts">
                {activeSuggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    className="tech-chat-chip"
                    onClick={() => {
                      techAudio.playClickBlip();
                      handleSendMessage(suggestion);
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>

              {/* Chat Input Row */}
              <form
                className="tech-chat-input-row"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
              >
                <input
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Ask for an artisan, location, rates, or booking..."
                  className="tech-chat-input-field"
                  aria-label="Type message to AI Concierge"
                />
                <button
                  type="submit"
                  disabled={!inputText.trim() || isTyping}
                  className="tech-chat-send-btn"
                  title="Send message"
                  aria-label="Send message"
                >
                  <Send className="size-4" />
                </button>
              </form>
            </>
          )}
        </div>
      )}
    </>
  );
}
