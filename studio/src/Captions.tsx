import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import type {Scene, Word} from './Short';

const GROUP = 3;

// Word-by-word captions in groups of three, current word highlighted: the standard viral-shorts style.
export const Captions: React.FC<{scenes: Scene[]}> = ({scenes}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;

  const groups: Word[][] = [];
  for (const scene of scenes) {
    for (let i = 0; i < scene.words.length; i += GROUP) groups.push(scene.words.slice(i, i + GROUP));
  }
  const group = groups.find((g) => t >= g[0].s && t < g[g.length - 1].e + 0.05);
  if (!group) return null;

  const enter = spring({frame: frame - Math.round(group[0].s * fps), fps, config: {damping: 12, stiffness: 220}});
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 560}}>
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'center',
          gap: '0 38px',
          padding: '0 70px',
          transform: `scale(${0.85 + 0.15 * enter})`,
        }}
      >
        {group.map((word, i) => {
          const active = t >= word.s && t < word.e + 0.05;
          return (
            <span
              key={i}
              style={{
                fontFamily: 'Caption',
                fontSize: 104,
                lineHeight: 1.15,
                textTransform: 'uppercase',
                color: active ? '#ffd60a' : '#ffffff',
                WebkitTextStroke: '14px #000',
                paintOrder: 'stroke fill',
                textShadow: '0 8px 24px rgba(0,0,0,.55)',
                transform: active ? 'scale(1.04)' : 'none',
                display: 'inline-block',
              }}
            >
              {word.w}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
