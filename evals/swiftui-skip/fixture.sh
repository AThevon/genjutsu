#!/usr/bin/env bash
# Scaffold for the swiftui-skip eval case, run by `claude plugin eval --scaffold`
# in the run's empty workspace. A Swift package whose only view is a one-line
# placeholder, so the stack scan detects SwiftUI on iOS and a run that writes
# nothing fails the swift-screen-written guard.
set -euo pipefail

mkdir -p Sources/SteadyUI

cat > Package.swift <<'SWIFT'
// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "Steady",
    platforms: [.iOS(.v18)],
    products: [.library(name: "SteadyUI", targets: ["SteadyUI"])],
    targets: [.target(name: "SteadyUI", path: "Sources/SteadyUI")]
)
SWIFT

cat > Sources/SteadyUI/TodayView.swift <<'SWIFT'
import SwiftUI

public struct TodayView: View {
    public init() {}

    public var body: some View {
        Text("Today")
    }
}
SWIFT
