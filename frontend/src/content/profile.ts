// Portfolio content. Facts here mirror the CV; update both together.

export const profile = {
  name: 'Tshimbiluni Nedambale',
  role: 'Software Engineer',
  focus: 'Python backend, applied AI & full-stack',
  location: 'Johannesburg, South Africa',
  summary:
    'I build and run production systems with Python, Django REST Framework, FastAPI, PostgreSQL, Celery and React. Today I work on a high-volume Accounts Payable automation platform: document intelligence, asynchronous processing, integrations and production support.',
  current: {
    title: 'Junior Python Developer',
    company: 'Fluid',
  },
  avatarUrl: 'https://github.com/TshimbiluniRSA.png?size=320',
  links: {
    email: 'hugetshimbi@gmail.com',
    linkedin: 'https://www.linkedin.com/in/tshimbiluni-nedambale',
    github: 'https://github.com/TshimbiluniRSA',
  },
};

export interface Role {
  title: string;
  company: string;
  period: string;
  location: string;
  highlights: string[];
}

export const experience: Role[] = [
  {
    title: 'Junior Python Developer',
    company: 'Fluid',
    period: 'Nov 2025 – Present',
    location: 'Fourways, Gauteng',
    highlights: [
      'Develop and support a production Accounts Payable automation platform with Django REST Framework, Celery, PostgreSQL, Docker, React and TypeScript.',
      'Build asynchronous workflows for mailbox ingestion, document classification and extraction, invoice creation and SharePoint task management.',
      'Improved duplicate-prevention, idempotency and status handling to stop repeated processing and inconsistent financial records.',
      'Built migration and reconciliation tooling for a dry run of more than 77,000 task operations.',
    ],
  },
  {
    title: 'Junior AI/Software Engineer (Graduate Trainee II)',
    company: 'Sasol',
    period: 'Aug 2025 – Nov 2025',
    location: 'Sandton, Gauteng',
    highlights: [
      'Co-developed the SHE AI chatbot, an enterprise assistant for Safety, Health and Environment governance information.',
      'Helped define an approved architecture pattern for secure, reusable AI integrations with architects and technology partners.',
      "Co-developed a digital screens application for Sasol's 75-year milestone, recognised by executive leadership.",
      'Modernised a legacy .NET crowdsourcing platform with a Django backend and React frontend.',
    ],
  },
  {
    title: 'Full-Stack Developer Intern',
    company: 'Sasol',
    period: 'Aug 2024 – Jul 2025',
    location: 'Sandton, Gauteng',
    highlights: [
      'Built secure REST APIs with Django REST Framework for React and TypeScript frontends.',
      'Built a real-time voice-chat prototype with FastAPI, React and Azure OpenAI.',
      'Led the migration of applications and databases from a local cluster to Azure Kubernetes Service.',
      'Set up CI/CD in Azure DevOps and GitHub with Snyk and SonarQube, and monitored services with New Relic.',
    ],
  },
  {
    title: 'YES Youth Intern, CIB Data Team',
    company: 'Nedbank',
    period: 'May 2024 – Jul 2024',
    location: 'Sandton, Gauteng',
    highlights: [
      'Built a Microsoft Power App to submit, track and prioritise business data requests.',
      'Documented data-lineage and governance processes and onboarding material for data roles.',
    ],
  },
];

export const education = {
  degree: 'BSc Information Technology',
  school: 'North-West University',
  year: '2023',
  certifications: ['Azure Fundamentals (AZ-900)', 'Azure AI Fundamentals (AI-900)'],
};

export interface Project {
  title: string;
  badge: string;
  summary: string;
  problem: string;
  approach: string;
  result: string;
  tags: string[];
  repo: string;
  live?: string;
}

export const projects: Project[] = [
  {
    title: 'AI-Powered Portfolio Platform',
    badge: 'In production',
    summary: 'This site: a full-stack application with an AI assistant, running on AWS.',
    problem: 'A CV lists skills; it does not show how I design, ship and operate software.',
    approach:
      'React and TypeScript frontend; FastAPI and PostgreSQL backend on EC2 and RDS; an OpenAI assistant grounded in my profile; GitHub data cached and refreshed daily.',
    result:
      'Merges to main deploy automatically through GitHub OIDC and Systems Manager, with migrations, health checks and rollback. The rotating database password is read from Secrets Manager.',
    tags: ['FastAPI', 'React', 'PostgreSQL', 'OpenAI', 'AWS', 'GitHub Actions'],
    repo: 'https://github.com/TshimbiluniRSA/Tshimbiluni-AI-powered-Portfolio',
    live: 'https://tshimbiluniportfolio.tech',
  },
  {
    title: 'AWS Infrastructure as Code',
    badge: 'Terraform',
    summary: 'The production AWS environment behind this portfolio, fully in Terraform.',
    problem:
      'The backend needed production infrastructure that is reproducible, private by default and free of long-lived credentials.',
    approach:
      'Terraform modules for a VPC with public and private subnets, private RDS, an EC2 host managed through Systems Manager, private S3 and least-privilege IAM, with locked remote state.',
    result:
      'Plans run on pull requests and applies run from main, all through GitHub OIDC: no AWS access keys and no SSH.',
    tags: ['Terraform', 'AWS', 'IAM', 'RDS', 'Systems Manager', 'OIDC'],
    repo: 'https://github.com/TshimbiluniRSA/my-aws-infrastructure',
  },
  {
    title: 'Multilingual Educational Content Platform',
    badge: 'Top 3 · GDG Build with AI 2026',
    summary: 'Turns English learning material into South African home languages.',
    problem: 'Most educational material is only available in English.',
    approach:
      'A four-person team build with FastAPI and React: PDF extraction and YouTube transcripts feed Gemini 2.5 Flash, which returns structured, consistent translations.',
    result:
      'Placed in the Top 3 at GDG Johannesburg Build with AI 2026, hosted with Google, BBD and OfferZen.',
    tags: ['FastAPI', 'React', 'TypeScript', 'Gemini', 'Pydantic'],
    repo: 'https://github.com/TshimbiluniRSA/BuildwithAI-buildathon',
  },
  {
    title: 'Context-Window-Aware RAG System',
    badge: 'Technical assessment',
    summary: 'Retrieval that respects the limits of an LLM context window.',
    problem: 'An LLM can only use the information that fits in its context window.',
    approach:
      'Structured retrieval, context selection and prompt construction, designed for maintainability and clear system boundaries.',
    result: 'A retrieval pipeline that chooses what the model sees instead of truncating it.',
    tags: ['Python', 'RAG', 'LLMs'],
    repo: 'https://github.com/TshimbiluniRSA/Context-Window-Aware-RAG-Deloitte-assessment-',
  },
];

export const skills: { area: string; items: string[] }[] = [
  {
    area: 'Backend',
    items: ['Python', 'Django REST Framework', 'FastAPI', 'Celery', 'SQLAlchemy', 'REST APIs'],
  },
  {
    area: 'Applied AI',
    items: [
      'OpenAI & Azure OpenAI',
      'Gemini',
      'RAG',
      'Document intelligence',
      'Structured extraction',
    ],
  },
  {
    area: 'Data',
    items: ['PostgreSQL', 'MySQL', 'Migrations', 'Reconciliation', 'Data integrity'],
  },
  {
    area: 'Frontend',
    items: ['React', 'TypeScript', 'Vite', 'Tailwind CSS'],
  },
  {
    area: 'Cloud & DevOps',
    items: ['AWS', 'Azure & AKS', 'Docker', 'Terraform', 'GitHub Actions', 'Azure DevOps'],
  },
  {
    area: 'Quality',
    items: ['pytest', 'Snyk', 'SonarQube', 'New Relic', 'Production debugging'],
  },
];

export const suggestedQuestions = [
  'What does he work on at Fluid?',
  'What AI projects has he built?',
  'How is this portfolio deployed?',
  'What is his experience with AWS?',
];
