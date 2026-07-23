# GSAP Core API

## Tween Methods

### gsap.to(targets, vars)

Animates properties TO the specified values.

```js
gsap.to(".box", {
  x: 200,           // translateX
  y: -50,           // translateY
  rotation: 360,    // rotate in degrees
  scale: 1.5,
  opacity: 0.5,
  duration: 1,
  ease: "power2.out",
  delay: 0.3,
});
```

`targets`: CSS selector string, element, Array of elements, NodeList, or JS object.

### gsap.from(targets, vars)

Animates FROM the specified values to the current state.

```js
gsap.from(".box", { y: 100, opacity: 0, duration: 0.8 });
```

**Warning**: `immediateRender` is `true` by default on `from()`. The element jumps to the `from` values immediately. Set `immediateRender: false` if needed.

### gsap.fromTo(targets, fromVars, toVars)

Full control over both the start AND the end.

```js
gsap.fromTo(".box",
  { x: -100, opacity: 0 },          // from
  { x: 0, opacity: 1, duration: 1 } // to (options here)
);
```

### gsap.set(targets, vars)

Applies values immediately (duration: 0). Equivalent to `gsap.to(target, { ...vars, duration: 0 })`.

```js
gsap.set(".box", { x: 0, y: 0, opacity: 1, clearProps: "all" });
```

`clearProps: "all"` removes all inline styles applied by GSAP.

## Tween Options

| Option            | Type              | Default   | Description                                                 |
| ----------------- | ----------------- | --------- | ----------------------------------------------------------- |
| `duration`        | number            | `0.5`     | Duration in seconds                                         |
| `ease`            | string            | `"power1.out"` | Animation curve                                        |
| `delay`           | number            | `0`       | Delay before start                                          |
| `repeat`          | number            | `0`       | Number of repetitions (`-1` = infinite)                     |
| `yoyo`            | boolean           | `false`   | Alternates direction on each repeat                         |
| `repeatDelay`     | number            | `0`       | Delay between each repeat                                    |
| `stagger`         | number/object     | `0`       | Delay between each target                                    |
| `overwrite`       | boolean/string    | `false`   | `true` kills conflicting tweens, `"auto"` conflicting props |
| `immediateRender` | boolean           | auto      | `true` on from/fromTo, `false` on to                        |
| `paused`          | boolean           | `false`   | Creates the tween paused                                    |
| `reversed`        | boolean           | `false`   | Plays in reverse                                            |
| `onStart`         | function          | null      | Callback on start                                           |
| `onUpdate`        | function          | null      | Callback on each frame                                      |
| `onComplete`      | function          | null      | Callback on complete                                        |
| `onRepeat`        | function          | null      | Callback on each repeat                                     |
| `onReverseComplete` | function        | null      | Callback when reverse reaches the start                     |
| `callbackScope`   | object            | tween     | `this` scope of the callbacks                               |

## Easing

Format: `"type.direction"`, e.g. `"power2.out"`, `"elastic.inOut"`, `"back.in"`.

Common types:
- `none` (linear), `power1`-`power4`, `back`, `elastic`, `bounce`, `circ`, `expo`, `sine`
- `steps(n)` -> stepped animation
- `"slow(0.7, 0.7, false)"` -> slow-mo effect
- Custom: `CustomEase.create("myEase", "M0,0 C0.5,0 0.5,1 1,1")`

## Stagger

### Simple

```js
gsap.to(".item", { y: -20, stagger: 0.1 }); // 0.1s between each element
```

### Object config

```js
gsap.to(".item", {
  y: -20,
  stagger: {
    each: 0.1,           // time between each element
    // OR amount: 0.8,   // TOTAL time for the stagger (divided by N elements)
    from: "center",       // "start" | "end" | "center" | "edges" | "random" | number (index)
    grid: "auto",         // enables 2D distribution, detects the grid
    axis: "y",            // "x" | "y" | null (2D distance)
    ease: "power2.in",   // ease of the stagger distribution
  },
});
```

## Animatable CSS Properties

### Transforms (GPU -> prefer these)

| GSAP shorthand | CSS equivalent         |
| --------------- | ---------------------- |
| `x`             | `translateX`           |
| `y`             | `translateY`           |
| `z`             | `translateZ`           |
| `rotation`      | `rotate` (in degrees)  |
| `rotationX/Y`   | `rotateX/Y`           |
| `scale`         | `scale`                |
| `scaleX/Y`      | `scaleX/Y`            |
| `skewX/Y`       | `skewX/Y`              |
| `xPercent`      | `translateX(%)`        |
| `yPercent`      | `translateY(%)`        |
| `transformOrigin` | `transform-origin`   |

### Other properties

- `opacity`, `borderRadius`, `backgroundColor`, `color`, `boxShadow`
- CSS variables: `gsap.to(el, { "--my-var": 100 })`
- SVG: `attr: { cx: 200, r: 50 }` for SVG attributes

## Utilities

### gsap.defaults(vars)

Applies defaults to ALL tweens created after this call.

```js
gsap.defaults({ duration: 0.8, ease: "power2.out" });
```

### gsap.registerPlugin(...plugins)

Registers plugins. Call once, at the top level.

```js
import { ScrollTrigger, SplitText, Flip } from "gsap/all";
gsap.registerPlugin(ScrollTrigger, SplitText, Flip);
```

### gsap.quickTo(target, prop, vars)

Creates a reusable function to animate a property (ideal for mouse-follow).

```js
const xTo = gsap.quickTo(".cursor", "x", { duration: 0.3, ease: "power3" });
const yTo = gsap.quickTo(".cursor", "y", { duration: 0.3, ease: "power3" });

window.addEventListener("mousemove", (e) => {
  xTo(e.clientX);
  yTo(e.clientY);
});
```

### gsap.quickSetter(target, prop, unit)

Like quickTo but instant (no interpolation). Ultra performant for onUpdate.

```js
const setX = gsap.quickSetter(".el", "x", "px");
```

### gsap.utils

```js
gsap.utils.toArray(".items")        // NodeList -> Array
gsap.utils.clamp(0, 100, value)     // clamps the value
gsap.utils.mapRange(0, 1, 0, 100, 0.5) // map 0.5 -> 50
gsap.utils.wrap([1, 2, 3], 5)       // cycle: returns 3
gsap.utils.interpolate(0, 100, 0.5) // returns 50
gsap.utils.random(1, 10, 1)         // random between 1-10, step 1
gsap.utils.shuffle(array)           // shuffles the array
gsap.utils.distribute({ amount: 1, from: "center" }) // distribution function
```

### gsap.context()

Scope for easy cleanup (crucial in React/Vue). Replace with `useGSAP()` in React.

```js
const ctx = gsap.context(() => {
  gsap.to(".box", { x: 200 });
  ScrollTrigger.create({ ... });
}, containerRef); // scope selectors to the container

// Cleanup
ctx.revert(); // kills everything: tweens, ScrollTriggers, etc.
```

## Controlling a Tween

```js
const tween = gsap.to(".box", { x: 200, paused: true });

tween.play();
tween.pause();
tween.reverse();
tween.restart();
tween.kill();

tween.progress(0.5);    // jumps to 50%
tween.timeScale(2);     // 2x faster
tween.duration();        // getter
tween.duration(2);       // setter
```
