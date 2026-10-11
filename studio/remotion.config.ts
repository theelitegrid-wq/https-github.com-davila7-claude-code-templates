import {Config} from '@remotion/cli/config';

// Software WebGL so 3D renders on any CPU-only machine (GitHub Actions, laptops without a GPU).
Config.setChromiumOpenGlRenderer('swangle');
Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
Config.setCrf(18);
