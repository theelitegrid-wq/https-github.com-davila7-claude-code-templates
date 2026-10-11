import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  OffthreadVideo,
  random,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import {SceneView} from './scenes';
import {Captions} from './Captions';

export type Word = {w: string; s: number; e: number};
export type Scene = {
  narration: string;
  type: string;
  color?: string;
  accent?: string;
  callout?: string;
  focus?: string;
  mode?: string;
  pose?: string;
  shot?: string;
  face?: string;
  cuts?: number[];
  media?: string; // AI-generated still (.png/.jpg) or clip (.mp4) in public/, e.g. shots/03.png
  motion?: string; // push | pull | pan-left | pan-right | up | down | shake
  start: number;
  duration: number;
  words: Word[];
};
export type Plan = {title: string; audio: string | null; scenes: Scene[]};

const fontFace = `@font-face{font-family:'Caption';src:url('${staticFile('fonts/BeVietnamPro-Bold.ttf')}') format('truetype');font-weight:700;}`;

const Callout: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: frame - 4, fps, config: {damping: 9, stiffness: 160}});
  const fade = interpolate(frame, [fps * 1.4, fps * 1.8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', top: 260, opacity: fade}}>
      <div
        style={{
          fontFamily: 'Caption',
          fontSize: 112,
          color: '#ffd60a',
          letterSpacing: -2,
          transform: `scale(${pop}) rotate(${interpolate(pop, [0, 1], [-8, -3])}deg)`,
          WebkitTextStroke: '8px #000',
          paintOrder: 'stroke fill',
          textShadow: '0 12px 40px rgba(0,0,0,.6)',
          textAlign: 'center',
          padding: '0 40px',
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};

// Camera move over an AI shot: [scale from, scale to, x from %, x to %, y from %, y to %].
const MOVES: Record<string, number[]> = {
  push: [1.04, 1.16, 0, 0, 0, 0],
  pull: [1.18, 1.04, 0, 0, 0, 0],
  'pan-left': [1.14, 1.14, 4, -4, 0, 0],
  'pan-right': [1.14, 1.14, -4, 4, 0, 0],
  up: [1.14, 1.14, 0, 0, 4, -4],
  down: [1.14, 1.14, 0, 0, -4, 4],
  shake: [1.1, 1.18, 0, 0, 0, 0],
};

const MediaShot: React.FC<{scene: Scene; index: number; variant: number; offset: number; dur: number}> = ({
  scene,
  index,
  variant,
  offset,
  dur,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(frame / fps, [0, Math.max(0.5, dur)], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.inOut(Easing.quad),
  });
  const name = scene.motion && MOVES[scene.motion] ? scene.motion : 'push';
  // Second angle: a tighter reframe drifting the other way, like a new camera setup.
  const m = variant ? [MOVES[name][1] * 1.12, MOVES[name][1] * 1.2, 3, -2, -3, 2] : MOVES[name];
  const scale = interpolate(p, [0, 1], [m[0], m[1]]);
  const x = interpolate(p, [0, 1], [m[2], m[3]]);
  const y = interpolate(p, [0, 1], [m[4], m[5]]);
  const hit = name === 'shake' && !variant ? Math.max(0, 1 - frame / (fps * 0.5)) : 0;
  const jx = hit * (random(`jx${index}-${frame}`) - 0.5) * 3;
  const jy = hit * (random(`jy${index}-${frame}`) - 0.5) * 3;
  const style: React.CSSProperties = {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    transform: `translate(${x + jx}%, ${y + jy}%) scale(${scale})`,
  };
  const src = staticFile(scene.media!);
  return scene.media!.endsWith('.mp4') ? (
    <OffthreadVideo src={src} muted startFrom={Math.round(offset * fps)} style={style} />
  ) : (
    <Img src={src} style={style} />
  );
};

const SceneShell: React.FC<{scene: Scene; index: number; variant: number; offset: number; dur: number}> = ({
  scene,
  index,
  variant,
  offset,
  dur,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  // New scene: soft punch-in + light flash. Mid-scene angle change: punch only.
  const punch = interpolate(frame, [0, 8], [variant ? 1.03 : 1.05, 1], {extrapolateRight: 'clamp'});
  const flash = index === 0 || variant ? 0 : interpolate(frame, [0, 5], [0.35, 0], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{transform: `scale(${punch})`, overflow: 'hidden'}}>
        {scene.media ? (
          <MediaShot scene={scene} index={index} variant={variant} offset={offset} dur={dur} />
        ) : (
          <ThreeCanvas width={width} height={height} gl={{antialias: true, preserveDrawingBuffer: true}}>
            <SceneView scene={scene} index={index} variant={variant} offset={offset} />
          </ThreeCanvas>
        )}
      </AbsoluteFill>
      <AbsoluteFill
        style={{background: 'radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,.75) 100%)'}}
      />
      {scene.callout && variant === 0 ? <Callout text={scene.callout} /> : null}
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    </AbsoluteFill>
  );
};

export const Short: React.FC<Plan> = (plan) => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: '#05060a'}}>
      <style>{fontFace}</style>
      {plan.scenes.map((scene, i) => {
        const from = Math.round(scene.start * fps);
        const next = plan.scenes[i + 1];
        const end = next ? Math.round(next.start * fps) : Math.ceil((scene.start + scene.duration + 0.6) * fps);
        // Split long scenes into two camera angles (a new shot every ~2-3 s).
        const bounds = [0, ...(scene.cuts ?? []).map((c) => Math.round(c * fps)), end - from];
        return bounds.slice(0, -1).map((b, j) => (
          <Sequence key={`${i}-${j}`} from={from + b} durationInFrames={Math.max(1, bounds[j + 1] - b)}>
            <SceneShell scene={scene} index={i} variant={j} offset={b / fps} dur={(bounds[j + 1] - b) / fps} />
          </Sequence>
        ));
      })}
      <Captions scenes={plan.scenes} />
      {plan.audio ? <Audio src={staticFile(plan.audio)} /> : null}
    </AbsoluteFill>
  );
};
