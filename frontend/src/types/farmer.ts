export interface Parcela {
  latitude: number;
  longitude: number;
  crop_type: string;
  area_hectares: number;
}

export interface FarmerProfile {
  name: string;
  phone: string;
  onboarded: boolean;
  registered_at: string;
  parcela: Parcela | null;
}

export interface AgriScoreCurrent {
  total: number;
  sub_productive: number;
  sub_climate: number;
  sub_behavioral: number;
  sub_esg: number;
  scored_at: string;
  risk_category: "bajo" | "moderado" | "alto";
}

export interface AgriScoreHistory {
  total: number;
  scored_at: string;
}

export interface AgriScoreResponse {
  has_score: boolean;
  message?: string;
  current?: AgriScoreCurrent;
  history?: AgriScoreHistory[];
}

export interface Challenge {
  id: string;
  type: string;
  status: "pending" | "sent" | "completed";
  ai_tag: string | null;
  sent_at: string;
  completed_at: string | null;
}

export interface ChallengesResponse {
  total: number;
  completed: number;
  challenges: Challenge[];
}

