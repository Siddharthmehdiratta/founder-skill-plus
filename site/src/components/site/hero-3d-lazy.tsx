"use client";
import dynamic from "next/dynamic";
import { href } from "@/lib/site";
const Fallback = ({ src }: { src: string }) => <img src={href(src)} alt="A sample report on a phone: score 34 out of 100." className="mx-auto block w-full max-w-[19rem] rounded-[2.2rem] border-8 border-[#081C21] bg-[#081C21] shadow-2xl" />;
const Hero3D = dynamic(() => import("./hero-3d").then((m) => m.Hero3D), { ssr: false, loading: () => <Fallback src="/shots/report-phone.png" /> });
export function Hero3DLazy({ fallback }: { fallback: string }) { return <Hero3D fallback={fallback} />; }
