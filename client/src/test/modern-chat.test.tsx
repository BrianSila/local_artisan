import { describe, expect, it } from "vitest";
import { processArtisanMessage, techAudio } from "@/lib/artisan-chat-engine";

describe("Modern Tech Artisan Chat Engine", () => {
  it("processes emergency plumbing query and returns services & suggestions", async () => {
    const result = await processArtisanMessage("I have an emergency pipe leak in Westlands");
    expect(result.text).toContain("Verified Plumbers");
    expect(result.services).toBeDefined();
    expect(result.services!.length).toBeGreaterThan(0);
    expect(result.suggestions).toContain("🚨 Emergency burst pipe repair");
  });

  it("handles EPRA electrical contractors query", async () => {
    const result = await processArtisanMessage("Need certified electrician for power outage wiring");
    expect(result.text).toContain("Electrical Contractors");
    expect(result.services).toBeDefined();
    expect(result.actionLink?.url).toContain("electrical");
  });

  it("explains booking and M-Pesa escrow protection", async () => {
    const result = await processArtisanMessage("How do I pay with mpesa and how is it safe?");
    expect(result.text).toContain("M-Pesa STK Push");
    expect(result.text).toContain("Milestone Settlement");
  });

  it("provides synthesizer audio toggling", () => {
    techAudio.enabled = false;
    expect(techAudio.enabled).toBe(false);
    techAudio.playClickBlip(); // Should not throw
    techAudio.enabled = true;
    expect(techAudio.enabled).toBe(true);
  });
});
