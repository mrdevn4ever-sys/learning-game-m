// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ChnobelDevelopment",
    platforms: [.iOS(.v18), .macOS(.v15)],
    products: [
        .library(name: "CoreDomain", targets: ["CoreDomain"]),
        .library(name: "ObservationLog", targets: ["ObservationLog"]),
        .library(name: "TaskEngine", targets: ["TaskEngine"]),
        .library(name: "LearningEngine", targets: ["LearningEngine"]),
        .library(name: "EvidenceKit", targets: ["EvidenceKit"]),
        .library(name: "InputKit", targets: ["InputKit"]),
        .library(name: "RecognitionKit", targets: ["RecognitionKit"])
    ],
    dependencies: [],
    targets: [
        .target(name: "CoreDomain"),
        .target(name: "ObservationLog", dependencies: ["CoreDomain"]),
        .target(name: "TaskEngine", dependencies: ["CoreDomain", "ObservationLog"]),
        .target(name: "LearningEngine", dependencies: ["CoreDomain", "ObservationLog", "TaskEngine"]),
        .target(name: "EvidenceKit", dependencies: ["CoreDomain", "ObservationLog", "LearningEngine"]),
        .target(name: "InputKit"),
        .target(name: "RecognitionKit", dependencies: ["InputKit"]),
        .testTarget(name: "CoreDomainTests", dependencies: ["CoreDomain"]),
        .testTarget(name: "ObservationLogTests", dependencies: ["ObservationLog", "CoreDomain"]),
        .testTarget(name: "TaskEngineTests", dependencies: ["TaskEngine", "CoreDomain", "ObservationLog"]),
        .testTarget(name: "LearningEngineTests", dependencies: ["LearningEngine", "TaskEngine", "ObservationLog", "CoreDomain"]),
        .testTarget(name: "EvidenceKitTests", dependencies: ["EvidenceKit", "TaskEngine", "ObservationLog", "CoreDomain"]),
        .testTarget(name: "InputKitTests", dependencies: ["InputKit"]),
        .testTarget(name: "RecognitionKitTests", dependencies: ["RecognitionKit", "InputKit"])
    ],
    swiftLanguageModes: [.v6]
)
