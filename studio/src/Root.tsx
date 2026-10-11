import {Composition} from 'remotion';
import {Short, type Plan} from './Short';

const FPS = 30;

const samplePlan: Plan = {
  title: 'Sample',
  audio: null,
  scenes: [
    {narration: 'This is what happens inside your body.', type: 'body', focus: 'heart', color: '#4cc9f0', accent: '#ff3b5c', start: 0, duration: 3, words: []},
    {narration: 'Your blood starts racing.', type: 'tunnel', color: '#8d0f1f', accent: '#ff6b6b', callout: '120 BPM', start: 3, duration: 3, words: []},
  ],
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Short"
    component={Short}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={FPS * 6}
    defaultProps={samplePlan}
    calculateMetadata={({props}) => {
      const last = props.scenes[props.scenes.length - 1];
      return {durationInFrames: Math.ceil((last.start + last.duration + 0.6) * FPS)};
    }}
  />
);
