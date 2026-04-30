export type Market = "domestic" | "international";

export interface SkillCount {
  skill_id: string;
  count: number;
}

export interface IndustryCount {
  industry: string;
  count: number;
}

export interface RoleSalary {
  min: number;
  max: number;
  median: number;
  avg: number;
  p25: number;
  p75: number;
  sample_size: number;
}

export interface RoleExperience {
  min_range: [number, number];
  median_min: number;
  avg_min: number;
  sample_size: number;
}

export interface VsNeighbor {
  neighbor_id: string | null;
  summary: string;
}

export interface RoleProfile {
  market: Market;
  role_id: string;
  role_name: string;
  job_count: number;
  role_description: string;
  core_skills: string[];
  vs_neighbor: VsNeighbor;
  narrative: string;
  who_fits: string;
  who_doesnt: string;
  required_skills: SkillCount[];
  preferred_skills: SkillCount[];
  sample_titles: string[];
  salary: RoleSalary;
  experience: RoleExperience;
  education: Record<string, number>;
  work_mode: Record<string, number>;
  top_companies: string[];
  top_industries: IndustryCount[];
}

export const WORK_MODE_LABELS: Record<string, string> = {
  onsite: "现场",
  remote: "远程",
  hybrid: "混合",
  unknown: "未注明",
};

export const EDU_LABELS: Record<string, string> = {
  bachelor: "本科",
  master: "硕士",
  phd: "博士",
  associate: "大专",
  any: "不限",
  unspecified: "未注明",
};

export function marketLabel(market: Market): string {
  return market === "domestic" ? "国内" : "海外";
}

export function fmtSalary(n: number): string {
  if (!n) return "—";
  if (n >= 10000) return `¥${(n / 10000).toFixed(1)}w`;
  if (n >= 1000) return `¥${(n / 1000).toFixed(1)}k`;
  return `¥${Math.round(n)}`;
}

export function fmtSalaryK(n: number): string {
  if (!n) return "—";
  return `${(n / 1000).toFixed(1)}k`;
}

export function isMixedCluster(roleId: string): boolean {
  return roleId === "other";
}
