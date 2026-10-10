import * as THREE from 'three';
import {clone} from 'three/examples/jsm/utils/SkeletonUtils.js';

// Retarget a Mixamo clip between two Mixamo-named characters whose bones have different
// rest orientations. Both are assumed to share a T-pose bind: each target bone copies the
// source bone's world-space rotation delta from that T-pose. Output: local quaternion tracks.
export function retarget(target: THREE.Object3D, source: THREE.Object3D, clip: THREE.AnimationClip, fps = 30) {
  const dst = clone(target);
  const src = clone(source);
  dst.updateMatrixWorld(true);
  src.updateMatrixWorld(true);

  const bones: THREE.Bone[] = [];
  dst.traverse((o) => {
    if ((o as THREE.Bone).isBone) bones.push(o as THREE.Bone);
  });
  const srcBone = new Map<string, THREE.Object3D>();
  src.traverse((o) => {
    if ((o as THREE.Bone).isBone) srcBone.set(o.name, o);
  });
  const worldQ = (o: THREE.Object3D) => o.getWorldQuaternion(new THREE.Quaternion());
  const restDst = new Map(bones.map((b) => [b.name, worldQ(b)]));
  const restSrcInv = new Map([...srcBone].map(([n, b]) => [n, worldQ(b).invert()]));
  const restLocal = new Map(bones.map((b) => [b.name, b.quaternion.clone()]));
  const staticParent = new Map(bones.map((b) => [b.name, b.parent && !(b.parent as THREE.Bone).isBone ? worldQ(b.parent) : null]));

  const mixer = new THREE.AnimationMixer(src);
  mixer.clipAction(clip).play();
  const frames = Math.max(2, Math.round(clip.duration * fps) + 1);
  const times = new Float32Array(frames);
  const values = new Map(bones.map((b) => [b.name, new Float32Array(frames * 4)]));

  for (let f = 0; f < frames; f++) {
    const t = Math.min(clip.duration, f / fps);
    times[f] = t;
    mixer.setTime(t);
    src.updateMatrixWorld(true);
    const solved = new Map<string, THREE.Quaternion>();
    for (const b of bones) {
      const parentWorld = staticParent.get(b.name) ?? solved.get(b.parent!.name)!;
      const s = srcBone.get(b.name);
      const world = s
        ? worldQ(s).multiply(restSrcInv.get(b.name)!).multiply(restDst.get(b.name)!)
        : parentWorld.clone().multiply(restLocal.get(b.name)!);
      solved.set(b.name, world);
      parentWorld.clone().invert().multiply(world).toArray(values.get(b.name)!, f * 4);
    }
  }
  const tracks = bones.map((b) => new THREE.QuaternionKeyframeTrack(`${b.name}.quaternion`, Array.from(times), Array.from(values.get(b.name)!)));
  return new THREE.AnimationClip(clip.name, clip.duration, tracks);
}
