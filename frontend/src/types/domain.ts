/** TypeScript mirrors of domain Ubiquitous Language terms. */

export interface PlayerStatusDTO {
  tag: string;
  name: string;
  role: "leader" | "coLeader" | "elder" | "member";
  attacks_today: number;
  attacks_total: number;
  total_points: number;
  yellow_cards: number;
  red_cards: number;
  black_cards: number;
  status: "clean" | "warning" | "danger" | "critical";
  trend: "improving" | "stable" | "declining" | "new";
}

export interface ClanStatusDTO {
  war_active: boolean;
  war_id: number | null;
  day: number | null;
  day_label: string | null;
  status: string | null;
  position: number | null;
  total_fame: number;
  daily_fame: number;
  clans_count: number;
  relaxed: boolean;
  players: PlayerStatusDTO[];
}

export interface WarDetailDTO {
  war: {
    id: number;
    start_date: string;
    end_date: string;
    status: string;
    total_fame: number;
    relaxed_days: number[];
  };
  players: PlayerStatusDTO[];
}

export interface PlayerHistoryDTO {
  tag: string;
  name: string;
  role: string;
  first_seen: string;
  last_seen: string;
  current_war: PlayerWarEntry | null;
  recency: {
    wars: PlayerWarEntry[];
    trend: string;
  };
  history: PlayerWarEntry[];
}

export interface PlayerWarEntry {
  war_id: number | null;
  start_date?: string;
  attacks?: [number, number, number, number];
  total_points: number;
  yellow_cards: number;
  red_cards: number;
  black_cards: number;
  status?: string;
}

export interface ConfigDTO {
  cr_clan_tag: string;
  attacks_per_day: number;
  yellow_to_red: number;
  red_to_black: number;
  min_points_warning: number;
  min_points_critical: number;
  relax_on_first_place: boolean;
  recency_weeks: number;
  history_months: number;
}

export interface ConfigUpdateDTO {
  attacks_per_day?: number;
  yellow_to_red?: number;
  red_to_black?: number;
  min_points_warning?: number;
  min_points_critical?: number;
  relax_on_first_place?: boolean;
  cr_clan_tag?: string;
}
