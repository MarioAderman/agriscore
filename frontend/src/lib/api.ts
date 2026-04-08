import type {
  FarmerProfile,
  AgriScoreResponse,
  ChallengesResponse,
} from "@/types/farmer";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json();
}

export function fetchProfile(phone: string): Promise<FarmerProfile> {
  return fetchJSON(`/api/farmer/${phone}/profile`);
}

export function fetchAgriScore(phone: string): Promise<AgriScoreResponse> {
  return fetchJSON(`/api/farmer/${phone}/agriscore`);
}

export function fetchChallenges(phone: string): Promise<ChallengesResponse> {
  return fetchJSON(`/api/farmer/${phone}/challenges`);
}

export function satelliteImageUrl(phone: string, type: "ndvi" | "rgb" = "ndvi"): string {
  return `${API_BASE}/api/farmer/${phone}/satellite?type=${type}`;
}
