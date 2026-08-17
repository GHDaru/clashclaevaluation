/** API client for ClashClanEvaluation backend. */

import type {
  ClanStatusDTO,
  ConfigDTO,
  ConfigUpdateDTO,
  PlayerHistoryDTO,
} from "../types/domain";

// In dev: Vite proxy forwards /api/v1 to localhost:8002
// In prod (Vercel): VITE_API_URL points to the Railway backend
const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : "/api/v1";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getClanStatus: (clanTag?: string) =>
    fetchJSON<ClanStatusDTO>(`/clan/status${clanTag ? `?clan_tag=${encodeURIComponent(clanTag)}` : ""}`),

  getPlayerHistory: (tag: string, expand = false) =>
    fetchJSON<PlayerHistoryDTO>(
      `/players/${encodeURIComponent(tag)}?expand=${expand}`
    ),

  listWars: (limit = 12) =>
    fetchJSON<{ wars: unknown[] }>(`/wars?limit=${limit}`),

  getWarDetail: (warId: number) => fetchJSON<unknown>(`/wars/${warId}`),

  triggerEvaluation: () =>
    fetchJSON<{ war_id: number; players_evaluated: number; summary: Record<string, number> }>(
      "/evaluate",
      { method: "POST" }
    ),

  getConfig: () => fetchJSON<ConfigDTO>("/config"),

  updateConfig: (config: ConfigUpdateDTO) =>
    fetchJSON<{ message: string }>("/config", {
      method: "PUT",
      body: JSON.stringify(config),
    }),

  restoreDefaults: () =>
    fetchJSON<{ message: string }>("/config/defaults", {
      method: "POST",
    }),

  collectSnapshot: (clanTag?: string, snapshotDate?: string) =>
    fetchJSON<{
      status: string;
      war_id: number | null;
      participants_captured: number;
      snapshot_date: string;
      error: string | null;
    }>(
      `/snapshots/collect${[
        clanTag ? `clan_tag=${encodeURIComponent(clanTag)}` : "",
        snapshotDate ? `snapshot_date=${snapshotDate}` : "",
      ].filter(Boolean).join("&")}`,
      { method: "POST" }
    ),

  checkCompleteness: (clanTag?: string) =>
    fetchJSON<{
      war_id: number | null;
      expected_dates: string[];
      missing_dates: string[];
      is_complete: boolean;
    }>(`/snapshots/missing${clanTag ? `?clan_tag=${encodeURIComponent(clanTag)}` : ""}`),
};
