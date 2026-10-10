// Procedural 3D scene library. Everything is driven by the Remotion frame, so renders are
// deterministic and need no GPU, assets or network.
import * as THREE from 'three';
import {useLayoutEffect, useMemo, useRef} from 'react';
import {useThree} from '@react-three/fiber';
import {useGLTF} from '@react-three/drei';
import {interpolate, random, staticFile, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {mergeVertices} from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import {clone as cloneSkinned} from 'three/examples/jsm/utils/SkeletonUtils.js';
import {retarget} from './retarget';
import type {Scene} from './Short';

type V3 = [number, number, number];
type SceneProps = {color: string; accent: string; t: number; dur: number; seed: string; focus?: string};

export const SCENE_TYPES = ['person', 'body', 'tunnel', 'blob', 'planet', 'shatter', 'virus'] as const;

const ease = (t: number, a: number, b: number, from: number, to: number) =>
  interpolate(t, [a, b], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.cubic),
  });

const fibonacciSphere = (n: number): V3[] =>
  Array.from({length: n}, (_, i) => {
    const y = 1 - (i / (n - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const phi = i * Math.PI * (3 - Math.sqrt(5));
    return [Math.cos(phi) * r, y, Math.sin(phi) * r];
  });

const Rig: React.FC<{pos: V3; look?: V3; fov?: number}> = ({pos, look = [0, 0, 0], fov = 40}) => {
  const {camera} = useThree();
  useLayoutEffect(() => {
    const cam = camera as THREE.PerspectiveCamera;
    cam.fov = fov;
    cam.near = 0.05;
    cam.far = 200;
    cam.position.set(...pos);
    cam.lookAt(...look);
    cam.updateProjectionMatrix();
  });
  return null;
};

const Backdrop: React.FC<{color: string; fog?: [number, number]}> = ({color, fog}) => {
  const bg = useMemo(() => new THREE.Color(color).multiplyScalar(0.07), [color]);
  return (
    <>
      <color attach="background" args={[bg]} />
      {fog ? <fog attach="fog" args={[bg, fog[0], fog[1]]} /> : null}
    </>
  );
};

type Placement = {p: V3; s: V3; r: V3};
const Swarm: React.FC<{
  count: number;
  geometry: THREE.BufferGeometry;
  place: (i: number) => Placement;
  children: React.ReactNode;
}> = ({count, geometry, place, children}) => {
  const ref = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  useLayoutEffect(() => {
    const mesh = ref.current!;
    for (let i = 0; i < count; i++) {
      const {p, s, r} = place(i);
      dummy.position.set(...p);
      dummy.scale.set(...s);
      dummy.rotation.set(...r);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  });
  return (
    <instancedMesh ref={ref} args={[geometry, undefined, count]}>
      {children}
    </instancedMesh>
  );
};

const Dust: React.FC<{seed: string; t: number; color: string; count?: number; spread?: number}> = ({
  seed,
  t,
  color,
  count = 90,
  spread = 7,
}) => {
  const geo = useMemo(() => new THREE.SphereGeometry(0.03, 8, 6), []);
  return (
    <Swarm
      count={count}
      geometry={geo}
      place={(i) => {
        const rx = random(`${seed}dx${i}`) - 0.5;
        const ry = random(`${seed}dy${i}`) - 0.5;
        const rz = random(`${seed}dz${i}`);
        const y = ((ry * spread + t * 0.15 * (0.5 + rz)) % spread) - spread / 2;
        const s = 0.5 + rz * 1.5;
        return {p: [rx * spread, y, -rz * spread], s: [s, s, s], r: [0, 0, 0]};
      }}
    >
      <meshBasicMaterial color={color} transparent opacity={0.5} />
    </Swarm>
  );
};

// ---------- organic blob: heart, brain, cell, stomach, any organ or creature ----------
const Blob: React.FC<SceneProps> = ({color, accent, t, seed}) => {
  const geo = useMemo(() => {
    const g = new THREE.IcosahedronGeometry(1.35, 40);
    g.deleteAttribute('normal');
    g.deleteAttribute('uv');
    return mergeVertices(g);
  }, []);
  const base = useMemo(() => Float32Array.from(geo.attributes.position.array as ArrayLike<number>), [geo]);
  useLayoutEffect(() => {
    const attr = geo.attributes.position as THREE.BufferAttribute;
    const a = attr.array as Float32Array;
    const beat = Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 1.1)), 6) * 0.07;
    for (let i = 0; i < a.length; i += 3) {
      const x = base[i], y = base[i + 1], z = base[i + 2];
      const n =
        Math.sin(x * 2.6 + t * 1.8) * Math.sin(y * 3.1 + t * 1.3) * Math.sin(z * 2.2 + t * 1.6) +
        0.45 * Math.sin(x * 5.3 - t * 2.1 + y * 4.1) * Math.sin(z * 4.7 + t);
      const r = 1 + 0.12 * n + beat;
      a[i] = x * r;
      a[i + 1] = y * r;
      a[i + 2] = z * r;
    }
    attr.needsUpdate = true;
    geo.computeVertexNormals();
  });
  const z = ease(t, 0, 6, 8.6, 7.4);
  return (
    <>
      <Backdrop color={color} fog={[6, 18]} />
      <Rig pos={[Math.sin(t * 0.3) * 0.8, 0.25 + Math.sin(t * 0.5) * 0.15, z]} />
      <ambientLight intensity={0.25} />
      <directionalLight position={[3, 4, 5]} intensity={2.6} />
      <pointLight position={[-3, 2, -2.5]} color={accent} intensity={60} />
      <pointLight position={[3, -2, 1]} color={accent} intensity={14} />
      <group rotation={[0.3, t * 0.35, 0]}>
        <mesh geometry={geo}>
          <meshPhysicalMaterial
            color={color}
            roughness={0.26}
            clearcoat={1}
            clearcoatRoughness={0.12}
            sheen={1}
            sheenColor={accent}
            emissive={color}
            emissiveIntensity={0.1}
          />
        </mesh>
      </group>
      <Dust seed={seed} t={t} color={accent} />
    </>
  );
};

// ---------- tunnel: flying through a blood vessel, throat, gut, cave, pipe ----------
const Tunnel: React.FC<SceneProps> = ({color, accent, t, seed}) => {
  const L = 90;
  const wall = useMemo(() => {
    const g = new THREE.CylinderGeometry(2.2, 2.2, L, 80, 260, true);
    g.rotateX(Math.PI / 2);
    const a = g.attributes.position.array as Float32Array;
    for (let i = 0; i < a.length; i += 3) {
      const ang = Math.atan2(a[i + 1], a[i]);
      const z = a[i + 2];
      const r = 2.2 * (1 + 0.13 * Math.sin(z * 1.5) + 0.05 * Math.sin(ang * 7 + z * 0.8) + 0.03 * Math.sin(ang * 19 - z * 2.3));
      a[i] = Math.cos(ang) * r;
      a[i + 1] = Math.sin(ang) * r;
    }
    g.computeVertexNormals();
    return g;
  }, []);
  const cell = useMemo(() => new THREE.SphereGeometry(0.3, 28, 18), []);
  const camZ = 38 - t * 4.2;
  return (
    <>
      <Backdrop color={color} fog={[1.5, 20]} />
      <Rig pos={[Math.sin(t * 0.9) * 0.35, Math.cos(t * 0.7) * 0.3, camZ]} look={[0, 0, camZ - 10]} fov={55} />
      <ambientLight intensity={0.15} />
      <pointLight position={[0, 0.6, camZ - 1]} color="#ffd9c7" intensity={35} distance={18} />
      <pointLight position={[0, 0, camZ - 12]} color={accent} intensity={80} distance={26} />
      <mesh geometry={wall}>
        <meshStandardMaterial color={color} side={THREE.BackSide} roughness={0.45} emissive={color} emissiveIntensity={0.12} />
      </mesh>
      <Swarm
        count={140}
        geometry={cell}
        place={(i) => {
          const ang = random(`${seed}a${i}`) * Math.PI * 2;
          const rad = 0.3 + random(`${seed}r${i}`) * 1.3;
          const span = 46;
          const z0 = random(`${seed}z${i}`) * span;
          const z = camZ + 4 - ((z0 + t * 2.2) % span);
          return {
            p: [Math.cos(ang) * rad, Math.sin(ang) * rad, z],
            s: [1, 0.36, 1],
            r: [random(`${seed}x${i}`) * 6 + t * 0.8, random(`${seed}y${i}`) * 6, t * 0.5],
          };
        }}
      >
        <meshPhysicalMaterial color={accent} roughness={0.35} clearcoat={0.6} emissive={accent} emissiveIntensity={0.15} />
      </Swarm>
    </>
  );
};

// ---------- planet: Earth, sun, moon, space, climate, scale ----------
const Planet: React.FC<SceneProps> = ({color, accent, t, seed}) => {
  const geo = useMemo(() => {
    const g = new THREE.SphereGeometry(1.6, 160, 120);
    const pos = g.attributes.position.array as Float32Array;
    const c1 = new THREE.Color(color), c2 = new THREE.Color(accent), out = new THREE.Color();
    const colors = new Float32Array(pos.length);
    for (let i = 0; i < pos.length; i += 3) {
      const x = pos[i], y = pos[i + 1], z = pos[i + 2];
      const n = Math.sin(x * 3.1 + Math.sin(z * 2.3) * 1.7) * Math.cos(y * 2.7 - x * 1.3) + 0.4 * Math.sin(z * 7.1 + y * 5.3);
      const band = 0.5 + 0.5 * Math.sin(y * 7 + n * 1.6);
      out.copy(c1).lerp(c2, n > 0.25 ? 0.85 : band * 0.35).multiplyScalar(0.75 + 0.25 * band);
      colors[i] = out.r;
      colors[i + 1] = out.g;
      colors[i + 2] = out.b;
    }
    g.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    return g;
  }, [color, accent]);
  const stars = useMemo(() => {
    const p = new Float32Array(2400 * 3);
    for (let i = 0; i < 2400; i++) {
      const th = random(`${seed}st${i}`) * Math.PI * 2;
      const u = random(`${seed}su${i}`) * 2 - 1;
      const r = 40 + random(`${seed}sr${i}`) * 20;
      const s = Math.sqrt(1 - u * u);
      p[i * 3] = Math.cos(th) * s * r;
      p[i * 3 + 1] = u * r;
      p[i * 3 + 2] = Math.sin(th) * s * r;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(p, 3));
    return g;
  }, [seed]);
  const z = ease(t, 0, 6, 9.5, 7.8);
  return (
    <>
      <color attach="background" args={['#020308']} />
      <Rig pos={[0.4, 0.2 + t * 0.03, z]} />
      <ambientLight intensity={0.06} />
      <directionalLight position={[5, 2, 3]} intensity={3.2} />
      <group rotation={[0.25, t * 0.25, 0.1]}>
        <mesh geometry={geo}>
          <meshStandardMaterial vertexColors roughness={0.75} />
        </mesh>
      </group>
      {[1.03, 1.08, 1.15].map((s, i) => (
        <mesh key={s} scale={s}>
          <sphereGeometry args={[1.6, 64, 48]} />
          <meshBasicMaterial color={accent} transparent opacity={[0.5, 0.25, 0.1][i]} side={THREE.BackSide} blending={THREE.AdditiveBlending} depthWrite={false} />
        </mesh>
      ))}
      <points geometry={stars}>
        <pointsMaterial size={0.14} color="#ffffff" />
      </points>
    </>
  );
};

// ---------- shatter: explosion, breaking, collapse, impact ----------
const Shatter: React.FC<SceneProps> = ({color, accent, t, dur, seed}) => {
  const N = 260;
  const dirs = useMemo(() => fibonacciSphere(N), []);
  const shard = useMemo(() => new THREE.TetrahedronGeometry(0.24), []);
  const t0 = Math.min(1.4, dur * 0.35);
  const dt = Math.max(0, t - t0);
  const charge = Math.min(1, t / t0);
  const shake = t > t0 ? 0.12 * Math.exp(-dt * 4) : 0.01 * charge;
  const z = 8.4 + dt * 0.6;
  return (
    <>
      <Backdrop color={color} fog={[5, 18]} />
      <Rig pos={[Math.sin(t * 61) * shake, Math.cos(t * 47) * shake + 0.2, z]} />
      <ambientLight intensity={0.2} />
      <directionalLight position={[3, 4, 5]} intensity={2.2} />
      <pointLight
        position={[0, 0, 0]}
        color={accent}
        intensity={t < t0 ? 5 + 60 * Math.pow(charge, 3) : 300 * Math.exp(-dt * 2.2)}
        distance={14}
      />
      <mesh scale={t < t0 ? 1.02 + 0.06 * charge : 1.05 + dt * 3}>
        <sphereGeometry args={[1, 48, 32]} />
        <meshBasicMaterial
          color={accent}
          transparent
          opacity={t < t0 ? 0.25 * charge : 0.9 * Math.exp(-dt * 2.5)}
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
      <Swarm
        count={N}
        geometry={shard}
        place={(i) => {
          const d = dirs[i];
          const speed = 2.2 + random(`${seed}v${i}`) * 3;
          const tremble = t < t0 ? 1 + 0.02 * Math.sin(t * 50 + i) * charge : 1;
          const k = 1.15 * tremble + dt * speed;
          const fall = dt * dt * 0.35;
          const spin = dt * (2 + random(`${seed}s${i}`) * 5);
          const s = 0.8 + random(`${seed}k${i}`) * 0.7;
          return {
            p: [d[0] * k, d[1] * k - fall, d[2] * k],
            s: [s, s, s],
            r: [random(`${seed}rx${i}`) * 6 + spin, random(`${seed}ry${i}`) * 6 + spin * 0.7, 0],
          };
        }}
      >
        <meshPhysicalMaterial color={color} roughness={0.3} metalness={0.25} clearcoat={1} emissive={accent} emissiveIntensity={0.06} />
      </Swarm>
    </>
  );
};

// ---------- virus: germs, bacteria, infection, disease, parasites ----------
const VirusBody: React.FC<{color: string; accent: string; spikes: number}> = ({color, accent, spikes}) => {
  const dirs = useMemo(() => fibonacciSphere(spikes), [spikes]);
  return (
    <group>
      <mesh>
        <icosahedronGeometry args={[1, 6]} />
        <meshPhysicalMaterial color={color} roughness={0.45} clearcoat={0.6} sheen={1} sheenColor={accent} />
      </mesh>
      {dirs.map((d, i) => {
        const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(...d));
        return (
          <group key={i} quaternion={q}>
            <mesh position={[0, 1.18, 0]}>
              <cylinderGeometry args={[0.035, 0.06, 0.4, 8]} />
              <meshStandardMaterial color={color} roughness={0.5} />
            </mesh>
            <mesh position={[0, 1.42, 0]}>
              <sphereGeometry args={[0.1, 16, 12]} />
              <meshStandardMaterial color={accent} emissive={accent} emissiveIntensity={0.45} roughness={0.3} />
            </mesh>
          </group>
        );
      })}
    </group>
  );
};

const Virus: React.FC<SceneProps> = ({color, accent, t, seed}) => {
  const others = useMemo(
    () =>
      Array.from({length: 7}, (_, i) => ({
        p: [(random(`${seed}ox${i}`) - 0.5) * 9, (random(`${seed}oy${i}`) - 0.5) * 12, -3 - random(`${seed}oz${i}`) * 7] as V3,
        s: 0.35 + random(`${seed}os${i}`) * 0.35,
        ph: random(`${seed}op${i}`) * 6,
      })),
    [seed],
  );
  const z = ease(t, 0, 6, 8.4, 7.2);
  return (
    <>
      <Backdrop color={color} fog={[5, 18]} />
      <Rig pos={[Math.sin(t * 0.4) * 0.6, 0.2, z]} />
      <ambientLight intensity={0.25} />
      <directionalLight position={[3, 4, 5]} intensity={2.4} />
      <pointLight position={[-3, 2, -2]} color={accent} intensity={50} />
      <group rotation={[t * 0.2, t * 0.45, 0]}>
        <VirusBody color={color} accent={accent} spikes={56} />
      </group>
      {others.map((o, i) => (
        <group key={i} position={[o.p[0], o.p[1] + Math.sin(t * 0.8 + o.ph) * 0.3, o.p[2]]} scale={o.s} rotation={[t * 0.3 + o.ph, t * 0.4, 0]}>
          <VirusBody color={color} accent={accent} spikes={26} />
        </group>
      ))}
      <Dust seed={seed} t={t} color={accent} count={60} />
    </>
  );
};

// ---------- body: x-ray human with a glowing organ (what happens to your body if...) ----------
const FOCUS: Record<string, {p: V3; r: number}> = {
  brain: {p: [0, 1.66, 0.02], r: 0.2},
  head: {p: [0, 1.62, 0.02], r: 0.26},
  eyes: {p: [0, 1.66, 0.27], r: 0.08},
  heart: {p: [0.08, 1.02, 0.12], r: 0.13},
  lungs: {p: [0, 1.02, 0.05], r: 0.26},
  chest: {p: [0, 1.0, 0.1], r: 0.24},
  stomach: {p: [0.06, 0.72, 0.13], r: 0.15},
  liver: {p: [-0.13, 0.8, 0.1], r: 0.14},
  gut: {p: [0, 0.45, 0.12], r: 0.2},
  kidneys: {p: [0, 0.62, -0.08], r: 0.14},
  bones: {p: [0.18, -0.4, 0], r: 0.2},
  legs: {p: [0.18, -0.4, 0], r: 0.22},
  skin: {p: [0, 0.6, 0.1], r: 0.35},
  blood: {p: [0.08, 1.02, 0.12], r: 0.18},
};

const BODY_PARTS: {p: V3; r: number; l: number; rot?: V3; s?: V3; sphere?: boolean}[] = [
  {p: [0, 1.64, 0], r: 0.3, l: 0, sphere: true},
  {p: [0, 1.32, 0], r: 0.09, l: 0.12},
  {p: [0, 0.88, 0], r: 0.36, l: 0.5, s: [1, 1, 0.62]},
  {p: [0, 0.38, 0], r: 0.3, l: 0.08, s: [1.08, 1, 0.66]},
  {p: [0.52, 1.0, 0], r: 0.1, l: 0.42, rot: [0, 0, 0.16]},
  {p: [-0.52, 1.0, 0], r: 0.1, l: 0.42, rot: [0, 0, -0.16]},
  {p: [0.6, 0.48, 0.04], r: 0.085, l: 0.42, rot: [-0.1, 0, 0.06]},
  {p: [-0.6, 0.48, 0.04], r: 0.085, l: 0.42, rot: [-0.1, 0, -0.06]},
  {p: [0.18, -0.08, 0], r: 0.14, l: 0.52},
  {p: [-0.18, -0.08, 0], r: 0.14, l: 0.52},
  {p: [0.19, -0.74, 0], r: 0.11, l: 0.52},
  {p: [-0.19, -0.74, 0], r: 0.11, l: 0.52},
];

const Body: React.FC<SceneProps> = ({color, accent, t, dur, focus, seed}) => {
  const f = FOCUS[(focus || 'heart').toLowerCase()] ?? FOCUS.heart;
  const beat = Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 1.2)), 8);
  const k = ease(t, 0, Math.max(2, dur), 0, 1);
  const angle = -0.6 + t * 0.22;
  const radius = 5.6 - 0.8 * k;
  const look: V3 = [f.p[0] * k * 0.6, 0.55 + (f.p[1] - 0.55) * k * 0.6, 0];
  const scanY = -1.25 + ((t * 0.7) % 1) * 3.2;
  return (
    <>
      <Backdrop color={color} fog={[3, 12]} />
      <Rig pos={[Math.sin(angle) * radius, look[1] + 0.35, Math.cos(angle) * radius]} look={look} />
      <ambientLight intensity={0.35} />
      <directionalLight position={[2, 4, 4]} intensity={1.2} />
      <pointLight position={f.p} color={accent} intensity={6 + 10 * beat} distance={3} />
      {BODY_PARTS.map((part, i) => (
        <group key={i} position={part.p} rotation={part.rot ?? [0, 0, 0]} scale={part.s ?? [1, 1, 1]}>
          <mesh>
            {part.sphere ? <sphereGeometry args={[part.r, 40, 28]} /> : <capsuleGeometry args={[part.r, part.l, 12, 24]} />}
            <meshPhysicalMaterial color={color} transparent opacity={0.22} roughness={0.15} emissive={color} emissiveIntensity={0.35} depthWrite={false} />
          </mesh>
          <mesh>
            {part.sphere ? <sphereGeometry args={[part.r * 1.002, 18, 12]} /> : <capsuleGeometry args={[part.r * 1.002, part.l, 6, 12]} />}
            <meshBasicMaterial color={color} wireframe transparent opacity={0.1} />
          </mesh>
        </group>
      ))}
      <mesh position={f.p} scale={1 + 0.18 * beat}>
        <sphereGeometry args={[f.r, 32, 24]} />
        <meshStandardMaterial color={accent} emissive={accent} emissiveIntensity={1.4} roughness={0.4} />
      </mesh>
      <mesh position={f.p} scale={2.2 + 0.5 * beat}>
        <sphereGeometry args={[f.r, 24, 16]} />
        <meshBasicMaterial color={accent} transparent opacity={0.18} blending={THREE.AdditiveBlending} depthWrite={false} />
      </mesh>
      <mesh position={[0, scanY, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.75, 0.008, 8, 96]} />
        <meshBasicMaterial color={accent} transparent opacity={0.8} />
      </mesh>
      <gridHelper args={[12, 48, accent, '#16303f']} position={[0, -1.32, 0]} />
      <Dust seed={seed} t={t} color={color} count={50} />
    </>
  );
};

// ---------- person: a realistic everyday person (Mixamo character + Mixamo motion) ----------
// Models are downloaded by setup.sh into public/models (not committed: third-party assets).
// Default person.glb is Michelle from the three.js examples (a Mixamo character).
// Any Mixamo character works (download from mixamo.com as FBX, convert to .glb, save as person.glb).
const PERSON_URL = staticFile('models/person.glb');
const MOTION_URL = staticFile('models/Xbot.glb');

// pose -> [looping base clip, optional additive pose layered on top]
const POSES: Record<string, [string, string?]> = {
  idle: ['idle'],
  tired: ['idle', 'sad_pose'],
  sad: ['idle', 'sad_pose'],
  no: ['idle', 'headShake'],
  yes: ['idle', 'agree'],
  sneak: ['idle', 'sneak_pose'],
  walk: ['walk'],
  run: ['run'],
};

const FACES: Record<string, {mouthOpen: number; mouthSmile: number}> = {
  neutral: {mouthOpen: 0, mouthSmile: 0},
  smile: {mouthOpen: 0.05, mouthSmile: 0.7},
  shocked: {mouthOpen: 0.75, mouthSmile: 0},
  scared: {mouthOpen: 0.45, mouthSmile: 0},
};

// Where to put the inner glow for each organ: [bone, offset in metres].
// Offsets are in the bone's local space (Mixamo bones are in centimetres).
const ORGANS: Record<string, [string, V3, number]> = {
  brain: ['mixamorigHead', [0, 17, -2], 0.05],
  head: ['mixamorigHead', [0, 10, -1], 0.07],
  eyes: ['mixamorigHead', [0, 8, 9], 0.025],
  heart: ['mixamorigSpine2', [3, 2, 6], 0.045],
  lungs: ['mixamorigSpine2', [0, 2, 3], 0.1],
  chest: ['mixamorigSpine2', [0, 2, 5], 0.09],
  blood: ['mixamorigSpine2', [3, 2, 6], 0.06],
  stomach: ['mixamorigSpine', [3, 0, 9], 0.05],
  liver: ['mixamorigSpine1', [-6, 4, 5], 0.055],
  gut: ['mixamorigSpine', [0, -3, 6], 0.07],
  kidneys: ['mixamorigSpine', [0, 4, -4], 0.05],
  bones: ['mixamorigLeftLeg', [0, 15, 0], 0.06],
  legs: ['mixamorigLeftUpLeg', [0, 20, 0], 0.07],
  skin: ['mixamorigSpine1', [0, 0, 10], 0.12],
};

// Camera framings relative to the character's face height (y) so any model is framed right.
const SHOTS: Record<string, (face: number) => {pos: V3; look: V3}> = {
  full: (y) => ({pos: [0, y * 0.6, 5.4], look: [0, y * 0.52, 0]}),
  medium: (y) => ({pos: [0, y - 0.1, 3.2], look: [0, y - 0.38, 0]}),
  close: (y) => ({pos: [0, y - 0.05, 1.8], look: [0, y - 0.15, 0]}),
};

const shadowTexture = (() => {
  if (typeof document === 'undefined') return null;
  const c = document.createElement('canvas');
  c.width = c.height = 128;
  const g = c.getContext('2d')!;
  const grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grad.addColorStop(0, 'rgba(0,0,0,0.55)');
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
})();

type PersonProps = SceneProps & {pose?: string; shot?: string; face?: string};

const Person: React.FC<PersonProps> = ({color, accent, t, dur, focus, pose = 'idle', shot = 'medium', face = 'neutral'}) => {
  const person = useGLTF(PERSON_URL);
  const motion = useGLTF(MOTION_URL);
  const model = useMemo(() => cloneSkinned(person.scene), [person]);
  const clips = useMemo(() => {
    const out: Record<string, THREE.AnimationClip> = {};
    for (const clip of motion.animations) out[clip.name] = retarget(person.scene, motion.scene, clip);
    return out;
  }, [person, motion]);
  const mixer = useMemo(() => new THREE.AnimationMixer(model), [model]);
  const [baseName, layerName] = POSES[pose] ?? POSES.idle;
  useLayoutEffect(() => {
    mixer.stopAllAction();
    mixer.uncacheRoot(model);
    mixer.clipAction(clips[baseName] ?? clips.idle).play();
    if (layerName && clips[layerName]) {
      const layer = THREE.AnimationUtils.makeClipAdditive(clips[layerName].clone());
      const action = mixer.clipAction(layer);
      action.blendMode = THREE.AdditiveAnimationBlendMode;
      action.play();
    }
  }, [mixer, model, clips, baseName, layerName]);

  const organ = focus ? ORGANS[focus.toLowerCase()] : undefined;
  const glow = useRef<THREE.Group>(null);
  useLayoutEffect(() => {
    mixer.setTime(t);
    model.updateMatrixWorld(true);
    const expr = FACES[face] ?? FACES.neutral;
    model.traverse((o) => {
      const mesh = o as THREE.Mesh;
      if (mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
        for (const [k, v] of Object.entries(expr)) {
          const idx = mesh.morphTargetDictionary[k];
          if (idx !== undefined) mesh.morphTargetInfluences[idx] = v;
        }
      }
    });
    if (organ && glow.current) {
      const bone = model.getObjectByName(organ[0]);
      if (bone) glow.current.position.copy(bone.localToWorld(new THREE.Vector3(...organ[1])));
    }
  });

  const faceY = useMemo(() => {
    const rest = cloneSkinned(person.scene);
    rest.updateMatrixWorld(true);
    const v = new THREE.Vector3();
    rest.getObjectByName('mixamorigHead')?.getWorldPosition(v);
    return v.y + 0.08;
  }, [person]);
  const s = (SHOTS[shot] ?? SHOTS.medium)(faceY);
  const push = ease(t, 0, Math.max(2, dur), 1, 0.95);
  const orbit = -0.25 + t * 0.06;
  const dist = Math.hypot(s.pos[0], s.pos[2]) * push;
  const beat = Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 1.2)), 8);
  const wall = useMemo(() => new THREE.Color(color).multiplyScalar(0.35), [color]);
  return (
    <>
      <color attach="background" args={[wall]} />
      <fog attach="fog" args={[wall, 6, 16]} />
      <Rig pos={[Math.sin(orbit) * dist, s.pos[1], Math.cos(orbit) * dist]} look={s.look} fov={32} />
      <hemisphereLight args={['#fff4e6', '#3a2f28', 1.4]} />
      <directionalLight position={[2.5, 4, 3]} intensity={2.4} color="#fff1dc" />
      <directionalLight position={[-3, 2.5, -2]} intensity={2.2} color={accent} />
      <directionalLight position={[0, 2, 4]} intensity={0.6} />
      <primitive object={model} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.002, 0]}>
        <planeGeometry args={[1.3, 1.3]} />
        <meshBasicMaterial map={shadowTexture} transparent depthWrite={false} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 30]} />
        <meshStandardMaterial color="#8a7a6a" roughness={0.85} />
      </mesh>
      <mesh position={[0, 3, -3]}>
        <planeGeometry args={[30, 8]} />
        <meshStandardMaterial color={color} roughness={0.95} />
      </mesh>
      {organ ? (
        <group ref={glow}>
          <mesh scale={1 + 0.2 * beat}>
            <sphereGeometry args={[organ[2], 24, 16]} />
            <meshBasicMaterial color={accent} transparent opacity={0.7} blending={THREE.AdditiveBlending} depthTest={false} depthWrite={false} />
          </mesh>
          <mesh scale={1.9 + 0.5 * beat} renderOrder={2}>
            <sphereGeometry args={[organ[2], 24, 16]} />
            <meshBasicMaterial color={accent} transparent opacity={0.15} blending={THREE.AdditiveBlending} depthTest={false} depthWrite={false} />
          </mesh>
        </group>
      ) : null}
    </>
  );
};

useGLTF.preload(PERSON_URL);
useGLTF.preload(MOTION_URL);

const COMPONENTS: Record<string, React.FC<PersonProps>> = {
  person: Person,
  body: Body,
  tunnel: Tunnel,
  blob: Blob,
  planet: Planet,
  shatter: Shatter,
  virus: Virus,
};

export const SceneView: React.FC<{scene: Scene; index: number}> = ({scene, index}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const Component = COMPONENTS[scene.type] ?? Blob;
  return (
    <Component
      color={scene.color || '#4cc9f0'}
      accent={scene.accent || '#ff3b5c'}
      t={frame / fps}
      dur={scene.duration}
      focus={scene.focus}
      pose={scene.pose}
      shot={scene.shot}
      face={scene.face}
      seed={`s${index}`}
    />
  );
};
