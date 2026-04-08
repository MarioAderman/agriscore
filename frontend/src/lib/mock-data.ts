import type {
  FarmerProfile,
  AgriScoreResponse,
  ChallengesResponse,
} from "@/types/farmer";

export const DEMO_PHONE = "5219611234567";

export const MOCK_PROFILE: FarmerProfile = {
  name: "José Ramón López Pérez",
  phone: DEMO_PHONE,
  onboarded: true,
  registered_at: "2024-05-15T00:00:00Z",
  parcela: {
    latitude: 24.8091,
    longitude: -107.3939,
    crop_type: "Tomate saladette",
    area_hectares: 12.5,
  },
};

export const MOCK_AGRISCORE: AgriScoreResponse = {
  has_score: true,
  current: {
    total: 81.8, // maps to ~750 on 300-850 scale
    sub_productive: 82.0,
    sub_climate: 71.0,
    sub_behavioral: 68.0,
    sub_esg: 74.0,
    scored_at: "2026-03-15T00:00:00Z",
    risk_category: "bajo",
  },
  history: [
    { total: 58.2, scored_at: "2025-10-01T00:00:00Z" },
    { total: 60.0, scored_at: "2025-11-01T00:00:00Z" },
    { total: 63.6, scored_at: "2025-12-01T00:00:00Z" },
    { total: 65.5, scored_at: "2026-01-01T00:00:00Z" },
    { total: 72.7, scored_at: "2026-02-01T00:00:00Z" },
    { total: 81.8, scored_at: "2026-03-01T00:00:00Z" },
  ],
};

export const MOCK_CHALLENGES: ChallengesResponse = {
  total: 200,
  completed: 56,
  challenges: [
    {
      id: "c1",
      type: "sustentabilidad",
      status: "pending",
      ai_tag: "Prácticas Sustentables",
      sent_at: "2026-03-20T00:00:00Z",
      completed_at: null,
    },
    {
      id: "c2",
      type: "tierra",
      status: "pending",
      ai_tag: "Cuidado de la tierra",
      sent_at: "2026-03-18T00:00:00Z",
      completed_at: null,
    },
    {
      id: "c3",
      type: "agua",
      status: "completed",
      ai_tag: "Ahorro de Agua",
      sent_at: "2026-03-10T00:00:00Z",
      completed_at: "2026-03-15T00:00:00Z",
    },
    {
      id: "c4",
      type: "fertilizacion",
      status: "completed",
      ai_tag: "Fertilización",
      sent_at: "2026-03-05T00:00:00Z",
      completed_at: "2026-03-12T00:00:00Z",
    },
    {
      id: "c5",
      type: "cosecha",
      status: "completed",
      ai_tag: "Vigor de la cosecha",
      sent_at: "2026-02-20T00:00:00Z",
      completed_at: "2026-03-01T00:00:00Z",
    },
    {
      id: "c6",
      type: "capacitacion",
      status: "completed",
      ai_tag: "Conocimiento y Capacitación",
      sent_at: "2026-02-15T00:00:00Z",
      completed_at: "2026-02-28T00:00:00Z",
    },
  ],
};

/** Challenge category display config */
export const CHALLENGE_CATEGORIES = [
  {
    tag: "Prácticas Sustentables",
    emoji: "🍃",
    total: 42,
    completed: 18,
    color: "accent",
  },
  {
    tag: "Cuidado de la tierra",
    emoji: "🌱",
    total: 60,
    completed: 19,
    color: "accent",
  },
  {
    tag: "Ahorro de Agua",
    emoji: "🚿",
    total: 34,
    completed: 22,
    color: "accent",
  },
  {
    tag: "Fertilización",
    emoji: "🏺",
    total: 28,
    completed: 23,
    color: "accent",
  },
  {
    tag: "Vigor de la cosecha",
    emoji: "⭐",
    total: 20,
    completed: 20,
    color: "accent",
  },
  {
    tag: "Conocimiento y Capacitación",
    emoji: "📖",
    total: 16,
    completed: 16,
    color: "accent",
  },
] as const;
