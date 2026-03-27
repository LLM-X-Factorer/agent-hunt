// 平台名中文映射
export const PLATFORM_ZH: Record<string, string> = {
  linkedin: "LinkedIn",
  indeed: "Indeed",
  glassdoor: "Glassdoor",
  liepin: "猎聘",
  boss_zhipin: "Boss直聘",
  lagou: "拉勾",
  wellfound: "Wellfound",
  remoteok: "RemoteOK",
};

// 技能类别中文
export const CATEGORY_ZH: Record<string, string> = {
  language: "编程语言",
  framework: "框架",
  tool: "工具与平台",
  concept: "核心概念",
  cloud: "云服务",
};

// 常见技能名中文（保留英文原名 + 中文注释）
export const SKILL_ZH: Record<string, string> = {
  "Large Language Models": "大语言模型 (LLM)",
  "Agent Architecture": "智能体架构",
  "Retrieval-Augmented Generation": "检索增强生成 (RAG)",
  "Prompt Engineering": "提示工程",
  "Function Calling": "函数/工具调用",
  "Multi-Agent Systems": "多智能体系统",
  "Fine-tuning": "模型微调",
  "Text Embedding": "文本向量化",
  "Knowledge Graph": "知识图谱",
  "Natural Language Processing": "自然语言处理 (NLP)",
  "Machine Learning": "机器学习 (ML)",
  "Deep Learning": "深度学习",
  "Reinforcement Learning": "强化学习",
  "Computer Vision": "计算机视觉",
  "Generative AI": "生成式 AI",
  "Distributed Systems": "分布式系统",
  "Microservices": "微服务",
  "Data Analysis": "数据分析",
  "Vector Database": "向量数据库",
  "Model Context Protocol": "模型上下文协议 (MCP)",
  "Multimodal AI": "多模态 AI",
};

// 行业中文映射
export const INDUSTRY_ZH: Record<string, string> = {
  internet: "互联网/SaaS",
  finance: "金融",
  healthcare: "医疗健康",
  manufacturing: "制造/工业",
  retail: "零售/电商",
  education: "教育",
  media: "媒体/内容",
  consulting: "咨询/服务",
  automotive: "汽车/自动驾驶",
  energy: "能源",
  telecom: "通信",
  government: "政府/公共",
  other: "其他",
};

export function industryLabel(id: string): string {
  return INDUSTRY_ZH[id] || id;
}

export function skillLabel(name: string): string {
  return SKILL_ZH[name] || name;
}

export function platformLabel(id: string): string {
  return PLATFORM_ZH[id] || id;
}
