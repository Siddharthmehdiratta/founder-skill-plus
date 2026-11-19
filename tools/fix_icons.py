import re, subprocess, json, sys
from pathlib import Path
from PIL import Image
for root in ["/home/claude/cgs/site", "/home/claude/repo/site"]:
    src = Path(root, "src")
    keys = set(json.loads(subprocess.run(["node", "-e", "console.log(JSON.stringify(Object.keys(require('lucide-react'))))"], cwd=root, capture_output=True, text=True).stdout))
    toks = set()
    for f in list(src.rglob("*.tsx")) + list(src.rglob("*.ts")):
        if "/velora/" in str(f) or "/ui/" in str(f) or f.name == "icon.tsx": continue
        toks |= set(re.findall(r'"([A-Z][A-Za-z0-9]+)"', f.read_text()))
    brand = {"Github", "Instagram", "Youtube", "Twitch"}
    names = sorted((toks & keys) - brand | {"Circle"})
    icon = Path(src, "components/site/icon.tsx")
    old = icon.read_text()
    brand_import = re.search(r'import \{[^}]*\} from "./brand-icons";', old).group(0)
    brand_map = re.search(r'const BRAND[^\n]*\n', old).group(0)
    icon.write_text(f'''/* Only the icons the site uses are imported, by name. Importing the whole icon library added about 1 MB of script to every page.
   Regenerate this list with tools/fix_icons.py after adding a new icon name. */
import {{ {", ".join(names)} }} from "lucide-react";
{brand_import}
{brand_map}const ICONS: Record<string, React.ComponentType<{{ className?: string; "aria-hidden"?: boolean }}>> = {{ {", ".join(names)} }};
export function Icon({{ name, className }}: {{ name: string; className?: string }}) {{
  const B = BRAND[name]; if (B) return <B className={{className}} />;
  const C = ICONS[name] ?? Circle;
  return <C aria-hidden className={{className}} />;
}}
''')
    # intrinsic sizes for screenshots, so the page does not jump while they load
    dims = {f"/shots/{p.name}": list(Image.open(p).size) for p in sorted(Path(root, "public/shots").glob("*.png"))}
    Path(src, "lib/shot-dims.json").write_text(json.dumps(dims, indent=0))
    for fp in [Path(src, "components/site/shell.tsx"), Path(src, "app/page.tsx")]:
        x = fp.read_text()
        if "shot-dims" not in x and "function Shot" in x:
            x = x.replace('<img src={href(src)} alt={alt} loading={eager ? "eager" : "lazy"} decoding="async" className={`block w-full ${className}`} /></picture>;',
                          '<img src={href(src)} alt={alt} width={(DIMS as Record<string, number[]>)[src]?.[0]} height={(DIMS as Record<string, number[]>)[src]?.[1]} loading={eager ? "eager" : "lazy"} decoding="async" className={`block h-auto w-full ${className}`} /></picture>;')
            i = x.index("import "); x = x[:i] + 'import DIMS from "@/lib/shot-dims.json";\n' + x[i:]
        # hero: size hints per source
        def hero(m):
            base = m.group(1); d = dims[f"{base}.png"]; dp = dims[f"{base}-phone.png"]
            return (f'<source media="(max-width: 640px)" type="image/webp" srcSet={{href("{base}-phone.webp")}} width={{{dp[0]}}} height={{{dp[1]}}} />\n                <source type="image/webp" srcSet={{href("{base}.webp")}} width={{{d[0]}}} height={{{d[1]}}} />\n                <img src={{href("{base}.png")}} width={{{d[0]}}} height={{{d[1]}}}')
        x = re.sub(r'<source media="\(max-width: 640px\)" type="image/webp" srcSet=\{href\("(/shots/[a-z0-9-]+)-phone\.webp"\)\} />\s*<source type="image/webp" srcSet=\{href\("/shots/[a-z0-9-]+\.webp"\)\} />\s*<img src=\{href\("/shots/[a-z0-9-]+\.png"\)\}', hero, x)
        x = x.replace('loading="eager" decoding="async" className="block w-full" />', 'loading="eager" fetchPriority="high" decoding="async" className="block h-auto w-full" />')
        fp.write_text(x)
    print(root, len(names), "icons:", " ".join(names)[:160])
