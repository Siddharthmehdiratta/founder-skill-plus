"use client";
import { Suspense, useEffect, useRef, useState } from "react";
import { Canvas, useFrame, useLoader } from "@react-three/fiber";
import { Float, RoundedBox } from "@react-three/drei";
import * as THREE from "three";
import { href } from "@/lib/site";

const STAR = (() => { const s = new THREE.Shape(); for (let i = 0; i < 10; i++) { const r = i % 2 ? 0.036 : 0.085, a = Math.PI / 2 + (i * Math.PI) / 5; const x = Math.cos(a) * r, y = Math.sin(a) * r; if (i) s.lineTo(x, y); else s.moveTo(x, y); } s.closePath(); return s; })();

/* A real phone, in 3D, showing the real report. It leans towards the pointer and floats.
   Loads after the page; phones and people who prefer less motion get the flat picture instead. */
function Phone({ src }: { src: string }) {
  const g = useRef<THREE.Group>(null!);
  const tex = useLoader(THREE.TextureLoader, src);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const aspect = tex.image ? (tex.image as HTMLImageElement).height / (tex.image as HTMLImageElement).width : 2.16;
  const w = 1.9, h = Math.min(4.2, w * aspect);
  useFrame((state) => {
    const { x, y } = state.pointer;
    g.current.rotation.y = THREE.MathUtils.lerp(g.current.rotation.y, -0.35 + x * 0.35, 0.06);
    g.current.rotation.x = THREE.MathUtils.lerp(g.current.rotation.x, 0.08 - y * 0.2, 0.06);
  });
  return (
    <group ref={g}>
      <Float speed={1.4} rotationIntensity={0.15} floatIntensity={0.6}>
        <RoundedBox args={[w + 0.18, h + 0.18, 0.22]} radius={0.22} smoothness={6}>
          <meshStandardMaterial color="#081C21" metalness={0.6} roughness={0.25} />
        </RoundedBox>
        <mesh position={[0, 0, 0.115]}>
          <planeGeometry args={[w, h]} />
          <meshBasicMaterial map={tex} toneMapped={false} />
        </mesh>
        {/* floating stars badge */}
        <group position={[1.35, 1.1, 0.5]}>
          <RoundedBox args={[1.25, 0.5, 0.08]} radius={0.12} smoothness={4}><meshStandardMaterial color="#ffffff" roughness={0.4} /></RoundedBox>
          {[0, 1, 2, 3, 4].map((i) => (
            <mesh key={i} position={[-0.42 + i * 0.21, 0, 0.05]}>
              <shapeGeometry args={[STAR]} /><meshBasicMaterial color={i < 4 ? "#F5A524" : "#E5E3EC"} />
            </mesh>
          ))}
        </group>
        <mesh position={[-1.4, -1.2, 0.45]}>
          <sphereGeometry args={[0.22, 32, 32]} /><meshStandardMaterial color="#0B7A5C" metalness={0.3} roughness={0.2} emissive="#0B7A5C" emissiveIntensity={0.25} />
        </mesh>
      </Float>
    </group>
  );
}

export function Hero3D({ fallback }: { fallback: string }) {
  const [on, setOn] = useState(false);
  useEffect(() => {
    const ok = window.matchMedia("(min-width: 1024px)").matches && !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    try { const c = document.createElement("canvas"); if (ok && (c.getContext("webgl2") || c.getContext("webgl"))) setOn(true); } catch {}
  }, []);
  const img = <img src={href(fallback)} alt="A sample report on a phone: score 34 out of 100." className="mx-auto block w-full max-w-[19rem] rounded-[2.2rem] border-8 border-[#081C21] bg-[#081C21] shadow-2xl" />;
  if (!on) return img;
  return (
    <div className="relative h-[40rem] w-full" aria-label="A sample report on a phone, in 3D. Move your pointer to tilt it.">
      <Canvas camera={{ position: [0, 0, 6.2], fov: 42 }} dpr={[1, 2]} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.8} />
        <directionalLight position={[3, 4, 5]} intensity={1.6} />
        <pointLight position={[-4, -2, 3]} intensity={30} color="#5FE3BC" />
        <Suspense fallback={null}><Phone src={href(fallback)} /></Suspense>
      </Canvas>
    </div>
  );
}
