import type {
  IndustryCount,
  MajorCount,
  ResponsibilityCount,
  RoleExperience,
  RoleSalary,
  SkillCount,
  Market,
} from "@/lib/roles";

export type ProfessionCategory = "engineering" | "business" | "service";

export interface AiPivotTarget {
  market: Market;
  role_id: string;
  role_name: string;
  count: number;
}

export interface ProfessionProfile {
  profession_id: string;
  cn_name: string;
  en_name: string;
  category: ProfessionCategory;
  one_liner: string;
  description: string;
  responsibilities: string[];
  pathway_summary: string;
  who_should_pivot: string;
  who_shouldnt_pivot: string;
  aliases: string[];

  sample_size: number;

  // Aggregates (present iff sample_size > 0)
  salary?: RoleSalary | null;
  experience?: RoleExperience | null;
  education?: Record<string, number>;
  work_mode?: Record<string, number>;
  top_companies?: string[];
  top_industries?: IndustryCount[];
  top_majors?: MajorCount[];
  majors_sample_size?: number;
  top_responsibilities?: ResponsibilityCount[];
  responsibilities_sample_size?: number;
  sample_titles?: string[];
  required_skills?: SkillCount[];
  preferred_skills?: SkillCount[];

  ai_pivot_targets: AiPivotTarget[];
}

export const PROFESSION_CATEGORY_LABELS: Record<ProfessionCategory, string> = {
  engineering: "工程线",
  business: "商科线",
  service: "服务线",
};

export const PROFESSION_CATEGORY_ORDER: ProfessionCategory[] = [
  "engineering",
  "business",
  "service",
];

// Tiered disclaimer for sample-size adequacy.
// strong (≥30): no banner. medium (10-29): yellow note. weak (5-9): red banner.
// none (0-4): suppress baseline section entirely — too few samples for any distribution to be meaningful.
export type SampleTier = "strong" | "medium" | "weak" | "none";

export function sampleTier(n: number): SampleTier {
  if (n < 5) return "none";
  if (n < 10) return "weak";
  if (n < 30) return "medium";
  return "strong";
}
