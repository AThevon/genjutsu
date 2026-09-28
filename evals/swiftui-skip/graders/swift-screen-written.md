---
type: regex
target: { source: file, path: Sources/SteadyUI/TodayView.swift }
match: contains
pattern: '\b(VStack|HStack|ZStack|ScrollView|List|LazyVStack|Grid)\s*[({]'
---

Positive guard, scored in both arms: the scaffold's one-line view was replaced by a real screen.
