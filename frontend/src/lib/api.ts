// Static mode: read from /data/*.json (pre-exported from backend API)
// To switch to live API, set NEXT_PUBLIC_API_URL env var

const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function fetchStatic<T>(filename: string): Promise<T> {
  const res = await fetch(`/data/${filename}`);
  if (!res.ok) throw new Error(`Failed to load ${filename}: ${res.status}`);
  return res.json();
}

async function fetchAPI<T>(path: string, staticFile: string): Promise<T> {
  if (API_URL) {
    const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  }
  return fetchStatic<T>(staticFile);
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

// API functions — static file fallback when no API_URL
export const api = {
  skills: () =>
    fetchAPI<Skill[]>("/skills?sort_by=total_count", "skills.json"),
  salaryDistribution: () =>
    fetchAPI<SalaryDistribution>("/analysis/salary/distribution", "salary-distribution.json"),
  salaryBySkill: () =>
    fetchAPI<SkillSalary[]>("/analysis/salary/by-skill?top_n=15", "salary-by-skill.json"),
  salaryByExperience: () =>
    fetchAPI<ExperienceSalary[]>("/analysis/salary/by-experience", "salary-by-experience.json"),
  salaryByPlatform: () =>
    fetchAPI<PlatformSalary[]>("/analysis/salary/by-platform", "salary-by-platform.json"),
  crossMarketOverview: () =>
    fetchAPI<MarketOverview>("/analysis/cross-market/overview", "cross-market-overview.json"),
  crossMarketSkills: () =>
    fetchAPI<CrossMarketSkills>("/analysis/cross-market/skills?top_n=20", "cross-market-skills.json"),
  skillGaps: () =>
    fetchAPI<SkillGap[]>("/analysis/cross-market/skill-gaps", "skill-gaps.json"),
  cooccurrence: () =>
    fetchAPI<CooccurrenceResult>("/analysis/cooccurrence?top_n=10", "cooccurrence.json"),
  jobCount: () =>
    fetchAPI<JobListResponse>("/jobs?page_size=1", "job-count.json"),
  industryOverview: () =>
    fetchAPI<IndustrySummary[]>("/analysis/industry/overview", "industry-overview.json"),
  industrySalary: () =>
    fetchAPI<IndustrySalary[]>("/analysis/industry/salary", "industry-salary.json"),
  insights: () => fetchStatic<Record<string, string>>("insights.json"),
  jobSamples: () => fetchStatic<Record<string, JobSampleGroup>>("job-samples.json"),
  personas: () => fetchStatic<Persona[]>("personas.json"),
  learningPaths: () => fetchStatic<LearningPath[]>("learning-paths.json"),
};

// Industry types
export interface IndustrySkillCount {
  skill_id: string;
  count: number;
}

export interface IndustrySummary {
  industry: string;
  job_count: number;
  domestic_count: number;
  international_count: number;
  avg_salary: number | null;
  top_skills: IndustrySkillCount[];
}

export interface IndustrySalary {
  industry: string;
  job_count: number;
  avg_salary: number;
}

// Insight types
export interface JobSample {
  title: string;
  company: string;
  location: string;
  market: string;
  salary: string;
  skills: string[];
  snippet: string;
}

export interface JobSampleGroup {
  skill_name: string;
  jobs: JobSample[];
}

export interface Persona {
  id: string;
  title: string;
  subtitle: string;
  market: string;
  core_skills: string[];
  salary_range: string;
  experience: string;
  education: string;
  company_types: string;
  work_mode: string;
  day_in_life: string;
  key_insight: string;
}

export interface LearningStep {
  order: number;
  title: string;
  description: string;
  skills: string[];
  resources_hint: string;
}

export interface LearningPath {
  id: string;
  title: string;
  subtitle: string;
  target_audience: string;
  assumed_skills: string[];
  target_role: string;
  duration: string;
  steps: LearningStep[];
  key_advice: string;
}
