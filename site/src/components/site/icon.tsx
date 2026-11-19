import * as L from "lucide-react";
import { GithubMark, InstagramMark, TwitchMark, YouTubeMark } from "./brand-icons";
const BRAND: Record<string, React.ComponentType<{ className?: string }>> = { Github: GithubMark, Instagram: InstagramMark, Youtube: YouTubeMark, Twitch: TwitchMark };
export function Icon({ name, className }: { name: string; className?: string }) {
  const B = BRAND[name]; if (B) return <B className={className} />;
  const C = (L as unknown as Record<string, React.ComponentType<{ className?: string; "aria-hidden"?: boolean }>>)[name] ?? L.Circle;
  return <C aria-hidden className={className} />;
}
