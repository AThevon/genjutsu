# GSAP Timeline

## Creation

```js
const tl = gsap.timeline({
  defaults: { duration: 0.8, ease: "power2.out" }, // applies to all children
  paused: false,
  repeat: -1,           // -1 = infinite
  yoyo: true,
  repeatDelay: 0.5,
  onComplete: () => console.log("done"),
});
```

## Position Parameter

The position parameter controls WHERE a tween is inserted in the timeline. It's the 3rd argument of `.to()`, `.from()`, `.fromTo()`, `.add()`.

### Absolute values

```js
tl.to(".a", { x: 100 }, 0);     // at exactly 0s (start of the timeline)
tl.to(".b", { x: 100 }, 1);     // at exactly 1s
tl.to(".c", { x: 100 }, 2.5);   // at exactly 2.5s
```

### Relative to the end of the timeline

```js
tl.to(".a", { x: 100 });              // appends to the end
tl.to(".b", { x: 100 }, "+=0.5");     // 0.5s AFTER the end
tl.to(".c", { x: 100 }, "-=0.3");     // 0.3s BEFORE the end (overlap)
```

### Relative to the previous tween

```js
tl.to(".a", { x: 100 });
tl.to(".b", { x: 100 }, "<");         // same start as the previous
tl.to(".c", { x: 100 }, "<0.2");      // 0.2s after the START of the previous
tl.to(".d", { x: 100 }, ">");         // at the END of the previous
tl.to(".e", { x: 100 }, ">-0.1");     // 0.1s BEFORE the end of the previous
```

### With labels

```js
tl.addLabel("intro", 1);
tl.to(".a", { x: 100 }, "intro");       // at the label
tl.to(".b", { x: 100 }, "intro+=0.3");  // 0.3s after the label
```

## Position cheatsheet

```
tl ─────────────────────────────────────>
   |  A  |      |  B  |
              |  C  |       |  D  |
                         |  E  |

A: tl.to(a, {}, 0)          // absolute
B: tl.to(b, {})             // sequential (end of A)
C: tl.to(c, {}, "<")        // start of B
D: tl.to(d, {}, "+=0.5")    // 0.5s after end of C
E: tl.to(e, {}, ">-0.2")    // 0.2s before end of D
```

## Labels

```js
tl.addLabel("reveal", "+=0.5");      // adds a label at the current position + 0.5s
tl.to(".box", { x: 200 }, "reveal"); // uses the label as position

tl.play("reveal");                   // plays from the label
tl.seek("reveal");                   // jumps to the label without playing
```

## .add() method

Adds tweens, callbacks, or labels.

```js
tl.add(gsap.to(".a", { x: 100 }), 1);           // tween at 1s
tl.add(() => console.log("checkpoint"), "+=0.5"); // callback
tl.add("myLabel");                                 // label shorthand
```

## Nesting (nested timelines)

Timelines can contain other timelines. Each sub-timeline acts as a single "block" in the parent.

```js
function heroAnimation() {
  const tl = gsap.timeline();
  tl.from(".hero-title", { y: 50, opacity: 0 })
    .from(".hero-subtitle", { y: 30, opacity: 0 }, "<0.2")
    .from(".hero-cta", { scale: 0.8, opacity: 0 }, "<0.1");
  return tl;
}

function cardsAnimation() {
  const tl = gsap.timeline();
  tl.from(".card", { y: 40, opacity: 0, stagger: 0.15 });
  return tl;
}

// Master timeline
const master = gsap.timeline();
master
  .add(heroAnimation())
  .add(cardsAnimation(), "-=0.3"); // 0.3s overlap
```

**Advantage**: each section is encapsulated, testable, and repositionable.

## defaults on Timeline

Defaults propagate to direct children but NOT to nested timelines.

```js
const tl = gsap.timeline({
  defaults: { duration: 1, ease: "power3.out" },
});

tl.to(".a", { x: 100 });           // duration: 1, ease: power3.out
tl.to(".b", { x: 100, duration: 2 }); // duration: 2 (override), ease: power3.out

// Child timeline: its own defaults apply
const child = gsap.timeline({ defaults: { duration: 0.5 } });
tl.add(child); // the parent's defaults do NOT apply to child's tweens
```

## Controlling the Timeline

```js
tl.play();
tl.pause();
tl.resume();
tl.reverse();
tl.restart();
tl.kill();

// Navigation
tl.seek(2);              // jumps to 2s
tl.seek("myLabel");      // jumps to the label
tl.progress(0.5);        // jumps to 50%
tl.time(1.5);            // jumps to 1.5s

// Speed
tl.timeScale(2);         // 2x faster
tl.timeScale(0.5);       // 2x slower

// State
tl.isActive();           // currently playing?
tl.totalDuration();      // total duration including repeats
tl.paused();             // paused?

// Modification
tl.clear();              // clears the timeline (keeps the instance)
tl.invalidate();         // resets the starting values
tl.totalProgress(0);     // resets to the start
```

## Common patterns

### Responsive timeline with matchMedia

```js
ScrollTrigger.matchMedia({
  "(min-width: 768px)": function () {
    // desktop animations
    gsap.timeline({ scrollTrigger: { trigger: ".section" } })
      .to(".box", { x: 500 });
  },
  "(max-width: 767px)": function () {
    // mobile animations (simpler)
    gsap.to(".box", { y: 100, scrollTrigger: ".section" });
  },
});
// Automatic cleanup when the media query no longer matches
```

### Timeline with ScrollTrigger

```js
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".section",
    start: "top center",
    end: "bottom center",
    scrub: 1,
    // DO NOT put ScrollTrigger on the timeline's children
  },
});

tl.to(".a", { x: 200 })
  .to(".b", { rotation: 360 }, "<")
  .to(".c", { scale: 2 }, "+=0.3");
```

### Clean kill in React

```jsx
import { useGSAP } from "@gsap/react";

function Component() {
  const container = useRef();

  useGSAP(() => {
    const tl = gsap.timeline();
    tl.to(".box", { x: 200 });
    // automatic cleanup by useGSAP
  }, { scope: container });

  return <div ref={container}>...</div>;
}
```
