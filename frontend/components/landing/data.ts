export type MatchBadge = {
  id: string;
  title: string;
  source: string;
  mode: string;
  deadlineLabel: string;
  daysLeft: number;
};

export const SYNTHETIC_MATCHES: MatchBadge[] = [
  {
    id: "1",
    title: "Campus AI Sprint",
    source: "MLH",
    mode: "In-person",
    deadlineLabel: "Apply by",
    daysLeft: 6,
  },
  {
    id: "2",
    title: "HealthTech Build Weekend",
    source: "Devpost",
    mode: "Remote",
    deadlineLabel: "Apply by",
    daysLeft: 12,
  },
  {
    id: "3",
    title: "Fintech Fellows Hack",
    source: "Devfolio",
    mode: "Hybrid",
    deadlineLabel: "Apply by",
    daysLeft: 2,
  },
];

export const SOURCES = ["Devpost", "Devfolio", "MLH", "HackerEarth"] as const;
