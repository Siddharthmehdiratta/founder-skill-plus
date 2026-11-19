/* Only the icons the site uses are imported, by name. Importing the whole icon library added about 1 MB of script to every page.
   Regenerate this list with tools/fix_icons.py after adding a new icon name. */
import { ArrowDown, ArrowLeft, ArrowRight, ArrowUp, BadgeCheck, BookOpen, Bug, Calendar, Circle, ClipboardList, Contact, Database, FileText, Files, FlaskConical, Globe, History, Inbox, LifeBuoy, Mail, MapPin, MessageCircleQuestion, MessageSquareHeart, Orbit, Rocket, Scale, ScanSearch, Search, Settings, ShieldCheck, Ship, Sparkles, Stars, Users, Workflow } from "lucide-react";
import { GithubMark, InstagramMark, TwitchMark, YouTubeMark } from "./brand-icons";
const BRAND: Record<string, React.ComponentType<{ className?: string }>> = { Github: GithubMark, Instagram: InstagramMark, Youtube: YouTubeMark, Twitch: TwitchMark };
const ICONS: Record<string, React.ComponentType<{ className?: string; "aria-hidden"?: boolean }>> = { ArrowDown, ArrowLeft, ArrowRight, ArrowUp, BadgeCheck, BookOpen, Bug, Calendar, Circle, ClipboardList, Contact, Database, FileText, Files, FlaskConical, Globe, History, Inbox, LifeBuoy, Mail, MapPin, MessageCircleQuestion, MessageSquareHeart, Orbit, Rocket, Scale, ScanSearch, Search, Settings, ShieldCheck, Ship, Sparkles, Stars, Users, Workflow };
export function Icon({ name, className }: { name: string; className?: string }) {
  const B = BRAND[name]; if (B) return <B className={className} />;
  const C = ICONS[name] ?? Circle;
  return <C aria-hidden className={className} />;
}
