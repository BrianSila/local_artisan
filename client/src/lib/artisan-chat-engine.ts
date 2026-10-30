import { api, type Service, type Category, API_BASE } from "@/lib/local/api";

export interface ActionLink {
  label: string;
  url: string;
  isExternal?: boolean | undefined;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
  services?: Service[] | undefined;
  suggestions?: string[] | undefined;
  actionLink?: ActionLink | undefined;
  category?: string | undefined;
}

export const INITIAL_SUGGESTIONS = [
  "🔧 Find an emergency plumber in Nairobi",
  "⚡ Certified electrician in Kilimani",
  "🔨 Masonry & building quotes",
  "🛡️ How does payment & escrow work?",
  "📅 How do I book an artisan?",
  "⭐ How are artisans verified?",
];

// Fallback high-quality curated sample artisan services for Kenya
const FALLBACK_SERVICES: Service[] = [
  {
    id: "fb-101",
    artisan_id: "artisan-kamau",
    category_id: 1,
    title: "Emergency Plumbing, Pipe Repairs & Drainage",
    description: "24/7 rapid response for leaking pipes, unblocking clogged drains, borehole pump repair, and bathroom fixture installation across Nairobi & Kiambu.",
    price_type: "fixed",
    base_price: 2500,
    artisan_name: "John Kamau",
    artisan_photo_url: "https://images.unsplash.com/photo-1540569014015-19a7be504e3a?w=400&auto=format&fit=crop&q=80",
    is_verified: true,
    specialty: "Master Plumber & Drainage Specialist",
    county_name: "Nairobi",
    sub_county_name: "Westlands",
    average_rating: 4.9,
    review_count: 28,
    completed_job_count: 42,
  },
  {
    id: "fb-102",
    artisan_id: "artisan-odhiambo",
    category_id: 2,
    title: "Certified Domestic & Commercial Electrical Wiring",
    description: "Licensed EPRA electrical contractor. Full building rewiring, solar inverter setup, fuse box overhaul, smart switches, and power fault diagnosis.",
    price_type: "hourly",
    base_price: 1800,
    artisan_name: "David Odhiambo",
    artisan_photo_url: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&auto=format&fit=crop&q=80",
    is_verified: true,
    specialty: "EPRA Class B Licensed Electrician",
    county_name: "Nairobi",
    sub_county_name: "Kilimani",
    average_rating: 4.8,
    review_count: 35,
    completed_job_count: 57,
  },
  {
    id: "fb-103",
    artisan_id: "artisan-mwangi",
    category_id: 3,
    title: "Structural Masonry, Tiling & Foundation Works",
    description: "High-precision floor & wall tiling, stone wall construction, plastering, screeding, and damp proofing for residences and commercial spaces.",
    price_type: "negotiable",
    base_price: 0,
    artisan_name: "Peter Mwangi",
    artisan_photo_url: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80",
    is_verified: true,
    specialty: "Master Stone Mason & Tile Craftsman",
    county_name: "Kiambu",
    sub_county_name: "Ruiru",
    average_rating: 5.0,
    review_count: 19,
    completed_job_count: 31,
  },
  {
    id: "fb-104",
    artisan_id: "artisan-kipkorir",
    category_id: 5,
    title: "Mobile Auto Mechanic & Diagnostics Callouts",
    description: "On-site vehicle breakdown assistance, OBD2 computer diagnosis, brake pad replacement, alternator repairs, and routine engine servicing.",
    price_type: "fixed",
    base_price: 3500,
    artisan_name: "Brian Kipkorir",
    artisan_photo_url: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&auto=format&fit=crop&q=80",
    is_verified: true,
    specialty: "Automotive Diagnostics & Mobile Mechanic",
    county_name: "Nairobi",
    sub_county_name: "Lang'ata",
    average_rating: 4.9,
    review_count: 44,
    completed_job_count: 63,
  },
  {
    id: "fb-105",
    artisan_id: "artisan-wanjiku",
    category_id: 4,
    title: "Bespoke African Fashion, Tailoring & Alterations",
    description: "Custom Kitenge, Ankara, official suits, wedding apparel tailoring, and precision garment adjustments with home fitting visits available.",
    price_type: "fixed",
    base_price: 4000,
    artisan_name: "Grace Wanjiku",
    artisan_photo_url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
    is_verified: true,
    specialty: "Haute Couture & Traditional Tailor",
    county_name: "Nairobi",
    sub_county_name: "Parklands",
    average_rating: 4.95,
    review_count: 51,
    completed_job_count: 88,
  },
];

/**
 * Sound Synthesizer via Web Audio API for futuristic modern tech micro-interactions.
 */
class TechSoundSynthesizer {
  private ctx: AudioContext | null = null;
  public enabled = true;

  private getContext(): AudioContext | null {
    if (typeof window === "undefined") return null;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  playSendBeep() {
    if (!this.enabled) return;
    try {
      const ctx = this.getContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(540, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.04, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.09);
    } catch {
      // Audio context policy ignored
    }
  }

  playReceiveChime() {
    if (!this.enabled) return;
    try {
      const ctx = this.getContext();
      if (!ctx) return;
      const now = ctx.currentTime;
      [780, 1046].forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "triangle";
        osc.frequency.setValueAtTime(freq, now + idx * 0.06);
        gain.gain.setValueAtTime(0.035, now + idx * 0.06);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.06 + 0.12);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + idx * 0.06);
        osc.stop(now + idx * 0.06 + 0.13);
      });
    } catch {
      // Audio context policy ignored
    }
  }

  playClickBlip() {
    if (!this.enabled) return;
    try {
      const ctx = this.getContext();
      if (!ctx) return;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(620, ctx.currentTime);
      gain.gain.setValueAtTime(0.02, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.045);
    } catch {
      // Audio context policy ignored
    }
  }
}

export const techAudio = new TechSoundSynthesizer();

/**
 * Searches live API or returns filtered curated fallbacks
 */
async function fetchArtisans(queryText: string): Promise<Service[]> {
  try {
    const res = await api<{ items: Service[] }>(
      `/marketplace/search?search_term=${encodeURIComponent(queryText)}&limit=4`
    );
    if (res?.items && res.items.length > 0) {
      return res.items;
    }
  } catch {
    // Fall back to client filtering
  }

  const lower = queryText.toLowerCase();
  const filtered = FALLBACK_SERVICES.filter((svc) => {
    return (
      svc.title.toLowerCase().includes(lower) ||
      svc.description.toLowerCase().includes(lower) ||
      svc.specialty?.toLowerCase().includes(lower) ||
      svc.county_name?.toLowerCase().includes(lower) ||
      svc.sub_county_name?.toLowerCase().includes(lower) ||
      (lower.includes("plumb") && svc.category_id === 1) ||
      (lower.includes("electr") && svc.category_id === 2) ||
      (lower.includes("mason") && svc.category_id === 3) ||
      (lower.includes("tailor") && svc.category_id === 4) ||
      (lower.includes("mechan") && svc.category_id === 5)
    );
  });

  return filtered.length > 0 ? filtered : FALLBACK_SERVICES.slice(0, 3);
}

/**
 * Intelligent AI Concierge processing function with comprehensive Kenyan domain logic.
 */
export async function processArtisanMessage(
  userText: string,
  context?: { service?: Service | undefined; artisanName?: string | undefined }
): Promise<Omit<ChatMessage, "id" | "sender" | "timestamp">> {
  const query = userText.trim().toLowerCase();

  // If user is inquiring in context of an active service detail page
  if (context?.service) {
    const svc = context.service;
    if (
      query.includes("available") ||
      query.includes("slot") ||
      query.includes("when") ||
      query.includes("time")
    ) {
      return {
        text: `📅 **Availability for ${svc.title}**\n\n` +
          `Artisan **${svc.artisan_name || "this artisan"}** accepts bookings based on live open availability slots.\n\n` +
          `• You can select an open future time slot right on this service page below.\n` +
          `• Once submitted, the artisan reviews and confirms your request directly.\n` +
          `• Need emergency or immediate same-day service? Use the direct WhatsApp chat to verify on-demand availability!`,
        suggestions: [
          "💬 Start WhatsApp Chat",
          "📅 How does slot booking work?",
          "💳 How do I pay with M-Pesa?",
        ],
        actionLink: {
          label: `Book ${svc.title}`,
          url: `/listing/${svc.id}`,
        },
      };
    }

    if (
      query.includes("price") ||
      query.includes("cost") ||
      query.includes("how much") ||
      query.includes("rate") ||
      query.includes("pesa")
    ) {
      const priceText =
        svc.price_type === "negotiable"
          ? "Price is negotiable based on the project scope."
          : `Base price is **KES ${svc.base_price.toLocaleString("en-KE")}** (${svc.price_type}).`;
      return {
        text: `💰 **Pricing Breakdown for ${svc.title}**\n\n` +
          `${priceText}\n\n` +
          `• **Transparent Pricing**: Verified artisans provide clear upfront quotes for materials & labor.\n` +
          `• **M-Pesa Escrow Protection**: Your funds are held securely until the work is dispatched and marked complete.\n` +
          `• **Receipt & Milestone**: You receive a digital invoice upon job completion.`,
        suggestions: [
          "💬 Negotiate or request a quote",
          "🛡️ What happens if there is a dispute?",
          "⭐ Check artisan reviews",
        ],
      };
    }
  }

  // 1. Plumbing
  if (
    query.includes("plumb") ||
    query.includes("leak") ||
    query.includes("drain") ||
    query.includes("pipe") ||
    query.includes("sink") ||
    query.includes("toilet") ||
    query.includes("borehole") ||
    query.includes("tap")
  ) {
    const matches = await fetchArtisans("plumbing");
    return {
      text: `🔧 **Verified Plumbers Available Now**\n\n` +
        `I found certified plumbing specialists ready to assist with pipe bursts, bathroom fittings, solar water heaters, drainage clearing, and borehole pumps.\n\n` +
        `• **Average response time**: Under 30 minutes in major Nairobi & Kiambu hubs.\n` +
        `• **Service warranty**: Verified artisans provide quality workmanship guarantees.\n` +
        `• Select an artisan below to review credentials, see completed jobs, or start an instant chat.`,
      services: matches,
      suggestions: [
        "🚨 Emergency burst pipe repair",
        "💧 Water heater & pump installation",
        "📍 Plumbers in Westlands / Kilimani",
        "📅 Check open slots",
      ],
      actionLink: {
        label: "Browse All Plumbing Services",
        url: "/browse?category=plumbing",
      },
    };
  }

  // 2. Electrical
  if (
    query.includes("electr") ||
    query.includes("power") ||
    query.includes("wiring") ||
    query.includes("solar") ||
    query.includes("blackout") ||
    query.includes("fuse") ||
    query.includes("short circuit") ||
    query.includes("generator")
  ) {
    const matches = await fetchArtisans("electrical");
    return {
      text: `⚡ **Licensed Electrical Contractors (EPRA Certified)**\n\n` +
        `Here are vetted electrical technicians ready for domestic wiring, breaker troubleshooting, solar backup installations, smart meters, and safety audits.\n\n` +
        `• **EPRA Compliance**: All certified electricians carry verifiable licensing.\n` +
        `• **Safety First**: Insulated tooling and rigorous compliance with Kenyan building codes.`,
      services: matches,
      suggestions: [
        "☀️ Solar inverter & battery installation",
        "🔌 Tripping breaker / power surge fix",
        "💡 Full house rewiring quote",
        "💬 WhatsApp an electrician",
      ],
      actionLink: {
        label: "Browse All Electrical Services",
        url: "/browse?category=electrical",
      },
    };
  }

  // 3. Masonry, Construction & Tiling
  if (
    query.includes("mason") ||
    query.includes("tile") ||
    query.includes("tiling") ||
    query.includes("wall") ||
    query.includes("brick") ||
    query.includes("cement") ||
    query.includes("concrete") ||
    query.includes("plaster") ||
    query.includes("foundation")
  ) {
    const matches = await fetchArtisans("masonry");
    return {
      text: `🔨 **Master Masons & Tiling Craftsmen**\n\n` +
        `Need precision construction work? Here are top-rated artisans specializing in stone work, floor & wall tiling, perimeter walls, damp proofing, and structural repairs.\n\n` +
        `• Detailed portfolios with verified job site photography.\n` +
        `• Fixed-rate and per-square-meter project pricing available.`,
      services: matches,
      suggestions: [
        "🧱 Perimeter wall & stone work",
        "✨ Bathroom & kitchen floor tiling",
        "🏗️ Foundation & structural repairs",
      ],
      actionLink: {
        label: "Browse Masonry & Construction",
        url: "/browse?category=masonry",
      },
    };
  }

  // 4. Automotive Mechanics
  if (
    query.includes("mechanic") ||
    query.includes("car") ||
    query.includes("auto") ||
    query.includes("engine") ||
    query.includes("brake") ||
    query.includes("tyre") ||
    query.includes("vehicle") ||
    query.includes("breakdown")
  ) {
    const matches = await fetchArtisans("mechanics");
    return {
      text: `🚗 **Mobile Auto Mechanics & Breakdown Specialists**\n\n` +
        `Certified automotive engineers who come directly to your location with diagnostic scanners, emergency jump-packs, brake systems, and quick service parts.\n\n` +
        `• On-site OBD2 computerized diagnostic scans.\n` +
        `• Field breakdown recovery across Nairobi, Mombasa Road, Thika Superhighway, and Nakuru Highway.`,
      services: matches,
      suggestions: [
        "💻 Computerized vehicle OBD2 scan",
        "🛑 Brake pads & disc replacement",
        "🔋 Dead battery & alternator troubleshooting",
        "🚨 Immediate breakdown rescue",
      ],
      actionLink: {
        label: "Browse Automotive Mechanics",
        url: "/browse?category=mechanics",
      },
    };
  }

  // 5. Tailoring & Fashion
  if (
    query.includes("tailor") ||
    query.includes("cloth") ||
    query.includes("sew") ||
    query.includes("dress") ||
    query.includes("suit") ||
    query.includes("kitenge") ||
    query.includes("ankara") ||
    query.includes("alteration")
  ) {
    const matches = await fetchArtisans("tailoring");
    return {
      text: `✂️ **Bespoke Tailors & Fashion Designers**\n\n` +
        `Connect with custom apparel artisans specializing in African Kitenge prints, custom tailored wedding suits, office attire, and precise garment fittings.\n\n` +
        `• Fabric consultation and custom measurements.\n` +
        `• Home and office fitting visits available on appointment.`,
      services: matches,
      suggestions: [
        "👗 Custom Kitenge & Ankara designs",
        "👔 Official 3-piece suit tailoring",
        "📏 Garment alteration & resizing",
      ],
      actionLink: {
        label: "Browse Tailoring & Design",
        url: "/browse?category=tailoring",
      },
    };
  }

  // 6. How Booking Works
  if (
    query.includes("how to book") ||
    query.includes("booking") ||
    query.includes("how it works") ||
    query.includes("schedule") ||
    query.includes("reserve")
  ) {
    return {
      text: `📅 **How Booking Works on Local Artisan**\n\n` +
        `1. **Find a Verified Artisan**: Search by service category, location (County/Subcounty), or GPS radius.\n` +
        `2. **Inspect Profile & Portfolio**: Check authentic client reviews, verified badges, and completed job track record.\n` +
        `3. **Pick an Open Time Slot**: Select an available slot directly on the artisan's listing page.\n` +
        `4. **Confirmation & Dispatch**: The artisan receives your notification, confirms details, and is dispatched to your site.\n` +
        `5. **Review & Payment**: Mark the job complete once satisfied and leave an honest rating for the community.`,
      suggestions: [
        "🔍 Find artisans near me",
        "💳 How does M-Pesa payment work?",
        "🛡️ What is the dispute process?",
      ],
      actionLink: {
        label: "Explore Services Catalog",
        url: "/browse",
      },
    };
  }

  // 7. Payment, M-Pesa & Escrow
  if (
    query.includes("pay") ||
    query.includes("mpesa") ||
    query.includes("m-pesa") ||
    query.includes("money") ||
    query.includes("escrow") ||
    query.includes("cost") ||
    query.includes("deposit") ||
    query.includes("refund")
  ) {
    return {
      text: `💳 **Payment Protection & M-Pesa Checkout**\n\n` +
        `• **M-Pesa STK Push**: Seamless payments directly on your Safaricom line via our integrated checkout.\n` +
        `• **Secure Milestone Settlement**: Labor payments are safeguarded until the artisan finishes the task to agreed standards.\n` +
        `• **No Hidden Platform Fees**: Clear pricing models displayed on every listing (Fixed, Hourly, or Negotiable).\n` +
        `• **Automated Receipts**: Downloadable digital receipts for corporate and personal expense bookkeeping.`,
      suggestions: [
        "🛡️ What happens if the job is unfinished?",
        "⭐ How to verify an artisan's credibility",
        "📞 Contact customer support",
      ],
    };
  }

  // 8. Verification & Safety
  if (
    query.includes("verify") ||
    query.includes("safe") ||
    query.includes("trust") ||
    query.includes("scam") ||
    query.includes("id") ||
    query.includes("police") ||
    query.includes("good conduct")
  ) {
    return {
      text: `🛡️ **Artisan Verification & Trust Standards**\n\n` +
        `Every artisan displaying the **Verified Artisan** badge has undergone rigorous vetting:\n\n` +
        `• **National ID / Alien ID Verification**: Cross-referenced with official records.\n` +
        `• **Certificate of Good Conduct**: Criminal background clearance verified before public listing.\n` +
        `• **Skill & Reference Checks**: Prior customer testimonials and verified trade licenses (EPRA, NCA where applicable).\n` +
        `• **Physical Location Confirmation**: County and sub-county mapping for accountability.\n\n` +
        `*Always check the blue badge on artisan profiles before booking!*`,
      suggestions: [
        "🔍 Search only verified artisans",
        "⚖️ How do disputes get resolved?",
        "🤝 Apply to become an artisan",
      ],
      actionLink: {
        label: "Browse Verified Artisans",
        url: "/browse",
      },
    };
  }

  // 9. Becoming an artisan / Onboarding
  if (
    query.includes("join") ||
    query.includes("become an artisan") ||
    query.includes("register as fundi") ||
    query.includes("onboard") ||
    query.includes("sell my skills")
  ) {
    return {
      text: `🚀 **Join Local Artisan as a Verified Professional**\n\n` +
        `Are you a skilled fundi or craftsperson looking to expand your clientele across Kenya?\n\n` +
        `1. Create an account and select the **Artisan** role.\n` +
        `2. Fill in your bio, skills, years of experience, and primary county/subcounty.\n` +
        `3. Upload your profile photo, work gallery, and verification documents.\n` +
        `4. Set up your service catalog with fixed, hourly, or negotiable rates.\n` +
        `5. Manage your availability calendar and accept booking requests directly!`,
      suggestions: [
        "📝 Register as an Artisan",
        "💡 Tips for getting verified quickly",
        "💬 Contact the Artisan Onboarding Desk",
      ],
      actionLink: {
        label: "Register New Artisan Account",
        url: "/auth?role=artisan",
      },
    };
  }

  // 10. General search or match
  const generalMatches = await fetchArtisans(query);
  return {
    text: `⚡ **FundiBot Neural Search Results**\n\n` +
      `I processed your query: *"${userText}"* and matched the top verified local specialists in Kenya matching your requirements.\n\n` +
      `• Browse the matched profiles below or click **View Service** to check schedule availability.\n` +
      `• You can also click **Direct WhatsApp** to chat with an artisan right now!`,
    services: generalMatches,
    suggestions: [
      "🔧 Find emergency plumbers",
      "⚡ Licensed electricians",
      "🔨 Stone masonry & tiling",
      "🛡️ How escrow protects my funds",
      "📍 Change search location",
    ],
    actionLink: {
      label: "View All Marketplace Listings",
      url: `/browse?search=${encodeURIComponent(userText)}`,
    },
  };
}
