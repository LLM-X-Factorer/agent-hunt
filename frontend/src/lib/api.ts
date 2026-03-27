const API_BASE =
  typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1")
    : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1");

async function fetchAPI<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// Types
export interface Skill {
  id: string;
  canonical_name: string;
  category: string;
  subcategory: string | null;
  domestic_count: number;
  international_count: number;
  total_count: number;
  avg_salary_with: number | null;
}

export interface SalaryBucket {
  range_label: string;
  count: number;
  percentage: number;
}

export interface SalaryDistribution {
  market: string | null;
  total_jobs_with_salary: number;
  buckets: SalaryBucket[];
}

export interface SkillSalary {
  skill_id: string;
  canonical_name: string;
  job_count: number;
  avg_salary: number;
  min_salary: number;
  max_salary: number;
}

export interface ExperienceSalary {
  bracket: string;
  job_count: number;
  avg_salary: number;
}

export interface PlatformSalary {
  platform_id: string;
  job_count: number;
  avg_salary: number;
}

export interface MarketSkillRank {
  skill_id: string;
  canonical_name: string;
  count: number;
  percentage: number;
}

export interface SkillGap {
  skill_id: string;
  canonical_name: string;
  domestic_count: number;
  international_count: number;
  domestic_pct: number;
  international_pct: number;
  gap: number;
  dominant_market: string;
}

export interface CrossMarketSkills {
  domestic_top: MarketSkillRank[];
  international_top: MarketSkillRank[];
  skill_gaps: SkillGap[];
}

export interface MarketSummary {
  market: string;
  total_jobs: number;
  avg_salary: number | null;
  median_salary: number | null;
  work_mode: Record<string, number>;
  education: Record<string, number>;
  experience_distribution: ExperienceSalary[];
}

export interface MarketOverview {
  domestic: MarketSummary;
  international: MarketSummary;
}

export interface SkillPair {
  skill_a: string;
  skill_b: string;
  skill_a_name: string;
  skill_b_name: string;
  cooccurrence_count: number;
  jaccard_index: number;
}

export interface CooccurrenceResult {
  top_pairs: SkillPair[];
  total_jobs_analyzed: number;
}

export interface JobListResponse {
  total: number;
  page: number;
  page_size: number;
}

// API functions
export const api = {
  skills: () => fetchAPI<Skill[]>("/skills?sort_by=total_count"),
  salaryDistribution: (market?: string) =>
    fetchAPI<SalaryDistribution>(
      `/analysis/salary/distribution${market ? `?market=${market}` : ""}`
    ),
  salaryBySkill: (topN = 20) =>
    fetchAPI<SkillSalary[]>(`/analysis/salary/by-skill?top_n=${topN}`),
  salaryByExperience: (market?: string) =>
    fetchAPI<ExperienceSalary[]>(
      `/analysis/salary/by-experience${market ? `?market=${market}` : ""}`
    ),
  salaryByPlatform: () => fetchAPI<PlatformSalary[]>("/analysis/salary/by-platform"),
  crossMarketOverview: () => fetchAPI<MarketOverview>("/analysis/cross-market/overview"),
  crossMarketSkills: (topN = 20) =>
    fetchAPI<CrossMarketSkills>(`/analysis/cross-market/skills?top_n=${topN}`),
  skillGaps: () => fetchAPI<SkillGap[]>("/analysis/cross-market/skill-gaps"),
  cooccurrence: (topN = 20) =>
    fetchAPI<CooccurrenceResult>(`/analysis/cooccurrence?top_n=${topN}`),
  jobCount: () => fetchAPI<JobListResponse>("/jobs?page_size=1"),
};
