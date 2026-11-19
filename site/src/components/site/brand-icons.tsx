/* Simple platform marks (lucide no longer ships brand icons). */
type P = { className?: string };
export const InstagramMark = ({ className }: P) => (
  <svg aria-hidden viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" /></svg>
);
export const YouTubeMark = ({ className }: P) => (
  <svg aria-hidden viewBox="0 0 24 24" className={className} fill="currentColor"><path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3z" /></svg>
);
export const TwitchMark = ({ className }: P) => (
  <svg aria-hidden viewBox="0 0 24 24" className={className} fill="currentColor"><path d="M4.3 3 3 6.4V19h4.3v2.3h2.4L12 19h3.5l4.7-4.7V3zm14.3 10.5L15.9 16.2h-4.3l-2.3 2.3v-2.3H5.6V4.6h13zM16 7.4h-1.6v4.7H16zm-4.3 0h-1.6v4.7h1.6z" /></svg>
);
export const GithubMark = ({ className }: P) => (
  <svg aria-hidden viewBox="0 0 24 24" className={className} fill="currentColor"><path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.4-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.4 1.1 2.9.8.1-.6.4-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-5a3.9 3.9 0 0 1 1-2.7 3.6 3.6 0 0 1 .1-2.7s.8-.3 2.8 1a9.6 9.6 0 0 1 5 0c1.9-1.3 2.7-1 2.7-1 .6 1.4.2 2.4.1 2.7a3.9 3.9 0 0 1 1 2.7c0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2z" /></svg>
);
export const LogoMark = ({ className }: P) => (
  <svg aria-hidden viewBox="0 0 32 32" className={className}><defs><linearGradient id="fpg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#0EA47A" /><stop offset="1" stopColor="#13A9C8" /></linearGradient></defs><rect width="32" height="32" rx="9" fill="url(#fpg)" /><circle cx="12" cy="13" r="3.2" fill="#fff" /><circle cx="20.5" cy="13" r="3.2" fill="#fff" fillOpacity=".75" /><path d="M7 24c.8-3.4 2.8-5.2 5-5.2s4.2 1.8 5 5.2M15.6 24c.8-3.4 2.8-5.2 5-5.2s4.2 1.8 5 5.2" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" fill="none" />
  </svg>
);
