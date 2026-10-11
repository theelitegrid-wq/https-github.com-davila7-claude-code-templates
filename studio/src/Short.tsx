import {
  AbsoluteFill,
  Audio,
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
  pose?: string;
  shot?: string;
  face?: string;
  cuts?: number[];
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

const SceneShell: React.FC<{scene: Scene; index: number; variant: number; offset: number}> = ({
  scene,
  index,
  variant,
  offset,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  // New scene: soft punch-in + light flash. Mid-scene angle change: punch only.
  const punch = interpolate(frame, [0, 8], [variant ? 1.03 : 1.05, 1], {extrapolateRight: 'clamp'});
  const flash = index === 0 || variant ? 0 : interpolate(frame, [0, 5], [0.35, 0], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{transform: `scale(${punch})`}}>
        <ThreeCanvas width={width} height={height} gl={{antialias: true, preserveDrawingBuffer: true}}>
          <SceneView scene={scene} index={index} variant={variant} offset={offset} />
        </ThreeCanvas>
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
            <SceneShell scene={scene} index={i} variant={j} offset={b / fps} />
          </Sequence>
        ));
      })}
      <Captions scenes={plan.scenes} />
      {plan.audio ? <Audio src={staticFile(plan.audio)} /> : null}
    </AbsoluteFill>
  );
};
