---
name: threejs-r3f
description: "Three.js and React Three Fiber sub-skill - 3D scenes, shaders, postprocessing."
---

> **Version-sensitive.** Every API name, SDK gate and browser-support claim below was
> verified on **2026-09-08** against primary sources. What against, and when, is in
> `_jutsu/VERSIONS.md`. If that date is old, re-verify before acting on a version number.

# Three.js & React Three Fiber

> 3D on the web. Three.js is the engine, R3F is the React renderer.
> Concise rules here. Deep-dive in `references/`.
>
> **Versions:** `three` r185 (`0.185.x`) · `@react-three/fiber` 9.x · `@react-three/drei` 10.x · `@react-three/postprocessing` 3.x.
> **R3F 9 is React 19 only** — its declared peer range is `react` / `react-dom` `>=19 <19.3` (drei 10 asks `^19`). React 18 projects must stay on R3F 8 + drei 9. Check the installed React major before scaffolding.
> **Renderers:** `WebGLRenderer` is still R3F's default. `WebGPURenderer` + TSL is shipped (not flagged) and self-falls-back to WebGL 2, but three's docs call it "the new alternative of `WebGLRenderer`", not the default. Opt in with an async `gl` callback:
> ```tsx
> import * as THREE from 'three/webgpu'
> <Canvas gl={async (props) => { const r = new THREE.WebGPURenderer(props as any); await r.init(); return r }} />
> ```

---

## When to Use What

| Need | Tool | Why |
|---|---|---|
| Full 3D scene (models, lights, physics) | R3F + drei | Declarative, React-friendly, ecosystem |
| Vanilla 3D (no React) | Three.js direct | Lighter, no React overhead |
| Simple 3D transforms on UI | CSS `transform3d` | GPU-composited, no WebGL context |
| 2D particles / generative | Canvas 2D | Simpler API, less GPU overhead |
| Shader-only visuals (no scene graph) | Raw WebGL / ShaderMaterial | Maximum control, minimal abstraction |

---

## Scene Setup Patterns

```tsx
import { Canvas } from '@react-three/fiber'
import { Environment, OrbitControls } from '@react-three/drei'
import { Suspense } from 'react'

<Canvas camera={{ position: [0, 2, 5], fov: 45 }} dpr={[1, 2]} gl={{ antialias: true }}>
  <Suspense fallback={null}>
    <Environment preset="studio" />
    <OrbitControls makeDefault />
    <Scene />
  </Suspense>
</Canvas>
```

**Rules:**
- Always wrap scene content in `<Suspense>` -- loaders (GLTF, textures, HDRI) need it
- Set `dpr={[1, 2]}` to clamp pixel ratio (Retina without melting GPUs)
- Keep the Canvas parent component minimal -- re-renders propagate into the scene

---

## R3F Hooks

| Hook | Purpose | Gotcha |
|---|---|---|
| `useFrame((state, delta) => {})` | Per-frame logic (animation, physics) | Never setState inside |
| `useThree()` | Access gl, scene, camera, size, viewport, pointer | Destructure only what you need |
| `useLoader(TextureLoader, url)` | Load any Three.js resource | Wrap parent in Suspense |
| `useGraph(scene)` | Extract nodes/materials from loaded scene | Useful after useGLTF |

### useFrame Tips

```tsx
useFrame((state, delta) => {
  // Use delta for framerate-independent animation
  meshRef.current.rotation.y += delta * 0.5
  // Access clock for time-based effects
  material.uniforms.uTime.value = state.clock.elapsedTime
})
```

---

## Drei Essentials

| Component | Use Case |
|---|---|
| `Environment` | HDRI lighting (presets: studio, sunset, city, forest, dawn) |
| `Float` | Idle floating animation (speed, rotationIntensity, floatIntensity) |
| `Text3D` | Extruded 3D text (needs JSON font from Facetype.js) |
| `useGLTF` | Load .glb/.gltf models (returns { nodes, materials, scene }) |
| `useGLTF.preload(url)` | Preload model before component mounts |
| `MeshTransmissionMaterial` | Glass/crystal/liquid refraction effects |
| `PresentationControls` | Drag-to-rotate for product showcases |
| `Center` | Auto-center any group of meshes |
| `Detailed` | LOD -- swap geometry by camera distance |
| `useTexture` | Load textures with Suspense support |
| `Instances` | Declarative instancing for repeated meshes |

---

## Postprocessing

```tsx
import { EffectComposer, Bloom, ChromaticAberration } from '@react-three/postprocessing'
import { BlendFunction } from 'postprocessing'

<EffectComposer>
  <Bloom
    luminanceThreshold={1}
    luminanceSmoothing={0.4}
    intensity={0.6}
  />
  <ChromaticAberration
    blendFunction={BlendFunction.NORMAL}
    offset={[0.002, 0.002]}
  />
</EffectComposer>
```

**Rules:**
- Bloom is selective by default -- lift material color/emissive above 1.0 to make it glow
- `luminanceThreshold={1}` = nothing glows unless explicitly emissive
- Order matters inside EffectComposer
- Effects are merged into a single pass (performant by design)

---

## Performance Patterns

| Pattern | When |
|---|---|
| `<Instances>` / `InstancedMesh` | 100+ identical meshes (particles, trees, crowds) |
| `<Detailed distances={[0, 50, 100]}>` | LOD: swap hi/lo models by distance |
| `dispose={null}` on `<primitive>` | Prevent auto-dispose when reusing shared geometry |
| `useGLTF` + Draco | Compress .glb models (70-90% size reduction) |
| `useTexture` + KTX2 | Compressed GPU textures (1/4 VRAM) |
| `frameloop="demand"` on Canvas | Only render when something changes (static scenes) |
| `invalidate()` from useThree | Trigger a render in demand mode |
| `<AdaptiveDpr pixelated />` + `<AdaptiveEvents />` (drei) | Drop resolution and raycasting while the camera moves, restore when idle |
| `<Bvh>` (drei) | Heavy scenes that need fast raycasting / hover picking |

**Target metrics:** < 100 draw calls, < 1M triangles, 60fps on mid-range GPU.
Use `stats-gl` or `r3f-perf` to monitor.

---

## Do Not

### 1. Never setState in useFrame

Causes full React re-render 60x/second. Mutate refs directly.

```tsx
// BAD
useFrame(() => {
  setRotation(prev => prev + 0.01) // React re-render every frame
})

// GOOD
useFrame((_, delta) => {
  meshRef.current.rotation.y += delta * 0.5 // Direct mutation, zero re-renders
})
```

### 2. Never allocate in the render loop

`new Vector3()` per frame = GC spikes = stutter.

```tsx
// BAD
useFrame((state) => {
  const target = new THREE.Vector3(0, Math.sin(state.clock.elapsedTime), 0)
  meshRef.current.position.copy(target)
})

// GOOD
const _target = useMemo(() => new THREE.Vector3(), [])
useFrame((state) => {
  _target.set(0, Math.sin(state.clock.elapsedTime), 0)
  meshRef.current.position.copy(_target)
})
```

### 3. Never forget dispose (memory leak)

Three.js textures, geometries, and materials live on the GPU. Unmounting a React component does NOT free them.

```tsx
// BAD -- texture stays in VRAM after unmount
const texture = useLoader(TextureLoader, '/big-texture.jpg')

// GOOD -- R3F auto-disposes when using JSX primitives
// For manual resources, dispose in cleanup:
useEffect(() => {
  return () => {
    texture.dispose()
    geometry.dispose()
    material.dispose()
  }
}, [])
```

### 4. Never re-render the Canvas parent

State changes in the parent force the entire Canvas to remount = flash, lost state, reloaded assets.

```tsx
// BAD
function App() {
  const [uiState, setUiState] = useState(false) // re-renders remount Canvas
  return (
    <>
      <button onClick={() => setUiState(!uiState)}>Toggle</button>
      <Canvas><Scene config={uiState} /></Canvas>
    </>
  )
}

// GOOD -- isolate Canvas in its own component
function App() {
  return (
    <>
      <UI />
      <SceneCanvas />
    </>
  )
}
```

### 5. Never load assets without Suspense

Loaders (useGLTF, useTexture, useLoader) throw promises. Without Suspense, you get crashes.

```tsx
// BAD
<Canvas>
  <Model /> {/* useGLTF inside -- will throw */}
</Canvas>

// GOOD
<Canvas>
  <Suspense fallback={<Loader />}>
    <Model />
  </Suspense>
</Canvas>
```

---

## Quick Reference: Loading Sub-resources

| Need | Load |
|---|---|
| Scene boilerplate, lighting rigs, controls | `references/scene-setup.md` |
| Custom shaders, GLSL patterns, uniforms | `references/shaders.md` |
| Animation principles, easing, timing | `../motion-principles/SKILL.md` |
| GSAP + Three.js integration | `../gsap/SKILL.md` |
