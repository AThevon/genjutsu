---
type: regex
target: { source: file, path: components/waitlist-button.tsx }
match: contains
pattern: '<(motion\.|m\.)?button\b[\s\S]*(whileHover|whileTap|whilePress|onPointer(Down|Up|Enter|Leave)|onMouse(Enter|Leave|Down|Up)|onTouch(Start|End)|\b(hover|active):[\w\[-]|:(hover|active)\b|useAnimate|useSpring)|(whileHover|whileTap|whilePress|onPointer(Down|Up|Enter|Leave)|onMouse(Enter|Leave|Down|Up)|onTouch(Start|End)|\b(hover|active):[\w\[-]|:(hover|active)\b|useAnimate|useSpring)[\s\S]*<(motion\.|m\.)?button\b'
---

Positive guard, scored in both arms: the button is still a button and now has a hover or press
state, in any of the forms the stack allows (Tailwind hover: and active: variants, :hover and
:active in CSS, Motion's whileHover and whileTap, pointer handlers). The scaffold's button has
none, so a run that wrote nothing fails this and is left out of the delta reading: the checks
below that pass on inaction never pass for free.
