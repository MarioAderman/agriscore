"use client";

import { useEffect, useState } from "react";
import type {
  FarmerProfile,
  AgriScoreResponse,
  ChallengesResponse,
} from "@/types/farmer";
import { fetchProfile, fetchAgriScore, fetchChallenges } from "@/lib/api";
import {
  DEMO_PHONE,
  MOCK_PROFILE,
  MOCK_AGRISCORE,
  MOCK_CHALLENGES,
} from "@/lib/mock-data";

interface UseDataResult<T> {
  data: T;
  loading: boolean;
  error: boolean;
}

function useFetch<T>(fetcher: (phone: string) => Promise<T>, fallback: T): UseDataResult<T> {
  const [data, setData] = useState<T>(fallback);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    fetcher(DEMO_PHONE)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch(() => {
        if (!cancelled) {
          setError(true);
          setData(fallback);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => { cancelled = true; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { data, loading, error };
}

export function useFarmerProfile(): UseDataResult<FarmerProfile> {
  return useFetch(fetchProfile, MOCK_PROFILE);
}

export function useFarmerAgriScore(): UseDataResult<AgriScoreResponse> {
  return useFetch(fetchAgriScore, MOCK_AGRISCORE);
}

export function useFarmerChallenges(): UseDataResult<ChallengesResponse> {
  return useFetch(fetchChallenges, MOCK_CHALLENGES);
}
